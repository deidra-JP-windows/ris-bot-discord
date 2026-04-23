import asyncio
import importlib
import os
import sys
import unittest
from unittest.mock import AsyncMock, Mock, patch

sys.path.append(
    os.path.join(
        os.path.dirname(__file__), "../../../../bots/local/ris-client-info-manjuuu"
    )
)


with patch("discord.Client.run", return_value=None):
    main = importlib.import_module("main")


class TestMain(unittest.TestCase):

    def setUp(self):
        intents = main.discord.Intents.default()
        intents.message_content = True
        self.client = main.MyClient(intents=intents)

        self.client.randam_string_service = Mock()
        self.client.randam_string_service.send_health_check = AsyncMock()
        self.client.randam_string_service.send_greeting = AsyncMock()
        self.client.randam_string_service.send_random_chat_line = AsyncMock()
        self.client.randam_string_service.send_random_string = AsyncMock()
        self.client.randam_string_service.send_random_game_title = AsyncMock()
        self.client.randam_string_service.send_575_text = AsyncMock()

    def test_on_message_health_check(self):
        """ヘルスチェックコマンドで正しいサービスが呼ばれることを確認する。"""
        message = Mock(author=object(), content="/manjuuu ヘルスチェック")

        asyncio.run(self.client.on_message(message))

        self.client.randam_string_service.send_health_check.assert_awaited_once_with(
            message
        )

    @patch("main.random.random", return_value=0.01)
    def test_on_message_random_string_uses_chat_history_branch(self, _mock_random):
        """ランダム文字列コマンドが5%分岐で履歴取得側を呼ぶことを確認する。"""
        message = Mock(author=object(), content="/manjuuu ランダム文字列")

        asyncio.run(self.client.on_message(message))

        self.client.randam_string_service.send_random_chat_line.assert_awaited_once_with(
            message
        )
        self.client.randam_string_service.send_random_string.assert_not_awaited()

    def test_on_message_575_calls_service_with_client(self):
        """575コマンドでサービスへ message と client が渡されることを確認する。"""
        message = Mock(author=object(), content="/manjuuu 575")

        asyncio.run(self.client.on_message(message))

        self.client.randam_string_service.send_575_text.assert_awaited_once_with(
            message, self.client
        )


if __name__ == "__main__":
    unittest.main()
