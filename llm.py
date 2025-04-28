from openai import AsyncOpenAI, OpenAIError
from openai.types.chat import ChatCompletionMessage
from typing import List, Optional, Dict, AsyncGenerator, Union
import tiktoken
import base64


def image_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


class LLM:
    multi_modal_models = {
        "gpt-4-vision-preview",
        "gpt-4o",
        "gpt-4o-mini",
    }

    model_token_limit = {
        "gpt-3.5-turbo": 4096,
        "gpt-3.5-turbo-16k": 16384,
        "gpt-4": 8192,
        "gpt-4-32k": 32768,
        "gpt-4o": 128000,
    }

    def __init__(self, model: str, api_key: str, base_url: str = None, max_tokens: int = 1024):
        self.model = model
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.max_input_tokens = self.model_token_limit.get(model)
        self.support_images = model in self.multi_modal_models
        self.base_url = base_url
        if base_url is None:
            self.base_url = 'https://api.openai.com/v1'  # Use OpenAI as provider in default
        self.client = AsyncOpenAI(api_key=self.api_key)

        # Choose tokenizer encoder for the given model name
        try:
            self.tokenizer = tiktoken.encoding_for_model(model)
        except KeyError:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

        self.input_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0

    def format_messages(self, messages: List[Dict]) -> List[Dict]:
        """
        Format the input messages to conform with the OpenAI API.
        :param messages: The list of messages to be sent to the model
        :return:
        """
        formatted_messages = []
        for msg in messages:
            # Validate the structure of the messages
            if not isinstance(msg, dict):
                raise ValueError(f"Each message must be a dict, got {type(msg)}")
            if "role" not in msg or "content" not in msg:
                raise ValueError(f"Each message must have 'role' and 'content' fields: {msg}")

            msg = dict(msg)
            # If the model supports images and this message contains a base64 image,
            # format the content to include a text + image_url multimodal message.
            if self.support_images and msg.get("base64_image"):
                content = msg.get("content")
                if not content:
                    content = []
                elif isinstance(content, str):
                    content = [{"type": "text", "text": content}]
                elif isinstance(content, list):
                    content = [
                        {"type": "text", "text": x} if isinstance(x, str) else x for x in content
                    ]
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{msg['base64_image']}"}
                })
                msg["content"] = content
                del msg["base64_image"]
            # If the model doesn't support images, remove the base64_image field to avoid invalid API input.
            elif not self.support_images and msg.get("base64_image"):
                del msg["base64_image"]
            formatted_messages.append(msg)
        return formatted_messages

    def count_text(self, text: str) -> int:
        return len(self.tokenizer.encode(text))

    def count_messages_tokens(self, messages: List[Dict]) -> int:
        """
        Count the number of tokens in the input messages.
        https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
        :param messages: The list of messages to be sent to the model
        :return: number of tokens in the input messages
        """

        tokens_per_message = 3
        tokens_per_name = 1
        num_tokens = 0
        for msg in messages:
            num_tokens += tokens_per_message
            for key, value in msg.items():
                if key == "name":
                    # Count extra token if name is present
                    num_tokens += tokens_per_name
                if isinstance(value, str):
                    num_tokens += self.count_text(value)
                elif isinstance(value, list):
                    # Count tokens for multimodal content or structured data like content or tool_calls
                    for item in value:
                        if isinstance(item, str):
                            for v in item.values():
                                if isinstance(v, str):
                                    num_tokens += self.count_text(v)
        num_tokens += 3
        return num_tokens

    def update_usage(self, usage):
        self.input_tokens += usage.prompt_tokens
        self.completion_tokens += usage.completion_tokens
        self.total_tokens += usage.total_tokens

    async def ask(self, messages: List[Dict], temperature: float, stream: bool = False) -> Union[str, AsyncGenerator[str, None]]:
        try:
            # Format the message
            formatted_messages = self.format_messages(messages)
            # Get the input token
            input_tokens = self.count_messages_tokens(messages)
            # Check whether the input tokens exceed the maximum token required
            if self.max_input_tokens is not None and input_tokens + self.max_tokens > self.max_input_tokens:
                raise ValueError(
                    f"Token limit exceeded: {input_tokens} input + {self.max_tokens} max completion > {self.max_input_tokens}")

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                max_tokens=self.max_tokens,
                temperature=temperature,
                stream=stream,
            )

            if stream:
                # Currently the system will not count the stream token, but it will be supported later
                self.input_tokens += input_tokens
                self.total_tokens += input_tokens

                async def stream_generator():
                    async for chunk in response:
                        content = chunk.choices[0].delta.content
                        if content:
                            yield content

                return stream_generator()
            else:
                self.update_usage(response.usage)
                return response.choices[0].message.content
        except OpenAIError as e:
            raise RuntimeError(f"OpenAI API Error: {e}")

    async def ask_tools(self, messages: List[Dict], temperature: float, tools: List[Dict],
                        tool_choice: Union[str, dict] = "auto") -> ChatCompletionMessage:
        try:
            # Format the message
            formatted_messages = self.format_messages(messages)
            # Get the input token
            input_tokens = self.count_messages_tokens(messages)
            # Check whether the input tokens exceed the maximum token required
            if self.max_input_tokens is not None and input_tokens + self.max_tokens > self.max_input_tokens:
                raise ValueError(
                    f"Token limit exceeded: {input_tokens} input + {self.max_tokens} max completion > {self.max_input_tokens}")

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                max_tokens=self.max_tokens,
                temperature=temperature,
                stream=False
            )
            self.update_usage(response.usage)
            return response.choices[0].message
        except OpenAIError as e:
            raise RuntimeError(f"OpenAI Tool API Error: {e}")

    def get_usage_summary(self) -> Dict:
        return {
            "prompt_tokens": self.input_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens
        }
