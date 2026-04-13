
from bot import envoyer_message, warmup
import discord

TOKEN = "REDACTED"

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print("Chargement du modèle...")
    warmup()
    print(f"SneakR prêt et connecté en tant que {client.user} 👟")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    async with message.channel.typing():
        reply = envoyer_message(message.content)
    
    await message.channel.send(reply)

client.run(TOKEN)