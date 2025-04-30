from typing import List, Tuple

TEMPLATE = """You are a member of a multi-agent collaborative system.
Your current task is:
----
{task}
----
Here is the record of previously completed tasks:
----
{history}
----
Please complete your response based on the current task and context.
"""


class TaskPromptTemplate:
    def __init__(self, template: str):
        self.template = template

    def format(self, task_content: str, chat_history: List[Tuple[str, str]]) -> str:
        """
        chat_history: List of tuples like (agent_name, result_text)
        """
        history_str = "\n".join(
            f"[{name}] {text}" for name, text in chat_history
        )
        return self.template.format(
            task=task_content,
            history=history_str
        )

