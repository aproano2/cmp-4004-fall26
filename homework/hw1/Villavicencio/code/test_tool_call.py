import urllib.request
import json

system = """You are a tool-calling assistant.
Your ONLY response must be valid JSON.
Do not explain.
Do not solve the puzzle.
Return exactly this structure:
{"tool":"astar_solve","arguments":{"state":[0,1,3,4,2,6,7,5,8]}}
"""

body = json.dumps({
    "model": "qwen2.5:3b",
    "stream": False,
    "messages": [
        {"role": "system", "content": system},
        {"role": "user", "content": "Call the astar_solve tool for the current puzzle."}
    ],
    "options": {
        "temperature": 0.0,
        "num_predict": 100
    }
}).encode()

req = urllib.request.Request(
    "http://localhost:11434/api/chat",
    data=body,
    headers={"Content-Type": "application/json"}
)

print("LLAMANDO...")

with urllib.request.urlopen(req, timeout=120) as r:
    d = json.loads(r.read())

print("RESPUESTA:")
print(repr(d["message"]["content"]))