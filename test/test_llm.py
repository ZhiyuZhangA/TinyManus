from unittest.mock import AsyncMock, patch
from llm import LLM
import pytest
import os
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

@pytest.fixture
def llm():
    return LLM(
        model="gpt-4o",
        api_key=api_key
    )


def test_format_messages_text_only(llm):
    messages = [{"role": "user", "content": "Hello!"}]
    formatted = llm.format_messages(messages)
    assert formatted == messages


def test_format_messages_with_image(llm):
    llm.supports_images = True  # 手动开启图像支持
    messages = [{
        "role": "user",
        "content": "Here's an image",
        "base64_image": "fakebase64data"
    }]
    formatted = llm.format_messages(messages)
    assert isinstance(formatted[0]["content"], list)
    assert any(part["type"] == "image_url" for part in formatted[0]["content"])


def test_count_tokens_basic(llm):
    messages = [{"role": "user", "content": "hello world"}]
    tokens = llm.count_messages_tokens(messages)
    assert isinstance(tokens, int)
    assert tokens > 0


@pytest.mark.asyncio
async def test_ask_mocked_response(llm):
    # mock client.chat.completions.create
    mock_response = AsyncMock()
    mock_response.choices = [AsyncMock(message=AsyncMock(content="Hi!"))]
    mock_response.usage = {
        "prompt_tokens": 3,
        "completion_tokens": 2,
        "total_tokens": 5
    }

    with patch.object(llm.client.chat.completions, "create", return_value=mock_response):
        reply = await llm.ask([{"role": "user", "content": "Hello!"}], stream=False)
        assert isinstance(reply, str)
        assert reply == "Hi!"
