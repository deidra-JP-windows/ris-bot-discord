import re
import os
import discord
from apiclient.discovery import build
from apiclient.errors import HttpError
from dotenv import load_dotenv
from datetime import datetime, timedelta


# YouTube URL抽出用正規表現
YOUTUBE_URL_PATTERN = re.compile(r"https?://(?:www\\.)?(?:youtube\\.com/watch\\?v=|youtu\\.be/)([\\w-]{11})")

# env読み込み
load_dotenv()
# Repository secretsから取得する環境変数名に統一
READ_MUSIC_CHANNEL_ID = int(os.getenv("READ_MUSIC_CHANNEL_ID"))

DEVELOPER_KEY = os.getenv("DEVELOPER_KEY")
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
YOUTUBE_PLAYLIST_ID = os.getenv("YOUTUBE_PLAYLIST_ID")


async def fetch_playlist_videos():
    """
    プレイリスト内の動画タイトルとURLをタプルで取得
    """
    videos = []
    request = youtube.playlistItems().list(
        part='snippet',
        playlistId=YOUTUBE_PLAYLIST_ID,
        maxResults=50
    )
    response = request.execute()
    for item in response['items']:
        video_id = item['snippet']['resourceId']['videoId']
        title = item['snippet']['title']
        url = f'https://www.youtube.com/watch?v={video_id}'
        videos.append((title, url))
    return videos


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


def filter_new_youtube_urls(youtube_urls, existing_urls):
    """
    既存URLと比較して新規のYouTube動画URLのみを返す
    """
    return [url for url in youtube_urls if url not in existing_urls]


async def add_urls_to_playlist(new_urls):
    """
    新規YouTube動画URLリストをプレイリストに追加
    """
    for url in new_urls:
        try:
            video_id_match = YOUTUBE_URL_PATTERN.search(url)
            if video_id_match:
                video_id = video_id_match.group(1)
                youtube.playlistItems().insert(
                    part='snippet',
                    body={
                        'snippet': {
                            'playlistId': YOUTUBE_PLAYLIST_ID,
                            'resourceId': {
                                'kind': 'youtube#video',
                                'videoId': video_id
                            }
                        }
                    }
                ).execute()
                print(f"Added to playlist: {url}")
        except HttpError as e:
            print(f"An HTTP error occurred: {e.resp.status} - {e.content}")
        except Exception as e:
            print(f"An error occurred: {e}")


async def add_youTube_playlist_main(client: 'discord.Client'):
    print("start: add_youTube_playlist_main")
    # 先週分のYouTube動画URLを取得
    youtube_urls = await get_last_week_youtube_urls(client)
    print(youtube_urls)
    if not youtube_urls:
        print("No YouTube URLs found in the last week.")
        return

    # プレイリストの既存動画を取得
    existing_videos = await fetch_playlist_videos()
    existing_urls = {url for title, url in existing_videos}
    print(existing_urls)

    # 追加する動画URLをフィルタリング
    new_urls = filter_new_youtube_urls(youtube_urls, existing_urls)
    print(new_urls)
    if not new_urls:
        print("No new YouTube URLs to add to the playlist.")
        return

    # プレイリストに新しい動画を追加
    await add_urls_to_playlist(new_urls)
    print("end: add_youTube_playlist_main")
