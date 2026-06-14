import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, request
from flask_cors import CORS

from rag.pipeline import chat, clear_session, evaluate_exchange, get_retriever, get_session_history

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175"])


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/chat", methods=["POST"])
def chat_endpoint():
    data = request.get_json(silent=True) or {}
    query: str = data.get("query", "").strip()
    session_id: str = data.get("session_id", "").strip()

    if not query:
        return jsonify({"error": "query cannot be empty"}), 400
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    result = chat(query, session_id)
    history = [{"query": q, "response": r} for q, r in get_session_history(session_id)]
    return jsonify({
        "response": result["response"],
        "exchange_id": result["exchange_id"],
        "metrics": result["metrics"],
        "history": history,
    })


@app.route("/api/evaluate", methods=["POST"])
def evaluate_endpoint():
    data = request.get_json(silent=True) or {}
    exchange_id: str = data.get("exchange_id", "").strip()

    if not exchange_id:
        return jsonify({"error": "exchange_id is required"}), 400

    scores = evaluate_exchange(exchange_id)
    if scores is None:
        return jsonify({"error": "exchange not found or expired"}), 404

    return jsonify(scores)


@app.route("/api/session/<session_id>", methods=["DELETE"])
def clear_history(session_id: str):
    clear_session(session_id)
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    get_retriever()  # pre-warm index at startup
    app.run(host="0.0.0.0", port=5001, debug=False)
