from utils.logger import logger
from tools.base import BaseTool
from typing import Dict, Optional
from tools.cmd.shell_session import create_shell_session
from tools.cmd.shell_session import ShellSession
from pydantic import PrivateAttr
import platform

system = platform.system()

_SHELL_TOOL_DESCRIPTION = (
    f"""
    Executes a {system} powershell command in an interactive session
    Useful for tasks like listing files, running scripts, or checking system status. 
    Do not use destructive or unsafe commands (e.g., delete files, shutdown, or modify system configuration).
    """
)


class ShellTool(BaseTool):
    name: str = "shell_tool"
    description: str = _SHELL_TOOL_DESCRIPTION
    parameters: Dict = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to execute, such as 'dir', 'echo Hello', or 'python script.py'"
            }
        },
        "required": ["command"],
    }

    _session: Optional[ShellSession] = PrivateAttr()

    def __init__(self):
        super().__init__()
        self._session = create_shell_session()

    async def execute(self, command: str) -> dict:
        logger.info(f"💻 Starting new ShellSession with command: {command}")
        if self._session:
            self._session.stop()
        self._session = create_shell_session()
        await self._session.start()

        logger.info("✅ ShellSession started.")

        if command is not None:
            try:
                result = await self._session.run(command)
            except Exception as e:
                logger.error(f"⚠️ Shell execution failed: {e}")
                return {"output": "", "error": str(e), "system": "Shell execution failed"}
            finally:
                self._session.stop()
                await self._session.wait_until_closed()

            output = result.get("output", "")
            # error = result.get("error", "")
            # logger.info(f"📤 Output: {output}, ❌ Error: {error}")
            logger.info(f"📤 Output: {output}")
            return result

        raise RuntimeError("No command is provided!")
        