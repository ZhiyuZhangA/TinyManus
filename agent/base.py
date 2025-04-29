from memory.memory import WorkingMemory
from memory.memory import Message
from typing import Optional, List, Union
from abc import ABC, abstractmethod
from enum import Enum
from llm import LLM
from utils.logger import logger


class AgentState(Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    SUCCEED = "SUCCEED"
    FAILED = "FAILED"
    TERMINATED = "TERMINATED"


class BaseAgent(ABC):
    def __init__(self,
                 name: str,
                 description: str,
                 system_prompt: str,
                 enabled_memory: bool,
                 allow_retry: bool,
                 max_iters: int,
                 llm: LLM):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        # Construct Memory
        self.enabled_memory = enabled_memory
        self.allow_retry = allow_retry
        self.max_iters = max_iters
        self.memory = WorkingMemory()
        self.memory.append(Message.system(system_prompt))

        self.llm = llm
        self.state = AgentState.IDLE

    def add_memory(self, role: str, content: Optional[str] = None, base64_image: Optional[str] = None,
                   tool_calls: Optional[List[str]] = None):
        message = None
        if role == "user":
            message = Message.user(content, base64_image)
        elif role == "assistant":
            message = Message.assistant(content, tool_calls=tool_calls)

        self.memory.append(message)

    async def run(self, request: str):
        self.state = AgentState.RUNNING
        attempt = 0

        if request:
            self.add_memory("user", request)
        else:
            logger.info(f"No existing prompt added for ")

        while attempt <= self.max_iters and self.state != AgentState.SUCCEED:
            try:
                logger.info(f"Executing step [{attempt + 1} / {self.max_iters}]...")
                await self.step()

                if self.state == AgentState.SUCCEED:
                    logger.info(f"[{self.name}] Step succeeded on attempt {attempt + 1}")
                    return self.get_final_result()

                elif self.state == AgentState.RUNNING:
                    logger.info(f"[{self.name}] Step still running on attempt [{attempt + 1}]")

                elif self.state == AgentState.FAILED:
                    logger.warning(f"[{self.name}] Step {attempt + 1} failed, retrying...")

            except Exception as e:
                logger.error(f"[{self.name}] Exception on step {attempt + 1}: {e}")

            attempt += 1

            if not self.allow_retry:
                break

        self.state = AgentState.FAILED
        logger.error(f"[{self.name}] Agent failed after {self.max_iters} retries.")
        raise RuntimeError(f"[{self.name}] Agent failed after {self.max_iters} retries.")

    @abstractmethod
    async def step(self):
        pass

    @abstractmethod
    def get_final_result(self) -> str:
        pass


    @property
    def messages(self) -> list[dict]:
        return self.memory.messages

