import os
import discord
import asyncio
from dotenv import load_dotenv
from services.randam_string import randam_string_main

# env読み込み
load_dotenv()
# Repository secretsから取得する環境変数名に統一
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    # サービス層のメイン処理を非同期で開始
    asyncio.create_task(randam_string_main(client))


if __name__ == "__main__":
    client.run(DISCORD_BOT_TOKEN)
