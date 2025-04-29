from typing import Optional, List, Union, Any
import json


class Message(dict):
    @classmethod
    def system(cls, content: str) -> "Message":
        return cls(role="system", content=content)

    @classmethod
    def user(cls, content: str, base64_image: Optional[str] = None) -> "Message":
        msg = cls(role="user", content=content)
        if base64_image:
            msg["base64_image"] = base64_image
        return msg

    @classmethod
    def assistant(cls, content: Optional[str] = None, tool_calls: Optional[List[Any]] = None) -> "Message":
        msg = cls(role="assistant")
        msg["content"] = content if content else ""
        if tool_calls:
            msg["tool_calls"] = tool_calls
        return msg

    @classmethod
    def tool_response(cls, content: Optional[str] = None, tool_calls: Optional[List[Any]] = None) -> "Message":
        """ Create a tool call message """
        formatted_tool_calls = [
            {"id": tool_call.id, "function": tool_call.function.model_dump(), "type": "function"} for tool_call in tool_calls
        ]

        return cls(
            role="assistant",
            content=content,
            tool_calls=formatted_tool_calls
        )

    @classmethod
    def from_tool_result(cls, tool_call, result: Union[str, dict]) -> "Message":
        """ Create a tool execution result message """
        return cls(
            role="tool",
            tool_call_id=tool_call.id,
            name=tool_call.function.name,
            content=result if isinstance(result, str) else json.dumps(result)
        )


class WorkingMemory:
    def __init__(self):
        self.messages: List[dict] = []

    def append(self, message: Union[Message, dict]) -> None:
        self.messages.append(dict(message))

    def get(self) -> List[dict]:
        return self.messages

    def clear(self):
        self.messages.clear()

    def truncate_recent(self, n: int = 1):
        if n >= len(self.messages):
            self.messages.clear()
        else:
            self.messages = self.messages[:-n]
