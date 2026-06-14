"""
LLM-as-judge evaluation for RAG responses.

Faithfulness  — is every claim in the answer supported by the retrieved context?
Answer Relevance — does the answer directly address the user's question?

Both are scored 0.0–1.0 by Gemini in a single call to keep latency low.
"""

import json
import re
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
_client = genai.Client(api_key=os.getenv("gemini_token"))

_EVAL_PROMPT = """You are an expert evaluator for RAG (Retrieval-Augmented Generation) systems.
Evaluate the response below on two dimensions and return ONLY a valid JSON object — no extra text.

Query: {query}

Retrieved Context:
{context}

Response: {response}

Score each dimension from 0.0 to 1.0:

- faithfulness: Are all claims in the response directly supported by the context?
  1.0 = every statement is grounded in the context
  0.5 = some statements are supported, others are not
  0.0 = the response contradicts or ignores the context entirely

- answer_relevance: Does the response directly and completely address the query?
  1.0 = fully answers what was asked
  0.5 = partially answers the query
  0.0 = does not address the query at all

Return exactly this JSON format:
{{"faithfulness": <float>, "answer_relevance": <float>}}"""


def evaluate(query: str, context: str, response: str) -> dict[str, float]:
    prompt = _EVAL_PROMPT.format(query=query, context=context, response=response)
    raw = _client.models.generate_content(model="gemini-2.5-flash", contents=prompt).text.strip()

    # Strip markdown code fences if Gemini wraps the JSON
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()

    try:
        scores = json.loads(raw)
        return {
            "faithfulness": round(float(scores.get("faithfulness", 0)), 3),
            "answer_relevance": round(float(scores.get("answer_relevance", 0)), 3),
        }
    except (json.JSONDecodeError, ValueError):
        return {"faithfulness": 0.0, "answer_relevance": 0.0}
