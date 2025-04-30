from typing import Optional
from agent.base import BaseAgent
import uuid


class Task:
    def __init__(self, content: str, assignee: BaseAgent, task_id: str = None):
        self.task_id = task_id or str(uuid.uuid4())
        self.content = content
        self.assignee = assignee
        self.result: Optional[str] = None
        self.status = "pending"

    async def execute(self, request: str) -> str:
        self.status = "running"
        self.result = await self.assignee.run(request)
        self.status = "completed"
        return self.result

    def get_agent_name(self):
        return self.assignee.name
