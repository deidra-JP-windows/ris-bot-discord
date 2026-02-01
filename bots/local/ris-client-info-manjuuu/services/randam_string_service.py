from datetime import datetime, timedelta
import random
import string


class RandamStringService:

    async def send_random_string(self, message) -> None:
        """
        ランダムな文字列をチャンネルに送信
        Args:
            message: Discordのメッセージオブジェクト
        Returns:
            None
        """
        rand_str = "".join(random.choices(string.ascii_letters + string.digits, k=12))
        await message.channel.send(rand_str)

    async def send_health_check(self, message) -> None:
        """
        ヘルスチェックメッセージをチャンネルに送信
        Args:
            message: Discordのメッセージオブジェクト
        Returns:
            None
        """
        await message.channel.send("生存")

    async def send_greeting(self, message) -> None:
        """
        挨拶メッセージをチャンネルに送信
        Args:
            message: Discordのメッセージオブジェクト
        Returns:
            None
        """
        await message.channel.send("おはようございます！")

    async def send_random_chat_line(self, message) -> None:
        """
        一週間分のチャットからランダムな一行を低確率で送信
        Args:
            message: Discordのメッセージオブジェクト
        Returns:
            None
        """
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        messages = []
        async for msg in message.channel.history(after=week_ago, limit=500):
            if msg.content:
                messages.append(msg.content)
        if messages:
            await message.channel.send(random.choice(messages))
