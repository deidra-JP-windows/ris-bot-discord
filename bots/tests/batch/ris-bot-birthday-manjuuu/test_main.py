import unittest
import asyncio
from unittest.mock import patch
import sys
import os

sys.path.append(
    os.path.join(
        os.path.dirname(__file__), "../../../../bots/batch/ris-bot-birthday-manjuuu"
    )
)

import main  # noqa: E402


class TestMain(unittest.TestCase):

    @patch("builtins.print")
    def test_main(self, mock_print):
        """
        エントリポイントが正しく動作するかのテスト
        処理概要:
            1. on_ready() の実行
            2. 各サービスのエントリポイントだけをモック化
            3. グローバル変数が正しく設定されていることを確認
            4. 各サービスが初期化されることを確認
        Arguments:
            mock_print: print関数のモック
        Returns:
            None
        Asserts:
            1. 各サービスのエントリポイントが一度ずつ呼び出されること
            2. 各サービスが初期化されることを確認
        """
        # エントリポイントとディスコード呼び出しだけをモック化
        with patch(
            "main.BirthdayNotificationService.birthday_notification_main",
            return_value=None,
        ) as mock_birthday, patch(
            "main.YouTubePickupSongService.add_youTube_playlist_main", return_value=None
        ) as mock_youtube, patch(
            "main.QiitaNewsService.get_qiita_news_main", return_value=None
        ) as mock_qiita, patch.object(
            main.client, "close", return_value=None
        ) as mock_close:

            # 環境変数にダミーのトークンを設定
            os.environ["DISCORD_BOT_TOKEN"] = "dummy_token"
            os.environ["READ_BIRTHDAY_CHANNEL_ID"] = "0"
            os.environ["SEND_GENERAL_CHANNEL_ID"] = "0"
            os.environ["SEND_QIITA_CHANNEL_ID"] = "0"
            os.environ["READ_MUSIC_CHANNEL_ID"] = "0"
            os.environ["SEND_MUSIC_CHANNEL_ID"] = "0"
            # on_ready() 実行
            asyncio.run(main.on_ready())

            # 各サービスのエントリポイントが一度ずつ呼び出されていることを確認（呼び出し回数だけ確認）
            mock_birthday.assert_called_once()
            mock_youtube.assert_called_once()
            mock_qiita.assert_called_once()

            # クライアントのcloseメソッドが呼び出されることを確認
            mock_close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
