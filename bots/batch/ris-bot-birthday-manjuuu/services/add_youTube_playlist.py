import re
import os
import discord
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
from datetime import datetime, timedelta


# YouTube URL抽出用正規表現
YOUTUBE_URL_PATTERN = re.compile(r"https?://(?:www\\.)?(?:youtube\\.com/watch\\?v=|youtu\\.be/)([\\w-]{11})")

# env読み込み
load_dotenv()
# Repository secretsから取得する環境変数名に統一
READ_MUSIC_CHANNEL_ID = int(os.getenv("READ_MUSIC_CHANNEL_ID"))
READ_MUSIC_LIST_CHANNEL_ID = int(os.getenv("READ_MUSIC_LIST_CHANNEL_ID"))
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

# YouTube Playlist ID (環境変数から取得)
YOUTUBE_PLAYLIST_ID = os.getenv("YOUTUBE_PLAYLIST_ID")
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def get_youtube_service():
    """
    サービスアカウント認証でYouTube APIクライアントを取得
    """
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build("youtube", "v3", credentials=credentials)


def add_videos_to_playlist(video_urls, playlist_id):
    """
    指定したYouTube動画URLリストをプレイリストに追加
    """
    youtube = get_youtube_service()
    for url in video_urls:
        # 動画ID抽出
        m = re.search(r"(?:v=|youtu.be/)([\w-]{11})", url)
        if not m:
            continue
        video_id = m.group(1)
        try:
            youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
            ).execute()
        except Exception as e:
            print(f"Failed to add {video_id}: {e}")


async def add_youTube_playlist_main(client: 'discord.Client'):
    print("start: add_youTube_playlist_main")
    try:
        urls = await get_last_week_youtube_urls(client)
        if not urls:
            await client.get_channel(READ_MUSIC_LIST_CHANNEL_ID).send('先週分のYouTube動画は見つかりませんでした。')
            print("No YouTube URLs found.")
            return
        add_videos_to_playlist(urls, YOUTUBE_PLAYLIST_ID)
        await client.get_channel(READ_MUSIC_LIST_CHANNEL_ID).send(f'{len(urls)}件のYouTube動画をプレイリストに追加しました。')
        print(f"Added {len(urls)} videos to playlist.")
    except Exception as e:
        await client.get_channel(READ_MUSIC_LIST_CHANNEL_ID).send(f'エラーが発生しました: {e}')
        print(f"Error: {e}")
    print("end: add_youTube_playlist_main")


async def get_last_week_youtube_urls(client: 'discord.Client'):
    """
    おすすめ曲チャンネルから先週分のYouTube動画URLをタプルで取得
    """
    channel = client.get_channel(READ_MUSIC_CHANNEL_ID)
    now = datetime.utcnow()
    one_week_ago = now - timedelta(days=7)
    youtube_urls = set()
    async for message in channel.history(limit=None, after=one_week_ago):
        for match in YOUTUBE_URL_PATTERN.finditer(message.content):
            # フルURLを取得
            url = match.group(0)
            youtube_urls.add(url)
    return tuple(youtube_urls)
