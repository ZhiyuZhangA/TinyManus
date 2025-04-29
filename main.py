from llm import LLM
import os
import asyncio
import base64
from agent.react import ReActAgent
from prompt.react_prompt import SYSTEM_PROMPT
from tools.google_search import GoogleSearchTool
from dotenv import load_dotenv
from tools.cmd.shell_tool import ShellTool


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
google_search_key = os.getenv("GOOGLE_SEARCH_API_KEY")
google_engine_id = os.getenv("GOOGLE_ENGINE_ID")


def image_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


async def main():
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

    await react.run("Please create a txt document on my laptop's desktop where it describes the first computer in the world.")

if __name__ == "__main__":
    asyncio.run(main())