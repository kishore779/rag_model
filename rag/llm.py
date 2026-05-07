"""
LLM integration with Anthropic Claude API.
"""
import os
from anthropic import Anthropic

client = Anthropic()


def query_claude(system_prompt, user_prompt, temperature=0.7, max_tokens=1024):
    """
    Query Claude API with the given prompts.
    Returns the response text.
    """
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )
        return message.content[0].text
    except Exception as e:
        raise Exception(f"Error calling Claude API: {str(e)}")
