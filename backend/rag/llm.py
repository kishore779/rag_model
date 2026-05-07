"""
LLM integration with Groq API (free tier).
"""
import os
from groq import Groq


def query_claude(system_prompt, user_prompt, temperature=0.7, max_tokens=1024):
    """
    Query Groq API with the given prompts.
    Returns the response text.
    """
    try:
        # Initialize client with Groq API key
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        message = client.chat.completions.create(
            model="mixtral-8x7b-32768",  # Free tier model
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
        return message.choices[0].message.content
    except Exception as e:
        raise Exception(f"Error calling Groq API: {str(e)}")
