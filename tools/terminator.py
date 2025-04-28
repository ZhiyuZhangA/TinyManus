import weakref
from tools.base_tool import BaseTool
from typing import Optional, Dict
from pydantic import PrivateAttr

_TERMINATE_DESCRIPTION = (
    "Use this tool to formally terminate the current task execution. "
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
            "reason": {
                "type": "string",
                "description": "Optional detailed reason for why the task was terminated."
            }
        },
    }

    def execute(self, reason: Optional[str] = None):
        agent = self._agent_ref()
        if agent is None:
            raise RuntimeError("Agent reference lost.")
        agent.terminate(reason)
