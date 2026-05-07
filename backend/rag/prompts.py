"""
Prompt templates for the RAG pipeline.
"""

SYSTEM_PROMPT = """You are an internal company policy assistant.
Answer ONLY using the provided context below.
If the answer is not in the context, say:
"I don't have that information in the company documents."
Never make up information."""

RAG_PROMPT_TEMPLATE = """Context:
{context}

Question:
{question}"""


def format_rag_prompt(context, question):
    """
    Format the RAG prompt with context and question.
    """
    return RAG_PROMPT_TEMPLATE.format(context=context, question=question)


def get_system_prompt():
    """
    Return the system prompt for the assistant.
    """
    return SYSTEM_PROMPT
