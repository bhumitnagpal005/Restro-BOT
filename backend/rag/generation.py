import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
_client = genai.Client(api_key=os.getenv("gemini_token"))

_SYSTEM_PROMPT = (
    "You are a helpful assistant knowledgeable about restaurants in Roorkee, India. "
    "Answer queries about menus, prices, dietary options, and restaurant details using the provided context. "
    "Be clear, concise, and directly address the question. "
    "Apply proper capitalisation and grammar without altering the information itself. "
    "If you cannot answer from the context or history, say \"I don't know\" or \"I'm not sure\". "
    "Do not add unnecessary line breaks within your response."
)


def generate_response(context: str, query: str, history_string: str) -> str:
    prompt = f"""{_SYSTEM_PROMPT}

Context:
{context}

Conversation History:
{history_string}

Question: {query}
Answer:"""
    response = _client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text.strip()
