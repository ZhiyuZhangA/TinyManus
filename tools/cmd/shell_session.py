from abc import ABC, abstractmethod
import asyncio
import platform

class ShellSession(ABC):
    _process: asyncio.subprocess.Process

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    async def run(self, command: str) -> dict:
        """ Run the given command """
        pass

    async def wait_until_closed(self):
        if self._process:
            await self._process.wait()


class PowershellSession(ShellSession):
    _started: bool

    command: str = "powershell.exe"
    _output_delay: float = 0.2
    _timeout: float = 120.0
    _sentinel: str = "<<exit>>"

    def __init__(self):
        self._started = False
        self._timed_out = False

    async def start(self):
        if self._started:
            return

        self._process = await asyncio.create_subprocess_exec(
            self.command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        self._started = True

    def stop(self):
        if not self._started:
            return

        if self._process.returncode is not None:
            return

        if self._process.stdin:
            self._process.stdin.close()

        self._process.terminate()

    async def run(self, command: str) -> dict:
        if not self._started:
            raise RuntimeError("Session not started.")

        # Check whether subprocess has ended
        if self._process.returncode is not None:
            return {"system": "shell exited", "error": f"exit code {self._process.returncode}"}

        assert self._process.stdin
        assert self._process.stdout

        self._process.stdin.write(
            command.encode() + f"\nWrite-Output '{self._sentinel}'\n".encode()
        )

        await self._process.stdin.drain()

        output = ""
        try:
            async with asyncio.timeout(self._timeout):
                while True:
                    line = await self._process.stdout.readline()
                    decoded = line.decode("gbk", errors="ignore")
                    if self._sentinel in decoded:
                        break
                    output += decoded

        except asyncio.TimeoutError:
            self._timed_out = True
            raise RuntimeError("Powershell command timed out!")

        # try:
        #     error_bytes = await asyncio.wait_for(self._process.stderr.read(), timeout=1)
        #     error = error_bytes.decode("utf-8", errors="ignore").strip()
        # except asyncio.TimeoutError:
        #     error = "[stderr empty or not flushed]"

        return {"output": output.strip()}


def create_shell_session() -> ShellSession:
    system = platform.system()
    if system == "Windows":
        return PowershellSession()
    else:
        raise RuntimeError(f"Unsupported system: {system}")
