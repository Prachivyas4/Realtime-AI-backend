import os
import json
from openai import AsyncOpenAI
from .tasks import get_current_time

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define tool for function calling
LLM_FUNCTIONS = [
    {
        "name": "get_current_time",
        "description": "Get the current time in a given timezone",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {"type": "string", "description": "Timezone, e.g., UTC, Europe/London"},
            },
            "required": ["timezone"],
        },
    }
]


async def stream_chat_completion(messages):
    """
    Streams responses from OpenAI LLM, handles function calling.
    Yields tokens one by one for realtime streaming.
    """
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True,
        functions=LLM_FUNCTIONS
    )

    async for chunk in response:
        delta = chunk.choices[0].delta # ChoiceDelta object

        # Stream text content
        if hasattr(delta, "content") and delta.content:
            yield delta.content

        # Handle function calls
        if hasattr(delta, "function_call") and delta.function_call:
            function_call = delta.function_call
            if function_call.name == "get_current_time":
                args_str = getattr(function_call, "arguments", {})
                try:
                    args =json.loads(args_str)
                except json.JSONDecodeError:
                    args={}
                tz=args.get("timezone","UTC")
                result = await get_current_time(tz)
                # Append function result to conversation
                messages.append({"role": "function", "name": "get_current_time", "content": result})
                yield f"\n{result}\n"

