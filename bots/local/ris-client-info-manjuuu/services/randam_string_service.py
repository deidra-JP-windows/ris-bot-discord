from datetime import datetime, timedelta
import random
import string


class RandamStringService:

    async def send_random_string(self, message) -> None:
        """
        処理概要:
            1. アルファベットと数字からランダムに12文字を選択
            2. 生成した文字列をチャンネルに送信
        
        Args:
            message: Discordのメッセージオブジェクト
        
        Returns:
            None
        """
        # 1. アルファベットと数字からランダムに12文字を選択
        rand_str = "".join(random.choices(string.ascii_letters + string.digits, k=12))
        # 2. 生成した文字列をチャンネルに送信
        await message.channel.send(rand_str)

    async def send_health_check(self, message) -> None:
        """
        処理概要:
            1. ヘルスチェックメッセージ「生存」をチャンネルに送信
        
        Args:
            message: Discordのメッセージオブジェクト
        
        Returns:
            None
        """
        # 1. ヘルスチェックメッセージ「生存」をチャンネルに送信
        await message.channel.send("生存")

    async def send_greeting(self, message) -> None:
        """
        処理概要:
            1. 挨拶メッセージ「おはようございます！」をチャンネルに送信
        
        Args:
            message: Discordのメッセージオブジェクト
        
        Returns:
            None
        """
        # 1. 挨拶メッセージ「おはようございます！」をチャンネルに送信
        await message.channel.send("おはようございます！")

    async def send_random_chat_line(self, message) -> None:
        """
        処理概要:
            1. 一週間分のチャット履歴を取得(最大500件)
            2. 取得したメッセージからランダムに1行を選択
            3. 選択したメッセージをチャンネルに送信
        
        Args:
            message: Discordのメッセージオブジェクト
        
        Returns:
            None
        """
        # 1. 一週間分のチャット履歴を取得(最大500件)
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        messages = []
        async for msg in message.channel.history(after=week_ago, limit=500):
            if msg.content:
                messages.append(msg.content)
        # 2. 取得したメッセージからランダムに1行を選択
        # 3. 選択したメッセージをチャンネルに送信
        if messages:
            await message.channel.send(random.choice(messages))
