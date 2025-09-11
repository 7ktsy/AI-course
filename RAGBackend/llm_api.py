import requests

API_KEY = "ragflow-FINDljYzUM0ZwMTExZjA5NGUxMGU0NW"
CHAT_ID = "3b4a7ac43e2411f0860c0e45b9310001"

def call_chatglm(prompt: str):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    payload = {
        "model": "glm-4",
        "messages": [{"role": "user", "content": prompt}]
    }
    resp = requests.post(url, headers=headers, json=payload)
    return resp.json()["choices"][0]["message"]["content"]
