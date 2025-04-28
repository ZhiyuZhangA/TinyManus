from typing import Dict
from pydantic import BaseModel, ConfigDict


class BaseTool(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    description: str
    parameters: Dict

    def execute(self, **kwargs):
        raise NotImplementedError

    def to_dict(self) -> Dict:
        """Convert tool to OpenAI function-calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }
