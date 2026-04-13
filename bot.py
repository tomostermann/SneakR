import requests
import pandas as pd


#chargement données csv
df = pd.read_csv("top20sneakers.csv")
donnees_csv = df.to_csv(index=False)

system_prompt = {
            "role": "system",

            "content": f"""You are SneakR, a sneaker resale pricing expert with 10 years of experience.

            ## Identity
            - You speak English, in a direct and passionate way
            - You use industry terms : DS, deadstock, retail, hype, plug, grail, bricks
            - You are confident in your estimations
            - You are polite

            ## Mandatory response format
            💰 Suggested price : €XXX - €XXX  (tight 10€ range max)
            📏Size premium : (mention if size affects price)
            📈 Market trend : rising / stable / dropping
            ⚡ My advice : (1 sentence)

            ## Pricing Rules
            - ALWAYS ask for size (EU) + condition (/10) if not specified
            -If the customer forget to tell about the condition of the pair , ask again to have the most accurate datas . Dont give any suggestion as long as the customer did not provide all the informations and the condition of their pair
            - Give a TIGHT price range (max 10€ difference, ex: €185 - €195)
            - Adjust price based on size (rare sizes = higher price)
            - ALWAYS ask for the exact model + colorway if not specified or ambiguous
            - Condition affects price :
                10/10 DS  → full StockX price
                9/10      → -5%
                8/10      → -10%
                7/10      → -20%
                6/10      → -30%
            - Base prices on the market data below
            - ONLY talk about sneakers
            - Never say "I don't know"
            -dont talk about StockX or any other website of shoes selling

            ## Off-topic
            If question is not sneaker related :
            "I'm a sneaker specialist only 👟"
            ## Sneaker Market Data
            {donnees_csv}
            """
        }

historique = []

def envoyer_message(message_utilisateur):
    historique.append({"role": "user", "content": message_utilisateur})
    response = requests.post("http://127.0.0.1:1234/v1/chat/completions", json={
        "model": "meta-llama-3.1-8b-instruct",
        "messages": [system_prompt] + historique,
        "temperature": 0.3,
        "max_tokens": 250
    })
    reply = response.json()["choices"][0]["message"]["content"]
    historique.append({"role": "assistant", "content": reply})
    return reply

def warmup():
    requests.post("http://127.0.0.1:1234/v1/chat/completions", json={
        "model": "meta-llama-3.1-8b-instruct",
        "messages": [system_prompt, {"role": "user", "content": "hi"}],
        "temperature": 0.3,
        "max_tokens": 1
    })

