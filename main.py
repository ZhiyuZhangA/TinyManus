from llm import LLM
import os
import asyncio
import json
import base64
from agent.react import ReActAgent
from prompt.react_prompt import SYSTEM_PROMPT
from tools.google_search import GoogleSearchTool
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
google_key = os.getenv("GOOGLE_API_KEY")


def image_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


async def main():
    llm = LLM(model="gpt-4o",
              api_key=api_key)

    searchTool = GoogleSearchTool()
    searchTool.set_api_key(google_key)

    react = ReActAgent("Manus",
                       "A helpful agent",
                       SYSTEM_PROMPT,
                       10,
                       llm,
                       [searchTool])

    await react.run("Please Tell Me what is the name of the first computer in the world using google search")

if __name__ == "__main__":
    asyncio.run(main())