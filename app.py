"""Field Card: turns a few details about where you are into a one-page,
printable, screen-free outing. The words are written by an open-weight model
running on this laptop through Ollama, so it works with no internet."""
import json
import os
import threading
import webbrowser

import requests
from flask import Flask, jsonify, request, send_from_directory

BASE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

MODEL = "gemma3:4b"                # change to any model you have pulled with Ollama
OLLAMA = "http://localhost:11434"  # where Ollama listens on this laptop

# How many "find these" items fit the time you have (minutes -> items)
COUNTS = {15: 5, 30: 6, 60: 8, 120: 10}

# The exact shape we force the model to answer in (Ollama "structured output")
CARD_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "intro": {"type": "string"},
        "bring": {"type": "array", "items": {"type": "string"}},
        "notice": {"type": "array", "items": {"type": "string"}},
        "phone_rule": {"type": "string"},
        "on_the_way_back": {"type": "string"},
    },
    "required": ["title", "intro", "bring", "notice", "phone_rule", "on_the_way_back"],
}


def build_prompt(d, n):
    """The instructions that turn a general model into a field-card writer."""
    return f"""Write a one-page field card for a screen-free outing. The person will print it, put their phone away, and go.

Today: {d.get('today')}
Region: {d.get('region')}
Place: {d.get('place')}
Time available: {d.get('minutes')} minutes
Going with: {d.get('who')}
Note: {d.get('note') or 'none'}

Rules:
- Use the region and today's date to work out the season and what is likely happening outdoors. Never name specific streets, parks or businesses.
- "notice" has exactly {n} things to find, see, hear, smell or touch. Describe each by color, shape, sound or behavior (for example "something that rustles when the wind moves it"), never by species name, so no expert knowledge is needed. Each must be doable in this kind of place within the time.
- "bring" has 3 to 5 short items, including water if the outing is over 30 minutes.
- If kids or a dog are coming, make it playful and safe for them.
- "phone_rule" is one short, friendly rule for keeping the phone away.
- "on_the_way_back" is one question to think about while walking home.
- "title" is 2 to 5 words. "intro" is one sentence. Plain language, no emoji."""


@app.get("/")
def home():
    return send_from_directory(os.path.join(BASE, "static"), "index.html")


@app.get("/api/status")
def status():
    """Tells the page if Ollama is running and the model is downloaded."""
    try:
        tags = requests.get(f"{OLLAMA}/api/tags", timeout=3).json()
    except requests.exceptions.RequestException:
        return jsonify(model=MODEL, state="offline", message="Ollama isn't running. Open the Ollama app from the Start menu, then reload this page.")
    names = [m["name"] for m in tags.get("models", [])]
    wanted = MODEL if ":" in MODEL else MODEL + ":latest"
    if wanted not in names:
        return jsonify(model=MODEL, state="missing", message=f"Model not downloaded yet. In PowerShell run: ollama pull {MODEL}")
    return jsonify(model=MODEL, state="ready")


@app.post("/api/card")
def card():
    """Asks the local model for a card and sends it back as JSON."""
    d = request.get_json()
    n = COUNTS.get(d.get("minutes"), 6)
    try:
        r = requests.post(
            f"{OLLAMA}/api/chat",
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": build_prompt(d, n)}],
                "stream": False,
                "format": CARD_SCHEMA,
                "options": {"temperature": 0.8},
            },
            timeout=300,
        )
        r.raise_for_status()
        result = json.loads(r.json()["message"]["content"])
        result["notice"] = result["notice"][:n]
    except requests.exceptions.RequestException:
        return jsonify(error="Can't reach the model. Check that Ollama is running and the model is downloaded."), 502
    except (ValueError, KeyError):
        return jsonify(error="The model gave a muddled answer. Press Make my card to try again."), 502
    return jsonify(result)


if __name__ == "__main__":
    threading.Timer(1.2, lambda: webbrowser.open("http://localhost:5001")).start()
    app.run(port=5001)
