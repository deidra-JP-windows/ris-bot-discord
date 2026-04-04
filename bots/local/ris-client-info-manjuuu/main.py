import os
import random
import discord
from dotenv import load_dotenv
from services.randam_string_service import RandamStringService

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")


class MyClient(discord.Client):

    randam_string_service = RandamStringService()

    async def on_ready(self):
        """
        処理概要:
            1. クライアントが準備完了時にユーザー名を出力
        
        Args:
            None
        
        Returns:
            None
        """
        # 1. クライアントが準備完了時にユーザー名を出力
        print("俺は", self.user, "だ")

    async def on_message(self, message):
        """
        処理概要:
            1. メッセージがBot自身のものであれば無視
            2. メッセージ内容に応じて適切なサービスメソッドを呼び出す
            3. ランダム文字列コマンドは5%の確率でチャット履歴からランダム送信

        条件:
            1. /manjuuu ランダム文字列 のとき、5%の確率で send_random_chat_line を実行する
        
        Args:
            message: Discordのメッセージオブジェクト
        
        Returns:
            None
        """
        # 1. メッセージがBot自身のものであれば無視
        if message.author == self.user:
            return
        # 2. メッセージ内容に応じて適切なサービスメソッドを呼び出す
        if message.content == "/manjuuu ヘルスチェック":
            await self.randam_string_service.send_health_check(message)
        elif message.content == "/manjuuu こんにちは":
            await self.randam_string_service.send_greeting(message)
        elif message.content == "/manjuuu ランダム文字列":
            # 3. ランダム文字列コマンドは5%の確率でチャット履歴からランダム送信
            if random.random() < 0.05:
                await self.randam_string_service.send_random_chat_line(message)
            else:
                await self.randam_string_service.send_random_string(message)


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = MyClient(intents=intents)
client.run(DISCORD_BOT_TOKEN)
