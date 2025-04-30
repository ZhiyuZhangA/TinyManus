from typing import List, Tuple
from workflow.task import Task
from prompt.template import TaskPromptTemplate
from utils.logger import logger
import asyncio


class Session:
    def __init__(self, name: str, prompt_template: TaskPromptTemplate):
        self.name = name
        self.task_groups: List[List[Task]] = []
        self.history: List[Tuple[str, str]] = []
        self.prompt_template = prompt_template

    def set_task_flow(self, task_groups: List[List[Task]]):
        self.task_groups = task_groups

    def get_formatted_request(self, task: Task) -> str:
        return self.prompt_template.format(task.content, self.history)

    async def run(self):
        logger.info(f"🚀 [Session: {self.name}] Starting session with {len(self.task_groups)} task group(s).")

        for group_idx, group in enumerate(self.task_groups):
            logger.info(f"🌀 [Group {group_idx + 1}] Launching {len(group)} task(s) in parallel:")

            for task in group:
                logger.info(f"   🟡 Launching task for {task.get_agent_name()} → '{task.content}'")

            # 👇 真正并发执行
            results = await asyncio.gather(*[
                self._run_single_task(task) for task in group
            ])

            for agent_name, result in results:
                logger.info(f"✅ [{agent_name}] Task completed.")
                self.history.append((agent_name, result))

        logger.info(f"🎉 [Session: {self.name}] All task groups completed successfully.")

    async def _run_single_task(self, task: Task) -> Tuple[str, str]:
        request = self.get_formatted_request(task)
        result = await task.execute(request)
        return task.get_agent_name(), result

    def get_chat(self) -> List[str]:
        return [f"[{name}] {msg}" for name, msg in self.history]
