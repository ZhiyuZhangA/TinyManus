from llm import LLM
import os
import asyncio
import base64
from agent.react import ReActAgent
from prompt.react_prompt import SYSTEM_PROMPT
from tools.google_search import GoogleSearchTool
from dotenv import load_dotenv
from tools.cmd.shell_tool import ShellTool
from workflow.session import Session
from prompt.template import TEMPLATE
from prompt.template import TaskPromptTemplate
from workflow.session import Task

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
google_search_key = os.getenv("GOOGLE_SEARCH_API_KEY")
google_engine_id = os.getenv("GOOGLE_ENGINE_ID")


def image_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


async def agent_():
    llm = LLM(model="gpt-4o",
              api_key=api_key)

    searchTool = GoogleSearchTool()
    searchTool.set_api_key(google_search_key, google_engine_id)
    shell_tool = ShellTool()

    react = ReActAgent("Manus",
                       "A helpful agent",
                       SYSTEM_PROMPT,
                       15,
                       llm,
                       [searchTool, shell_tool])

    result = await react.run(
        "Please create a txt document on my laptop's desktop where it describes the first computer in the world.")


async def main():
    llm = LLM(model="gpt-4o",
              api_key=api_key)

    searchTool = GoogleSearchTool()
    searchTool.set_api_key(google_search_key, google_engine_id)
    shell_tool = ShellTool()

    agent1 = ReActAgent("Searcher1",
                        "A helpful agent",
                        SYSTEM_PROMPT,
                        15,
                        llm,
                        [searchTool, shell_tool])

    agent2 = ReActAgent("Searcher2",
                        "A helpful agent",
                        SYSTEM_PROMPT,
                        15,
                        llm,
                        [searchTool, shell_tool])

    agent3 = ReActAgent("Operator1",
                        "A helpful agent",
                        SYSTEM_PROMPT,
                        15,
                        llm,
                        [searchTool, shell_tool])

    agent4 = ReActAgent("Operator2",
                        "A helpful agent",
                        SYSTEM_PROMPT,
                        15,
                        llm,
                        [searchTool, shell_tool])

    template = TaskPromptTemplate(TEMPLATE)

    session = Session("Demo", template)

    task1 = Task("Brief introduction to the first computer in the world", agent1)
    task2 = Task("Brief introduction to the first quantum computer in the world", agent2)
    task3 = Task("Create a txt document file on my desktop where it stores info about the first computer and first quantum computer", agent3)
    task4 = Task("Check whether the txt is created on my desktop", agent4)

    session.set_task_flow([
        [task1, task2],
        [task3],
        [task4]
    ])

    await session.run()

    for line in session.get_chat():
        print(line)

if __name__ == "__main__":
    asyncio.run(main())
