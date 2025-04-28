from abc import ABC
from base import BaseAgent
from llm import LLM


class OneShotAgent(BaseAgent, ABC):
    def __init__(self,
                 name: str,
                 description: str,
                 system_prompt: str,
                 enabled_memory: bool,
                 llm: LLM):
        super().__init__(name, description, system_prompt, enabled_memory, llm)

    async def run(self, request: str):
        # Implement the function calling with inference in one shot
        pass



