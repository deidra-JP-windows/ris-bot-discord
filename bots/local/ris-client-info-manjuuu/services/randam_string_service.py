import asyncio
from functools import partial
from datetime import datetime, timedelta
import random
import string
from janome.tokenizer import Tokenizer


class RandamStringService:

    _tokenizer = Tokenizer()
    _APPARE_KIGO = (
        # 春
        "寒椿",
        "梅",
        "桜",
        "霞",
        "朧",
        # 夏
        "蛍",
        "紫陽花",
        "夕立",
        "天の川",
        "青嵐",
        # 秋
        "月見",
        "紅葉",
        "霧",
        "時雨",
        "雁",
        # 冬
        "雪",
        "霜",
        "氷柱",
        "木枯らし",
        "柚子湯",
        # LOL
        "LOL",
        "MID",
        "ミッド",
        "ADC",
        "アサシン",
        "SUP",
        "サポート",
        "JUNGLE",
        "ジャングル",
        "TOP",
        "トップ",
        "PENTAKILL",
        "ペンタキル",
    )

    def _hiragana_to_katakana(self, text: str) -> str:
        """ひらがなをカタカナへ正規化する。
        Args:
            text: 正規化対象の文字列。
        Returns:
            ひらがなをカタカナへ変換した文字列。
        """
        result = []
        for char in text:
            code = ord(char)
            # Convert Hiragana to Katakana by Unicode block offset.
            if 0x3041 <= code <= 0x3096:
                result.append(chr(code + 0x60))
            else:
                result.append(char)
        return "".join(result)

    def _count_mora(self, reading: str) -> int:
        """読み文字列からモーラ数を数える。
        小書きカナは直前の文字と一体で数えるため除外し、
        記号・空白もカウント対象外にする。
        Args:
            reading: カタカナ読み文字列。
        Returns:
            推定モーラ数。
        """
        small_kana = set("ャュョァィゥェォヮヵヶ")
        skip_chars = set("・ 　\t\n\r")
        mora = 0
        for ch in reading:
            if ch in skip_chars:
                continue
            if ch in small_kana:
                continue
            mora += 1
        return mora

    def _is_hiragana_only(self, text: str) -> bool:
        """文字列がひらがなのみで構成されるかを判定する。
        Args:
            text: 判定対象の文字列。
        Returns:
            ひらがなのみで構成される場合は True。
        """
        return bool(text) and all(0x3041 <= ord(ch) <= 0x3096 for ch in text)

    def _contains_kanji(self, text: str) -> bool:
        """文字列に漢字が含まれるかを判定する。
        Args:
            text: 判定対象の文字列。
        Returns:
            漢字を1文字以上含む場合は True。
        """
        return any(
            (0x4E00 <= ord(ch) <= 0x9FFF) or (0x3400 <= ord(ch) <= 0x4DBF)
            for ch in text
        )

    def _mora_candidates(self, base_mora: int, has_kanji: bool):
        """トークンごとのモーラ候補を返す。
        Args:
            base_mora: 解析結果の基準モーラ数。
            has_kanji: 対象トークンに漢字を含むかどうか。
        Returns:
            許容するモーラ数の候補配列。
            漢字を含む場合は基準値の ±1 を含む。
        """
        if not has_kanji:
            return [base_mora]
        return sorted({max(1, base_mora - 1), base_mora, base_mora + 1})

    def _boundary_penalty(self, analyzed, index: int) -> float:
        """句切れ境界の自然さに応じたペナルティを返す。
        Args:
            analyzed: 形態素解析済みタプル配列。
            index: 境界判定対象となる現在トークンのインデックス。
        Returns:
            境界の不自然さを表すペナルティ値。
            値が小さいほど自然な分割として扱う。
        """
        if index >= len(analyzed) - 1:
            return 0.0

        cur_surface, _cur_reading, _cur_mora, cur_has_kanji, cur_pos1, _cur_pos2 = (
            analyzed[index]
        )
        (
            next_surface,
            _next_reading,
            _next_mora,
            _next_has_kanji,
            next_pos1,
            next_pos2,
        ) = analyzed[index + 1]

        penalty = 0.0
        # 助詞の直後は切れ目として自然になりやすいため優遇。
        if cur_pos1 == "助詞":
            penalty -= 1.0
        # 活用のつながりを途中で切るのは不自然なため抑制。
        if cur_pos1 in {"動詞", "形容詞"} and next_pos1 in {"助動詞"}:
            penalty += 2.0
        if cur_has_kanji and self._is_hiragana_only(next_surface):
            penalty += 1.5
        if next_pos2 == "接尾":
            penalty += 1.0

        return penalty

    def _search_best_575(
        self,
        analyzed,
        targets,
        index,
        target_index,
        current_mora,
        current_tokens,
        lines,
        score,
    ):
        """5-7-5 分割候補を探索し、最小ペナルティ解を返す。
        Args:
            analyzed: 形態素解析済みタプル配列。
            targets: 目標モーラ配列（例: [5, 7, 5]）。
            index: 現在処理中のトークンインデックス。
            target_index: 現在処理中の句（上五/中七/下五）のインデックス。
            current_mora: 現在の句で積算したモーラ数。
            current_tokens: 現在の句に含めている表層形配列。
            lines: 確定済みの句配列。
            score: 現時点までの累積ペナルティ。
        Returns:
            解が存在する場合は (score, lines) を返す。
            解がない場合は None を返す。
        """
        if target_index == len(targets):
            if index == len(analyzed) and current_mora == 0 and not current_tokens:
                return score, lines
            return None

        if index >= len(analyzed):
            return None

        surface, _reading, base_mora, has_kanji, _pos1, _pos2 = analyzed[index]
        best = None
        for mora in self._mora_candidates(base_mora, has_kanji):
            next_mora = current_mora + mora
            if next_mora > targets[target_index]:
                continue

            next_tokens = current_tokens + [surface]
            mora_penalty = 0.25 * abs(mora - base_mora)
            if next_mora == targets[target_index]:
                found = self._search_best_575(
                    analyzed,
                    targets,
                    index + 1,
                    target_index + 1,
                    0,
                    [],
                    lines + ["".join(next_tokens)],
                    score + self._boundary_penalty(analyzed, index) + mora_penalty,
                )
            else:
                found = self._search_best_575(
                    analyzed,
                    targets,
                    index + 1,
                    target_index,
                    next_mora,
                    next_tokens,
                    lines,
                    score + mora_penalty,
                )

            if found is not None and (best is None or found[0] < best[0]):
                best = found

        return best

    def _is_same_user_channel_message(self, next_message, message) -> bool:
        """待受対象メッセージかを判定する。
        Args:
            next_message: wait_for で受信したメッセージ。
            message: 575コマンド起動時の元メッセージ。

        Returns:
            同一ユーザーかつ同一チャンネルで、Bot投稿でない場合は True。
        """
        return (
            next_message.author == message.author
            and next_message.channel == message.channel
            and not next_message.author.bot
        )

    def _analyze_mora(self, text: str):
        """入力テキストを形態素単位で読みとモーラ数に分解する
        処理概要:
                1. Janomeで入力文を形態素へ分割する。
                2. 各形態素について以下を算出する。
                    - 読み（読めない場合は表層形で代替）
                    - モーラ数
                    - 漢字を含むかどうか
                    - 品詞情報（大分類、細分類1）
                3. 「単独漢字 + 直後ひらがな」の場合は送り仮名として連結し、
                     不自然な句切れを減らす
        補足:
                - 本メソッドの戻り値は、5-7-5判定だけでなく
                    境界スコア計算でも利用する。
                - 連結時は品詞情報を先頭語側で保持する
        Args:
            text: 解析対象の日本語テキスト。
        Returns:
            (表層形, 読み, モーラ数, 漢字を含むかどうか, 品詞大分類, 品詞細分類1)
            のタプル配列。
        """
        analyzed = []

        tokens = self._tokenizer.tokenize(text)
        for token in tokens:
            pos = token.part_of_speech.split(",")
            pos1 = pos[0] if len(pos) > 0 else "*"
            pos2 = pos[1] if len(pos) > 1 else "*"
            reading = (
                token.reading
                if token.reading and token.reading != "*"
                else token.surface
            )
            reading = self._hiragana_to_katakana(reading)
            mora = self._count_mora(reading)
            has_kanji = self._contains_kanji(token.surface)
            # Janomeが「漢字語 + 送り仮名」を分割した場合は結合して不自然な改行を避ける。
            if analyzed and self._is_hiragana_only(token.surface):
                (
                    prev_surface,
                    prev_reading,
                    prev_mora,
                    prev_has_kanji,
                    prev_pos1,
                    prev_pos2,
                ) = analyzed[-1]
                if prev_has_kanji and len(prev_surface) == 1:
                    analyzed[-1] = (
                        prev_surface + token.surface,
                        prev_reading + reading,
                        prev_mora + mora,
                        True,
                        prev_pos1,
                        prev_pos2,
                    )
                    continue

            analyzed.append((token.surface, reading, mora, has_kanji, pos1, pos2))
        return analyzed

    def _split_575(self, analyzed):
        """解析済みトークン列を 5-7-5 に分割できるか判定する
        処理概要:
                1. 目標拍を [5, 7, 5] として深さ優先探索を行う。
                2. 各トークンのモーラ候補を生成する。
                    - 漢字を含まない語: 基本モーラのみ
                    - 漢字を含む語: 基本モーラの ±1 を候補として許容
                3. 候補ごとに境界ペナルティを加算し、
                     最終的に最小スコアの分割案を採用する
        補足:
                - 助詞の直後は自然な切れ目として優遇する。
                - 活用の途中（動詞/形容詞 + 助動詞）や
                    漢字語直後のひらがな語境界は不自然になりやすいため抑制する。
                - 戻り値は最小スコア解のみで、同点候補の全列挙は行わない
        Args:
            analyzed: (表層形, 読み, モーラ数, 漢字を含むかどうか, 品詞大分類,
                品詞細分類1) のタプル配列。
        Returns:
            5-7-5 に分割できた場合は3行の文字列配列。
            分割できない場合は None。
        """
        targets = [5, 7, 5]

        result = self._search_best_575(analyzed, targets, 0, 0, 0, [], [], 0.0)
        return result[1] if result is not None else None

    async def send_random_string(self, message) -> None:
        """ランダムな文字列を送信するサービスメソッド
        処理概要:
            1. アルファベットと数字からランダムに12文字を選択
            2. 生成した文字列をチャンネルに送信
        Args:
            message: Discordのメッセージオブジェクト
        Returns:
            None
        """
        # 1. アルファベットと数字からランダムに12文字を選択
        rand_str = "".join(random.choices(string.ascii_letters + string.digits, k=12))
        # 2. 生成した文字列をチャンネルに送信
        await message.channel.send(rand_str)

    async def send_health_check(self, message) -> None:
        """ヘルスチェックメッセージを送信するサービスメソッド
        処理概要:
            1. ヘルスチェックメッセージ「生存」をチャンネルに送信
        Args:
            message: Discordのメッセージオブジェクト
        Returns:
            None
        """
        # 1. ヘルスチェックメッセージ「生存」をチャンネルに送信
        await message.channel.send("生存")

    async def send_greeting(self, message) -> None:
        """挨拶メッセージを送信するサービスメソッド
        処理概要:
            1. 挨拶メッセージ「おはようございます！」をチャンネルに送信
        Args:
            message: Discordのメッセージオブジェクト
        Returns:
            None
        """
        # 1. 挨拶メッセージ「おはようございます！」をチャンネルに送信
        await message.channel.send("おはようございます！")

    async def send_random_chat_line(self, message) -> None:
        """ランダムなチャット履歴を送信するサービスメソッド
        処理概要:
            1. 一週間分のチャット履歴を取得(最大500件)
            2. 取得したメッセージからランダムに1行を選択
            3. 選択したメッセージをチャンネルに送信
        Args:
            message: Discordのメッセージオブジェクト
        Returns:
            None
        """
        # 1. 一週間分のチャット履歴を取得(最大500件)
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        messages = []
        async for msg in message.channel.history(after=week_ago, limit=500):
            if msg.content:
                messages.append(msg.content)
        # 2. 取得したメッセージからランダムに1行を選択
        # 3. 選択したメッセージをチャンネルに送信
        if messages:
            await message.channel.send(random.choice(messages))

    async def send_random_game_title(self, message) -> None:
        """ランダムなゲームタイトルを送信するサービスメソッド
        処理概要:
            1. ゲームタイトルのリストからランダムに1つ選択
            2. 選択したゲームタイトルをチャンネルに送信
        Args:
            message: Discordのメッセージオブジェクト
        Returns:
            None
        """
        # 1. ゲームタイトルのリストからランダムに1つ選択
        game_titles = [
            "Among Us",
            "Minecraft",
            "League of Legends",
            "VRChat",
            "Geo Guessr",
            "Human: Fall Flat",
            "麻雀",
            "Apex Legends",
            "Chill雑談",
            "Valorant",
        ]
        random_title = random.choice(game_titles)
        # 2. 選択したゲームタイトルをチャンネルに送信
        await message.channel.send(f"今日のおすすめゲームタイトル: {random_title}")

    async def send_575_text(self, message, client) -> None:
        """5-7-5形式のテキストを生成して送信するサービスメソッド
        処理概要:
            1. コマンド実行後、同一ユーザー/同一チャンネルの発言を待機
                - メッセージ待機のタイムアウトは120分
            2. 受信したテキストを処理
              - 受信テキストが /manjuuu 退勤 の場合は終了
              - モーラ数を解析し、5-7-5として分割できるかを判定
                - 5-7-5形式であれば、音節を半角スペースで区切りチャンネルに送信
                - 一部の文字を含んでいる場合、改行区切りで「あっぱれ！」を付与してチャンネルに送信
                - 5-7-5形式でなければ次のテキストを待機
        補足:
            - モーラ数の解析には Janome を使用し、ひらがなをカタカナに正規化してからモーラ数を数える
            - 小書きカナは直前の文字と一体で数えるため除外し、記号・空白もカウント対象外にする
            - 5-7-5形式の判定は、モーラ数の合計が5-7-5になっているかを確認することで行う
            - モーラ数とは日本語の「音の拍（はく）」の数
              - 例えば「カタカナ」は「カ（1）タ（1）カ（1）ナ（1）」の4モーラ
              - 「きゃ」は「きゃ（1）」の1モーラ、「ん」は「ん（1）」の1モーラ
        Args:
            message: Discordのメッセージオブジェクト
        Print:
            string: メッセージ
        Returns:
            None
        """
        await message.channel.send(
            "夏井先生です。終了する時は /manjuuu 退勤 と送ってください。"
        )

        check = partial(self._is_same_user_channel_message, message=message)

        # コマンド実行後、同一ユーザー/同一チャンネルの発言を待機
        while True:
            # メッセージ待機のタイムアウトは120分
            try:
                next_msg = await client.wait_for("message", check=check, timeout=7200.0)
            except asyncio.TimeoutError:
                await message.channel.send(
                    "夏井先生退勤。もう一度コマンドを実行してください。"
                )
                return

            # 受信したテキストを処理
            text = next_msg.content

            # 受信テキストが /manjuuu 退勤 の場合は終了
            if text == "/manjuuu 退勤":
                await message.channel.send("夏井先生退勤。")
                return

            # モーラ数を解析し、5-7-5として分割できるかを判定
            analyzed = self._analyze_mora(text)
            split_lines = self._split_575(analyzed)
            if split_lines is not None:
                # 5-7-5形式であれば、音節を半角スペースで区切りチャンネルに送信
                await message.channel.send("今日の一句")
                await message.channel.send(" ".join(split_lines))
                if any(kigo in text for kigo in self._APPARE_KIGO):
                    await message.channel.send("あっぱれ！")
            else:
                continue
