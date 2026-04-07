import requests

response = requests.post("http://127.0.0.1:1234/v1/chat/completions", json={
    "model": "mistralai/mistral-7b-instruct-v0.3",
    "messages": [
        {
            "role": "user",
            "content": "Tu es SoleAdvisor, expert en pricing de sneakers de revente. Réponds en français.\n\nJe veux vendre mes Air Jordan 1 Chicago taille 42, état 8/10. Quel prix me conseilles-tu ?"
        }
    ],
    "temperature": 0.7,
    "max_tokens": 200
})

data = response.json()
print(data)