from typing import List, Dict, Optional
from tools.base_tool import BaseTool


class ToolCollection:
    def __init__(self, tools: Optional[List[BaseTool]]):
        self.tools = tools or []

    def add_tool(self, tool: BaseTool):
        self.tools.append(tool)

    def to_dict(self) -> List[Dict]:
        return [tool.to_dict() for tool in self.tools]

    def get_tool(self, name: str) -> Optional[BaseTool]:
        for tool in self.tools:
            if tool.name == name:
                return tool

        return None

    def to_list(self):
        return self.tools
