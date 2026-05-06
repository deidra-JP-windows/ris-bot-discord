import os
import re
import discord
import random
from dotenv import load_dotenv


class YouTubePickupSongService:

    def __init__(self):
        """
        処理概要:
            1. 環境変数を読み込む
            2. チャンネルIDとYouTube URL抽出用正規表現を初期化する

        補足:
            1. youtu.be と youtube.com/watch?v= のURLに対応する

        Args:
            None

        Returns:
            None
        """
        # 1. 環境変数を読み込む
        load_dotenv()
        # 2. チャンネルIDとYouTube URL抽出用正規表現を初期化する
        self.READ_MUSIC_CHANNEL_ID = int(os.getenv("READ_MUSIC_CHANNEL_ID"))
        self.SEND_MUSIC_CHANNEL_ID = int(os.getenv("SEND_MUSIC_CHANNEL_ID"))
        self.YOUTUBE_URL_PATTERN = re.compile(
            r"https://(youtu\.be/|www\.youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})"
        )

    async def _get_all_youtube_urls(self, read_music_channel: "discord.TextChannel"):
        """
        処理概要:
            1. おすすめ曲チャンネルから全期間のメッセージを取得
            2. 正規表現でYouTube URLを抽出
            3. URLと送信者名のタプルをセットに格納して返す

        Args:
            read_music_channel (discord.TextChannel): YouTube動画URLを取得するチャンネルオブジェクト

        Returns:
            tuple: (YouTube動画URL, 送信者名) のタプル
        """
        # 1. おすすめ曲チャンネルから全期間のメッセージを取得
        youtube_url_senders = set()
        async for message in read_music_channel.history(limit=None):
            # 2. 正規表現でYouTube URLを抽出
            for match in self.YOUTUBE_URL_PATTERN.finditer(message.content):
                url = match.group(0)
                sender = (
                    message.author.display_name
                    if hasattr(message.author, "display_name")
                    else str(message.author)
                )
                # 3. URLと送信者名のタプルをセットに格納して返す
                youtube_url_senders.add((url, sender))
        return tuple(youtube_url_senders)

    def _random_sample_youtube_urls(self, youtube_url_senders, sample_size=3):
        """
        処理概要:
            1. YouTube動画URLと送信者のリストからランダムに指定数を抽出

        Args:
            youtube_url_senders (tuple): (URL,送信者)のタプル
            sample_size (int): 抽出する数(デフォルトは3)

        Returns:
            list: 抽出された(YouTube動画URL,送信者)のリスト
        """
        # 1. YouTube動画URLと送信者のリストからランダムに指定数を抽出
        return random.sample(
            youtube_url_senders, min(sample_size, len(youtube_url_senders))
        )

    async def _clear_channel_messages(self, send_music_channel: "discord.TextChannel"):
        """
        処理概要:
            1. おすすめ曲をピックアップするチャンネルからすべてのメッセージを削除

        Args:
            send_music_channel (discord.TextChannel): メッセージを削除するチャンネルオブジェクト

        Returns:
            None
        """
        # 1. おすすめ曲をピックアップするチャンネルからすべてのメッセージを削除
        async for message in send_music_channel.history(limit=None):
            await message.delete()

    async def _post_youtube_urls(
        self, send_music_channel: "discord.TextChannel", youtube_url_senders: tuple
    ):
        """
        処理概要:
            1. おすすめ曲をピックアップするチャンネルにYouTube動画URLと送信者を投稿

        Args:
            send_music_channel (discord.TextChannel): メッセージを投稿するチャンネルオブジェクト
            youtube_url_senders (tuple): 投稿する(YouTube動画URL,送信者)のタプル

        Returns:
            None
        """
        # 1. おすすめ曲をピックアップするチャンネルにYouTube動画URLと送信者を投稿
        for url, sender in youtube_url_senders:
            await send_music_channel.send(f"{sender} のおすすめ！\n{url}")

    async def add_youTube_playlist_main(self, client: "discord.Client"):
        """
        処理概要:
            1. チャンネルクライアントを取得
            2. すべてのYouTube動画URLを取得
            3. ランダムに3件のみ抽出
            4. おすすめ曲をピックアップするチャンネルからすべてのメッセージを削除
            5. おすすめ曲をピックアップするチャンネルに3件のYouTube動画URLを投稿

        Args:
            client (discord.Client): Discordクライアントオブジェクト

        Returns:
            None
        """
        print("start: add_youTube_playlist_main")
        # 1. チャンネルクライアントを取得
        send_music_channel = client.get_channel(self.SEND_MUSIC_CHANNEL_ID)
        read_music_channel = client.get_channel(self.READ_MUSIC_CHANNEL_ID)
        # 2. すべてのYouTube動画URLを取得
        youtube_urls = await self._get_all_youtube_urls(read_music_channel)
        if not youtube_urls:
            print("No YouTube URLs found.")
            return
        # 3. ランダムに3件のみ抽出
        youtube_urls = self._random_sample_youtube_urls(youtube_urls, sample_size=3)
        # 4. おすすめ曲をピックアップするチャンネルからすべてのメッセージを削除
        await self._clear_channel_messages(send_music_channel)
        # 5. おすすめ曲をピックアップするチャンネルに3件のYouTube動画URLを投稿
        await self._post_youtube_urls(send_music_channel, youtube_urls)
        print("end: add_youTube_playlist_main")
