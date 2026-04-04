import os
import discord
from dotenv import load_dotenv
from services.birthday_notification_service import BirthdayNotificationService
from services.youtube_pickup_song_service import YouTubePickupSongService
from services.qiita_news_service import QiitaNewsService

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    """
    処理概要:
        1. 各サービスのインスタンスを作成
        2. 誕生日通知、YouTubeプレイリスト、Qiitaニュースの各処理を実行
        3. クライアントを閉じる
    
    Args:
        None
    
    Returns:
        None
    """
    # 1. 各サービスのインスタンスを作成
    birthday_service = BirthdayNotificationService()
    youtube_service = YouTubePickupSongService()
    qiita_service = QiitaNewsService()
    # 2. 誕生日通知、YouTubeプレイリスト、Qiitaニュースの各処理を実行
    await birthday_service.birthday_notification_main(client)
    await youtube_service.add_youTube_playlist_main(client)
    await qiita_service.get_qiita_news_main(client)
    # 3. クライアントを閉じる
    await client.close()


if __name__ == "__main__":
    client.run(DISCORD_BOT_TOKEN)
