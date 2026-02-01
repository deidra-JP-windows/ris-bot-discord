import os
import random
import discord
from dotenv import load_dotenv
from services.randam_string_service import RandamStringService

# env読み込み
load_dotenv()
# Repository secretsから取得する環境変数名に統一
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")


class MyClient(discord.Client):

    randam_string_service = RandamStringService()

    async def on_ready(self):
        print("俺は", self.user, "だ")

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content == "/manjuuu ヘルスチェック":
            await self.randam_string_service.send_health_check(message)
        elif message.content == "/manjuuu こんにちは":
            await self.randam_string_service.send_greeting(message)
        elif message.content == "/manjuuu ランダム文字列":
            if random.random() < 0.05:  # 5%の確率
                await self.randam_string_service.send_random_chat_line(message)
            else:
                await self.randam_string_service.send_random_string(message)


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = MyClient(intents=intents)
client.run(DISCORD_BOT_TOKEN)
