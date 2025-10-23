import re
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# env読み込み
load_dotenv()
# Repository secretsから取得する環境変数名に統一
SEND_GENERAL_CHANNEL_ID = int(os.getenv("SEND_GENERAL_CHANNEL_ID"))

def randam_string_main(client: 'discord.Client'):
    print("start: randam_string_main")
    print("end: randam_string_main")
