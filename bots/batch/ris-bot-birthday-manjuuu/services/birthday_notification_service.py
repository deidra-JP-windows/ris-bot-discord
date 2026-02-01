import re
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta


class BirthdayNotificationService:

    def __init__(self):
        load_dotenv()
        # Repository secretsから取得する環境変数名に統一
        self.READ_BIRTHDAY_CHANNEL_ID = int(os.getenv("READ_BIRTHDAY_CHANNEL_ID"))
        self.SEND_GENERAL_CHANNEL_ID = int(os.getenv("SEND_GENERAL_CHANNEL_ID"))
        # 対応する日付フォーマットをリストで管理
        self.DATE_FORMATS = [
            "%m月%d日",  # 9月6日
            "%m/%d",  # 09/06
            "%m-%d",  # 09-06
            "%m.%d",  # 09.06
            "%Y-%m-%d",  # 2025-09-06
            "%Y/%m/%d",  # 2025/09/06
            "%m/%d/%Y",  # 09/06/2025
            "%d-%m-%Y",  # 06-09-2025
            "%Y年%m月%d日",  # 2025年9月6日
        ]

    def _convert_kansuji_to_number(self, kanji_str: str) -> int:
        """
        漢数字の文字列（一から三十一まで）を整数に変換するヘルパー関数
        Args:
            kanji_str: 変換したい漢数字の文字列
        Returns:
            対応する整数値
        """
        kanji_map = {
            "一": 1,
            "二": 2,
            "三": 3,
            "四": 4,
            "五": 5,
            "六": 6,
            "七": 7,
            "八": 8,
            "九": 9,
            "十": 10,
        }

        # 「二十三」や「三十一」のような形式を処理
        if "十" in kanji_str:
            if kanji_str == "十":
                return 10
            parts = kanji_str.split("十")
            tens_digit = 1
            if parts[0]:
                tens_digit = kanji_map.get(parts[0])
            ones_digit = 0
            if len(parts) > 1 and parts[1]:
                ones_digit = kanji_map.get(parts[1])
            return tens_digit * 10 + ones_digit
        else:
            # 「九」のような一桁の形式を処理
            return kanji_map.get(kanji_str, 0)

    def _preprocess_kansuji_date(self, date_string: str) -> str:
        """
        漢数字の日付（例: 九月六日）をアラビア数字（例: 9月6日）に変換する
        Args:
            date_string: 変換したい日付文字列
        Returns:
            アラビア数字に変換した日付文字列
        """
        # 正規表現で「(漢数字)月(漢数字)日」のパターンにマッチするか確認
        match = re.fullmatch(
            r"([一二三四五六七八九十]+)月([一二三四五六七八九十]+)日", date_string
        )
        if match:
            kanji_month = match.group(1)
            kanji_day = match.group(2)
            # 漢数字を整数に変換
            month_num = self._convert_kansuji_to_number(kanji_month)
            day_num = self._convert_kansuji_to_number(kanji_day)
            if month_num and day_num:
                # 「9月6日」のようなdatetimeが解析できる形式の文字列を再構築して返す
                return f"{month_num}月{day_num}日"
        # マッチしない場合は、元の文字列をそのまま返す
        return date_string

    def _day_formatter(self, date_string: str) -> str | None:
        """
        様々なフォーマットの日付文字列を 'MM/DD' 形式に変換する関数。
        漢数字のフォーマットにも対応。
        Args:
            date_string: 変換したい日付文字列。
        Returns:
            'MM/DD' 形式の文字列。どのフォーマットにも一致しない場合は None。
        """
        # 最初に漢数字のフォーマットを前処理する
        processed_string = self._preprocess_kansuji_date(date_string)
        for fmt in self.DATE_FORMATS:
            try:
                # 処理後の文字列で照合を試みる
                # 年を含まないフォーマットの場合、うるう年(2024年)を補ってチェック
                if "%Y" not in fmt and "%y" not in fmt:
                    # 日付文字列とフォーマットの両方に年を追加
                    temp_date_str = f"{processed_string} 2024"
                    temp_fmt = f"{fmt} %Y"
                    dt_object = datetime.strptime(temp_date_str, temp_fmt)
                else:
                    # 年を含むフォーマットはそのままチェック
                    dt_object = datetime.strptime(processed_string, fmt)
                return dt_object.strftime("%m/%d")
            except ValueError:
                continue
        return None

    async def birthday_notification_main(self, client):
        """
        Discordクライアントから誕生日メッセージを取得し、
        本日が誕生日のユーザーがいれば通知を送信するメイン関数
        Args:
            client: Discordのクライアントインスタンス
        """
        print("start: birthday_notification_main")
        birthdays = {}
        # 指定チャンネルの過去メッセージを全て取得
        async for message in client.get_channel(self.READ_BIRTHDAY_CHANNEL_ID).history(
            limit=None
        ):
            # Bot自身のメッセージは除外
            if message.author != client.user:
                date = self._day_formatter(message.content)
                if date is not None:
                    birthdays.setdefault(date, set())
                    birthdays[date].add(message.author.global_name)
        # 現在の日付（JST）を取得
        today = (datetime.utcnow() + timedelta(hours=9)).strftime("%m/%d")
        members = birthdays.get(today)
        if members:
            # 本日が誕生日のメンバーがいれば通知を送信
            await client.get_channel(self.SEND_GENERAL_CHANNEL_ID).send(
                f'@everyone\n今日は{"と".join([f" {mem}さん " for mem in members])}'
                f"の誕生日です！！！皆でお祝いしましょう！！！"
            )
        print("end: birthday_notification_main")
