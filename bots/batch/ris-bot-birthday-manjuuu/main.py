import os
import discord
from dotenv import load_dotenv
from services.birthday_notification_service import BirthdayNotificationService
from services.youtube_pickup_song_service import YouTubePickupSongService

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
    birthday_service = BirthdayNotificationService()
    youtube_service = YouTubePickupSongService()
    await birthday_service.birthday_notification_main(client)
    await youtube_service.add_youTube_playlist_main(client)
    await client.close()

if __name__ == "__main__":
    client.run(DISCORD_BOT_TOKEN)
