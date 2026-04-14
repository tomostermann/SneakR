import requests



KICKSDB_API_KEY  = "REDACTED"  
KICKSDB_BASE_URL = "https://api.kicks.dev"
LLM_URL          = "http://127.0.0.1:1234/v1/chat/completions"
LLM_MODEL        = "meta-llama-3.1-8b-instruct"

system_prompt_base = """You are SneakR, a sneaker resale pricing expert with 10 years of experience.

## Identity
- You speak English, in a direct and passionate way
- You use industry terms : DS, deadstock, retail, hype, plug, grail, bricks
- You are confident in your estimations
- You are polite
- You say hello in a new conversation
- You thank the customer when they give you information

## Mandatory response format
💰 Suggested price : €XXX - €XXX  (tight 10€ range max)
📏 Size premium : (mention if size affects price)
📈 Market trend : rising / stable / dropping
⚡ My advice : (1 sentence)

## Pricing Rules
- ALWAYS ask for size (EU) + condition (/10) if not specified
- If the customer forgets to tell about the condition, ask again. Do not give any suggestion until condition is provided
- Give a TIGHT price range (max 10€ difference, ex: €185 - €195)
- Adjust price based on size (rare sizes = higher price)
- ALWAYS ask for the exact model + colorway if not specified or ambiguous
- Condition affects price :
    10/10 DS  → full market price
    9/10      → -10%
    8/10      → -20%
    7/10      → -30%
    6/10      → -40%
    5/10      → -50%
    4/10      → -60%
    3/10      → -70%
    2/10      → -80%
    1/10      → -90%
- Under a condition of 4/10 recommend the customer to not sell his shoes
- Base prices strictly on the live market data provided below
- ONLY talk about sneakers
- Never say "I don't know"
- Do not mention any resale platform by name

## Off-topic
If question is not sneaker related, reply only:
"I'm a sneaker specialist only 👟"
"""



historique = []


def extraire_nom_sneaker(message):
    try:
        response = requests.post(LLM_URL, json={
            "model": LLM_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Extract only the sneaker model name and colorway from the message. "
                        "Return ONLY the sneaker name, nothing else. "
                        "Examples: 'Yeezy Slide Pure', 'Air Jordan 1 Bred', 'New Balance 2002R Blue'"
                    )
                },
                {"role": "user", "content": message}
            ],
            "temperature": 0,
            "max_tokens": 20
        })
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Erreur extraction nom : {e}")
        return message 


def chercher_sneaker(message):
    try:
        query_clean = extraire_nom_sneaker(message)
        print(f" Query extraite : {query_clean}")

        response = requests.get(
            f"{KICKSDB_BASE_URL}/v3/stockx/products",
            headers={"Authorization": f"Bearer {KICKSDB_API_KEY}"},
            params={
                "query": query_clean,
                "limit": 3,
                "market": "FR",
                "display[prices]": "true",
                "display[variants]": "true",
                "sort": "rank"
            },
            timeout=5
        )
        print(f" Réponse : {response.status_code}")

        data = response.json()

        if response.status_code != 200 or "data" not in data or not data["data"]:
            print("Aucune donnée trouvée.")
            return "No live market data available for this model."

        lignes = []
        for sneaker in data["data"]:
            min_p    = sneaker.get("min_price", "N/A")
            max_p    = sneaker.get("max_price", "N/A")
            avg_p    = sneaker.get("avg_price", "N/A")
            sales_30 = sneaker.get("sales_count_30_days", "N/A")
            sales_15 = sneaker.get("sales_count_15_days", "N/A")

            variants = sneaker.get("variants", []) or []
            tailles  = [str(v.get("size")) for v in variants if v.get("size")]

            lignes.append(
                f"- {sneaker.get('title')} | "
                f"SKU: {sneaker.get('sku', 'N/A')} | "
                f"Min: €{min_p} | Max: €{max_p} | Avg: €{avg_p} | "
                f"Sales last 15d: {sales_15} | Sales last 30d: {sales_30} | "
                f"Available sizes (EU): {', '.join(tailles) if tailles else 'N/A'}"
            )

        return "\n".join(lignes)

    except Exception as e:
        print(f"Erreur KicksDB : {e}")
        return "Live market data unavailable."




def envoyer_message(message_utilisateur):

    donnees_live = chercher_sneaker(message_utilisateur)
    print(f" Données injectées :\n{donnees_live}\n")

    system_dynamique = {
        "role": "system",
        "content": system_prompt_base + f"\n## Live Market Data (StockX FR)\n{donnees_live}"
    }

    historique.append({"role": "user", "content": message_utilisateur})
    response = requests.post(LLM_URL, json={
        "model": LLM_MODEL,
        "messages": [system_dynamique] + historique,
        "temperature": 0.3,
        "max_tokens": 250
    })

    reply = response.json()["choices"][0]["message"]["content"]
    historique.append({"role": "assistant", "content": reply})
    return reply