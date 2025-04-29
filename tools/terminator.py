import weakref
from tools.base import BaseTool
from typing import Dict
from pydantic import PrivateAttr

_TERMINATE_DESCRIPTION = (
    "Use this tool to deliver the final answer to the user and formally terminates the reasoning process. "
    "You should only call this tool when you are confident that the objective has been achieved "
    "or no further action can meaningfully improve the outcome."
)


class Terminator(BaseTool):
    _agent_ref: weakref.ReferenceType = PrivateAttr()

    name: str = "Terminator"
    description: str = _TERMINATE_DESCRIPTION
    parameters: Dict = {
        "type": "object",
        "properties": {
            "answer": {
                "type": "string",
                "description": "Optional detailed reason for why the task was terminated."
            }
        },
        "required": ["answer"]
    }

    async def execute(self, answer: str):
        agent = self._agent_ref()
        if agent is None:
            raise RuntimeError("Agent reference lost.")
        agent.terminate(answer)
        return answer
