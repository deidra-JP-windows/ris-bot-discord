import random


class RandamStringService:

    async def send_random_game_title(self, message) -> None:
        """
        ランダムなゲームタイトルをチャンネルに送信
        Args:
            message: Discordのメッセージオブジェクト
        Returns:
            None
        """
        game_titles = [
            "Among Us",
            "Minecraft",
            "League of Legends",
            "VRChat",
            "Geo Guessr",
            "Human: Fall Flat",
            "麻雀",
            "Apex Legends",
            "Chill雑談",
            "Valorant",
        ]
        random_title = random.choice(game_titles)
        await message.channel.send(f"今日のおすすめゲームタイトル: {random_title}")
