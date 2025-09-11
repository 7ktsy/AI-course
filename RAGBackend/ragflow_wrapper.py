import requests

def search_from_ragflow(query: str, top_k: int = 3) -> list[str]:
    url = "http://localhost:8080/search" 
    resp = requests.post(url, json={"question": query, "top_k": top_k})
    data = resp.json()
    return [item["content"] for item in data["results"]]
