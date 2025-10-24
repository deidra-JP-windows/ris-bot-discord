import re
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# env読み込み
load_dotenv()
# Repository secretsから取得する環境変数名に統一
SEND_GENERAL_CHANNEL_ID = int(os.getenv("SEND_GENERAL_CHANNEL_ID"))


# ランダム文字列生成用
import random
import string
import asyncio
import discord

class IRandamStringService:
    async def send_random_string(self, client: discord.Client) -> None:
        """
        ランダムな文字列を一般チャンネルに送信
        Args:
            client (discord.Client): Discordクライアント
        Returns:
            None
        """
        pass

    async def send_random_chat_line(self, client: discord.Client) -> None:
        """
        一週間分のチャットからランダムな一行を低確率で送信
        Args:
            client (discord.Client): Discordクライアント
        Returns:
            None
        """
        pass

class RandamStringService(IRandamStringService):
    async def send_random_string(self, client: discord.Client) -> None:
        """
        ランダムな文字列を一般チャンネルに送信
        Args:
            client (discord.Client): Discordクライアント
        Returns:
            None
        """
        channel = client.get_channel(SEND_GENERAL_CHANNEL_ID)
        if channel:
            rand_str = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            await channel.send(rand_str)

    async def send_random_chat_line(self, client: discord.Client) -> None:
        """
        一週間分のチャットからランダムな一行を低確率で送信
        Args:
            client (discord.Client): Discordクライアント
        Returns:
            None
        """
        channel = client.get_channel(SEND_GENERAL_CHANNEL_ID)
        if channel and random.random() < 0.05:  # 5%の確率
            now = datetime.now()
            week_ago = now - timedelta(days=7)
            messages = []
            async for msg in channel.history(after=week_ago, limit=500):
                if msg.content:
                    messages.append(msg.content)
            if messages:
                await channel.send(random.choice(messages))

async def randam_string_main(client: discord.Client) -> None:
    """
    メイン処理: 定期的にランダム文字列送信・低確率でチャットランダム一行送信
    Args:
        client (discord.Client): Discordクライアント
    Returns:
        None
    """
    service = RandamStringService()
    while True:
        await service.send_random_string(client)
        await service.send_random_chat_line(client)
        await asyncio.sleep(3600)  # 1時間ごとに実行
