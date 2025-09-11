import re
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# env読み込み
load_dotenv()
# Repository secretsから取得する環境変数名に統一
READ_BIRTHDAY_CHANNEL_ID = int(os.getenv("READ_BIRTHDAY_CHANNEL_ID"))
SEND_GENERAL_CHANNEL_ID = int(os.getenv("SEND_GENERAL_CHANNEL_ID"))



async def add_youTube_playlist_main(client: 'discord.Client'):
    print("start: add_youTube_playlist_main")
    client.get_channel(READ_BIRTHDAY_CHANNEL_ID).history(limit=None)
    await client.get_channel(SEND_GENERAL_CHANNEL_ID).send('test')
    print("end: add_youTube_playlist_main")
