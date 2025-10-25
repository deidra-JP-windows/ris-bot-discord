import re
import os
import discord
import json
import base64
import random
from apiclient.discovery import build
from apiclient.errors import HttpError
from dotenv import load_dotenv
from datetime import datetime, timedelta
from google.oauth2 import service_account


class YouTubePickupSongService:


    def __init__(self):
        load_dotenv()
        # Repository secretsから取得する環境変数名に統一
        self.READ_MUSIC_CHANNEL_ID = int(os.getenv("READ_MUSIC_CHANNEL_ID"))
        self.SEND_MUSIC_CHANNEL_ID = int(os.getenv("SEND_MUSIC_CHANNEL_ID"))
        # YouTube URL抽出用正規表現
        self.YOUTUBE_URL_PATTERN = re.compile(r"https://(youtu\.be/|www\.youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})")


    async def _get_all_youtube_urls(self, read_music_channel: 'discord.TextChannel'):
        """
        おすすめ曲チャンネルから全期間のYouTube動画URLと送信者名のタプルを取得

        Args: 
            read_music_channel (discord.TextChannel): YouTube動画URLを取得するチャンネルオブジェクト
        Returns: 
            tuple: (YouTube動画URL, 送信者名) のタプル
        """
        youtube_url_senders = set()
        async for message in read_music_channel.history(limit=None):
            for match in self.YOUTUBE_URL_PATTERN.finditer(message.content):
                url = match.group(0)
                sender = message.author.display_name if hasattr(message.author, 'display_name') else str(message.author)
                youtube_url_senders.add((url, sender))
        return tuple(youtube_url_senders)


    def _random_sample_youtube_urls(self, youtube_url_senders, sample_size=3):
        """
        YouTube動画URLと送信者のリストからランダムに指定数を抽出

        Args:
            youtube_url_senders (tuple): (URL,送信者)のタプル
            sample_size (int): 抽出する数（デフォルトは3）
        Returns:
            list: 抽出された(YouTube動画URL,送信者)のリスト
        """
        return random.sample(youtube_url_senders, min(sample_size, len(youtube_url_senders)))


    async def _clear_channel_messages(self, send_music_channel: 'discord.TextChannel'):
        """
        おすすめ曲をピックアップするチャンネルからすべてのメッセージを削除

        Args: 
            send_music_channel (discord.TextChannel): メッセージを削除するチャンネルオブジェクト
        Returns:
            None
        """
        async for message in send_music_channel.history(limit=None):
            await message.delete()


    async def _post_youtube_urls(self, send_music_channel: 'discord.TextChannel', youtube_url_senders: tuple):
        """
        おすすめ曲をピックアップするチャンネルにYouTube動画URLと送信者を投稿

        Args: 
            send_music_channel (discord.TextChannel): メッセージを投稿するチャンネルオブジェクト
            youtube_url_senders (tuple): 投稿する(YouTube動画URL,送信者)のタプル
        Returns:
            None
        """
        for url, sender in youtube_url_senders:
            await send_music_channel.send(f"{sender} のおすすめ！\n{url}")


    async def add_youTube_playlist_main(self, client: 'discord.Client'):
        """
        メイン処理
        Args:
            client (discord.Client): Discordクライアントオブジェクト
        Returns:
            None
        """
        print("start: add_youTube_playlist_main")
        # チャンネルクライアントの取得
        send_music_channel = client.get_channel(self.SEND_MUSIC_CHANNEL_ID)
        read_music_channel = client.get_channel(self.READ_MUSIC_CHANNEL_ID)

        # すべてのYouTube動画URLを取得
        youtube_urls = await self._get_all_youtube_urls(read_music_channel)
        if not youtube_urls:
            print("No YouTube URLs found.")
            return
        # ランダムに3件のみ抽出
        youtube_urls = self._random_sample_youtube_urls(youtube_urls, sample_size=3)
        # おすすめ曲をピックアップするチャンネルからすべてのメッセージを削除
        await self._clear_channel_messages(send_music_channel)
        # おすすめ曲をピックアップするチャンネルに3件のYouTube動画URLを投稿
        await self._post_youtube_urls(send_music_channel, youtube_urls)
        print("end: add_youTube_playlist_main")
