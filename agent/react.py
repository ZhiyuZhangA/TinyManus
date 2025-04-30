from agent.base import BaseAgent
from agent.base import AgentState
from llm import LLM
from typing import List, Optional
from memory.memory import Message
from tools.tool_collection import ToolCollection
from tools.base import BaseTool
from tools.terminator import Terminator
from logger import logger
import json
import weakref


# TODO: 记录每个task所对应的message,如果validator表示不行，那么我可以将这部分的message删掉，从而节省空间
class ReActAgent(BaseAgent):
    def get_final_result(self) -> str:
        pass

    def __init__(self,
                 name: str,
                 description: str,
                 system_prompt: str,
                 max_iters: int,
                 llm: LLM,
                 tools: Optional[List[BaseTool]] = None,
                 tool_choice="auto"):
        super().__init__(name, description, system_prompt, True, True, max_iters, llm)

        self.tool_collection = ToolCollection(tools)
        self.tool_calls = []
        self.tool_choice = tool_choice

        # Add terminator to the tool collection
        terminator = Terminator()
        terminator._agent_ref = weakref.ref(self)
        self.tool_collection.add_tool(terminator)

    async def step(self) -> str:
        # Terminating Condition: The agent will execute a tool called terminating task to modify its state
        should_act = await self.think()
        if should_act:
            return await self.act()
        else:
            return ""

    async def think(self) -> bool:
        """
        Process the current state and plan the actions to do next
        """

        try:
            response = await self.llm.ask_tools(self.messages, 0.2, self.tool_collection.to_dict(), self.tool_choice)
        except Exception as e:
            logger.error(f"🚨 LLM think() failed: {str(e)}")
            raise

        if response is None:
            logger.error("🚨 LLM returned None during think()")
            return False

        self.tool_calls = response.tool_calls or []
        thought = response.content

        # Log the thought
        logger.info(f"🧠 {self.name}'s Thought: {thought}")

        # Add the tool call message to the history
        if self.tool_calls:
            logger.info(f"🛠️  Tool Calls Proposed: {[call.function.name for call in self.tool_calls]}")
            self.memory.append(Message.tool_response(thought, self.tool_calls))
        else:
            self.add_memory("assistant", thought, self.tool_calls)

        return bool(self.tool_calls)

    async def act(self) -> str:
        """
        Action in react process with function calling
        """

        if not self.tool_calls:
            logger.warning(f"⚠️ No tool calls to execute for {self.name}. Skipping act().")

        for tool_call in self.tool_calls:
            tool_name = tool_call.function.name
            arguments = tool_call.function.arguments

            tool = self.tool_collection.get_tool(tool_name)
            if tool is None:
                logger.error(f"🚨 Tool '{tool_name}' not found for {self.name}. Skipping this tool call.")
                continue

            # Execute the tool
            try:
                parsed_args = json.loads(arguments) if isinstance(arguments, str) else arguments

                # Execute the tool
                result = await tool.execute(**parsed_args)

                # Construct tool message
                tool_msg = Message.from_tool_result(tool_call, result)

                # Add to memory
                self.memory.append(tool_msg)

                logger.info(f"✅ Executed tool '{tool_name}' for {self.name}, result: {result}")

                return result

            except Exception as e:
                logger.error(f"🚨 Error executing tool '{tool_name}' for {self.name}: {str(e)}")
                continue

    def terminate(self) -> None:
        """
        terminate the agent by setting its state to SUCCEED.
        Deliver a final answer.
        """
        self.state = AgentState.SUCCEED

        termination_msg = f"✅ Agent '{self.name}' has successfully terminated."

        logger.info(termination_msg)

        if self.enabled_memory:
            self.memory.append(
                Message.system(content=termination_msg)
            )
