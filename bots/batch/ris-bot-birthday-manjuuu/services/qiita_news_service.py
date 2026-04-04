import os
import discord
import httpx
from dotenv import load_dotenv


class QiitaNewsService:

    def __init__(self):
        """
        処理概要:
            1. 環境変数を読み込む
            2. チャンネルIDとQiita APIエンドポイントを初期化する

        補足:
            1. SEND_QIITA_CHANNEL_ID を環境変数から取得する
        
        Args:
            None
        
        Returns:
            None
        """
        # 1. 環境変数を読み込む
        load_dotenv()
        # 2. チャンネルIDとQiita APIエンドポイントを初期化する
        self.SEND_QIITA_CHANNEL_ID = int(os.getenv("SEND_QIITA_CHANNEL_ID"))
        self.QIITA_API_ENDPOINT = "https://qiita.com/api/v2/items"

    async def _get_qiita_top_news(self):
        """
        処理概要:
            1. httpxライブラリを使用してQiita APIにGETリクエストを送信
            2. レスポンスからフィルタリングを行い、最新記事のタイトルとURLを抽出
            3. 抽出したデータを辞書形式で返す
        
        補足:
            リクエストのフォーマット:
                GET /api/v2/items?page=1&per_page=1 HTTP/1
                Host: qiita.com
                Accept: application/json
            curl での打鍵例:
                curl -H "Accept: application/json" \
                "https://qiita.com/api/v2/items?page=1&per_page=1" \
                | jq '.[] | {title: .title, url: .url}'
            レスポンスの取得例:
                {
                    "title": " ブロックチェーンデータモデルのすべて [Sui Foundation Blog]",
                    "url": "https://qiita.com/nft/items/c9e2ed2f1198befe0de4"
                }
        
        Args:
            None
        
        Returns:
            dict: 最新記事のタイトルとURLを含む辞書
        """
        # 1. httpxライブラリを使用してQiita APIにGETリクエストを送信
        async with httpx.AsyncClient() as client:
            params = {"page": 1, "per_page": 1}
            headers = {"Accept": "application/json"}
            response = await client.get(
                self.QIITA_API_ENDPOINT, params=params, headers=headers
            )
            response.raise_for_status()
            # 2. レスポンスからフィルタリングを行い、最新記事のタイトルとURLを抽出
            items = response.json()
            if items:
                top_item = items[0]
                # 3. 抽出したデータを辞書形式で返す
                return {
                    "title": top_item.get("title", "タイトル不明"),
                    "url": top_item.get("url", "URL不明"),
                }
            else:
                # 3. 抽出したデータを辞書形式で返す
                return {"title": "記事なし", "url": ""}
        return

    async def _formatter_qiita_news_message(self, qiita_news: dict) -> str:
        """
        処理概要:
            1. 辞書からタイトルとURLを抽出
            2. フォーマットされたメッセージ文字列を生成
        
        Args:
            qiita_news (dict): Qiita記事のタイトルとURLを含む辞書
        
        Returns:
            str: フォーマットされたメッセージ文字列
        """
        # 1. 辞書からタイトルとURLを抽出
        title = qiita_news.get("title", "タイトル不明")
        url = qiita_news.get("url", "URL不明")
        # 2. フォーマットされたメッセージ文字列を生成
        message = f"最新のQiita記事はこちら！\n**{title}**\n{url}"
        return message

    async def _send_qiita_news_message(
        self, send_qiita_channel: "discord.TextChannel", message: str
    ):
        """
        処理概要:
            1. Discordのsendメソッドを使用してメッセージを送信
        
        Args:
            send_qiita_channel (discord.TextChannel): メッセージを送信するチャンネルオブジェクト
            message (str): 送信するメッセージ文字列
        
        Returns:
            None
        """
        # 1. Discordのsendメソッドを使用してメッセージを送信
        await send_qiita_channel.send(message)

    async def get_qiita_news_main(self, client):
        """
        処理概要:
            1. _get_qiita_top_newsメソッドを呼び出して最新記事を取得
            2. 取得した記事のタイトルとURLをフォーマット
            3. 指定されたDiscordチャンネルにメッセージを送信
        
        Args:
            client (discord.Client): Discordクライアントオブジェクト
        
        Returns:
            None
        """
        print("start: get_qiita_news_main")
        # 1. _get_qiita_top_newsメソッドを呼び出して最新記事を取得
        send_qiita_channel = client.get_channel(self.SEND_QIITA_CHANNEL_ID)
        qiita_news = await self._get_qiita_top_news()
        # 2. 取得した記事のタイトルとURLをフォーマット
        message = await self._formatter_qiita_news_message(qiita_news)
        # 3. 指定されたDiscordチャンネルにメッセージを送信
        await self._send_qiita_news_message(send_qiita_channel, message)
        return
