import random


class RandamStringService:

    async def send_random_game_title(self, message) -> None:
        """
        処理概要:
            1. ゲームタイトルのリストからランダムに1つ選択
            2. 選択したゲームタイトルをチャンネルに送信
        
        Args:
            message: Discordのメッセージオブジェクト
        
        Returns:
            None
        """
        # 1. ゲームタイトルのリストからランダムに1つ選択
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
        # 2. 選択したゲームタイトルをチャンネルに送信
        await message.channel.send(f"今日のおすすめゲームタイトル: {random_title}")
