import re
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta


class BirthdayNotificationService:

    def __init__(self):
        """
        処理概要:
            1. 環境変数を読み込む
            2. チャンネルIDと日付フォーマットを初期化する

        補足:
            1. READ_BIRTHDAY_CHANNEL_ID と SEND_GENERAL_CHANNEL_ID を環境変数から取得する
            2. 年あり/年なしの複数フォーマットを受け付ける

        Args:
            None

        Returns:
            None
        """
        # 1. 環境変数を読み込む
        load_dotenv()
        # 2. チャンネルIDと日付フォーマットを初期化する
        self.READ_BIRTHDAY_CHANNEL_ID = int(os.getenv("READ_BIRTHDAY_CHANNEL_ID"))
        self.SEND_GENERAL_CHANNEL_ID = int(os.getenv("SEND_GENERAL_CHANNEL_ID"))
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
        処理概要:
            1. 漢数字のマッピング辞書を参照
            2. 「十」を含む場合は十の位と一の位を分けて処理
            3. 一桁の場合は辞書から直接変換

        Args:
            kanji_str (str): 変換したい漢数字の文字列(一から三十一まで)

        Returns:
            int: 変換された整数値
        """
        # 1. 漢数字のマッピング辞書を参照
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

        # 2. 「十」を含む場合は十の位と一の位を分けて処理
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
            # 3. 一桁の場合は辞書から直接変換
            return kanji_map.get(kanji_str, 0)

    def _preprocess_kansuji_date(self, date_string: str) -> str:
        """
        処理概要:
            1. 正規表現で「(漢数字)月(漢数字)日」のパターンにマッチするか確認
            2. マッチした場合、月と日をそれぞれ整数に変換
            3. 「MM月DD日」形式の文字列を再構築して返す

        Args:
            date_string (str): 変換したい日付文字列(例: 九月六日)

        Returns:
            str: アラビア数字に変換した日付文字列(例: 9月6日)、マッチしない場合は元の文字列
        """
        # 1. 正規表現で「(漢数字)月(漢数字)日」のパターンにマッチするか確認
        match = re.fullmatch(
            r"([一二三四五六七八九十]+)月([一二三四五六七八九十]+)日", date_string
        )
        if match:
            kanji_month = match.group(1)
            kanji_day = match.group(2)
            # 2. マッチした場合、月と日をそれぞれ整数に変換
            month_num = self._convert_kansuji_to_number(kanji_month)
            day_num = self._convert_kansuji_to_number(kanji_day)
            if month_num and day_num:
                # 3. 「MM月DD日」形式の文字列を再構築して返す
                return f"{month_num}月{day_num}日"
        return date_string

    def _day_formatter(self, date_string: str) -> str | None:
        """
        処理概要:
            1. 漢数字のフォーマットを前処理してアラビア数字に変換
            2. 定義された日付フォーマットリストを順に試行
            3. マッチしたフォーマットで日付をパースし 'MM/DD' 形式に変換

        条件:
            1. 年を含まないフォーマットは 2024 年を補完して妥当性を確認する

        Args:
            date_string (str): 変換したい日付文字列(様々なフォーマットに対応)

        Returns:
            str | None: 'MM/DD' 形式の文字列。どのフォーマットにも一致しない場合は None
        """
        # 1. 漢数字のフォーマットを前処理してアラビア数字に変換
        processed_string = self._preprocess_kansuji_date(date_string)
        # 2. 定義された日付フォーマットリストを順に試行
        for fmt in self.DATE_FORMATS:
            try:
                if "%Y" not in fmt and "%y" not in fmt:
                    temp_date_str = f"{processed_string} 2024"
                    temp_fmt = f"{fmt} %Y"
                    dt_object = datetime.strptime(temp_date_str, temp_fmt)
                else:
                    dt_object = datetime.strptime(processed_string, fmt)
                # 3. マッチしたフォーマットで日付をパースし 'MM/DD' 形式に変換
                return dt_object.strftime("%m/%d")
            except ValueError:
                continue
        return None

    async def birthday_notification_main(self, client):
        """
        処理概要:
            1. 指定チャンネルから過去メッセージを全て取得
            2. メッセージ内容を日付フォーマットに変換し、誕生日辞書を作成
            3. 本日の日付(JST)と照合
            4. 本日が誕生日のメンバーがいれば通知メッセージを送信

        Args:
            client: Discordのクライアントインスタンス

        Returns:
            None
        """
        print("start: birthday_notification_main")
        birthdays = {}
        # 1. 指定チャンネルから過去メッセージを全て取得
        async for message in client.get_channel(self.READ_BIRTHDAY_CHANNEL_ID).history(
            limit=None
        ):
            if message.author != client.user:
                # 2. メッセージ内容を日付フォーマットに変換し、誕生日辞書を作成
                date = self._day_formatter(message.content)
                if date is not None:
                    birthdays.setdefault(date, set())
                    birthdays[date].add(message.author.global_name)
        # 3. 本日の日付(JST)と照合
        today = (datetime.utcnow() + timedelta(hours=9)).strftime("%m/%d")
        members = birthdays.get(today)
        if members:
            # 4. 本日が誕生日のメンバーがいれば通知メッセージを送信
            await client.get_channel(self.SEND_GENERAL_CHANNEL_ID).send(
                f'@everyone\n今日は{"と".join([f" {mem}さん " for mem in members])}'
                f"の誕生日です！！！皆でお祝いしましょう！！！"
            )
        print("end: birthday_notification_main")
