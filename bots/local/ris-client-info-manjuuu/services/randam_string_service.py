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
        処理概要:
            1. 変換結果を格納する配列を初期化する。
              - 入力文字列を1文字ずつ走査する。
              - 各文字のUnicodeコードポイントを取得する。
              - ひらがな範囲ならカタカナへ変換し、範囲外ならそのまま保持する。
            2. 変換後の文字配列を文字列として結合して返す。
        Args:
            text: 正規化対象の文字列。
        Returns:
            ひらがなをカタカナへ変換した文字列。
        """
        # 1. 変換結果を格納する配列を初期化する。
        result = []
        # - 入力文字列を1文字ずつ走査する。
        for char in text:
            # - 各文字のUnicodeコードポイントを取得する。
            code = ord(char)
            # - ひらがな範囲ならカタカナへ変換し、範囲外ならそのまま保持する。
            if 0x3041 <= code <= 0x3096:
                result.append(chr(code + 0x60))
            else:
                result.append(char)
        # 2. 変換後の文字配列を文字列として結合して返す。
        return "".join(result)

    def _count_mora(self, reading: str) -> int:
        """読み文字列からモーラ数を数える。
        小書きカナは直前の文字と一体で数えるため除外し、
        記号・空白もカウント対象外にする。
        処理概要:
            1. カウント除外ルールとカウンタを初期化する。
              - 小書きカナ集合を定義する。
              - 記号・空白集合を定義する。
              - モーラ数カウンタを0で初期化する。
            2. 読み文字列を1文字ずつ判定してモーラ数を積算する。
              - 除外対象の記号・空白はスキップする。
              - 小書きカナは単独モーラとして数えない。
              - それ以外の文字を1モーラとして加算する。
            3. 積算したモーラ数を返す。
        Args:
            reading: カタカナ読み文字列。
        Returns:
            推定モーラ数。
        """
        # 1. カウント除外ルールとカウンタを初期化する。
        # - 小書きカナ集合を定義する。
        small_kana = set("ャュョァィゥェォヮヵヶ")
        # - 記号・空白集合を定義する。
        skip_chars = set("・ 　\t\n\r")
        # - モーラ数カウンタを0で初期化する。
        mora = 0
        # 2. 読み文字列を1文字ずつ判定してモーラ数を積算する。
        for ch in reading:
            # - 除外対象の記号・空白はスキップする。
            if ch in skip_chars:
                continue
            # - 小書きカナは単独モーラとして数えない。
            if ch in small_kana:
                continue
            # - それ以外の文字を1モーラとして加算する。
            mora += 1
        # 3. 積算したモーラ数を返す。
        return mora

    def _is_hiragana_only(self, text: str) -> bool:
        """文字列がひらがなのみで構成されるかを判定する。
        処理概要:
            1. 判定対象が空文字でないことを確認する。
              - 各文字がひらがなUnicode範囲かを全件判定する。
            2. 条件を満たす場合のみ True を返す。
        Args:
            text: 判定対象の文字列。
        Returns:
            ひらがなのみで構成される場合は True。
        """
        # 1. 判定対象が空文字でないことを確認する。
        has_text = bool(text)
        # - 各文字がひらがなUnicode範囲かを全件判定する。
        is_all_hiragana = all(0x3041 <= ord(ch) <= 0x3096 for ch in text)
        # 2. 条件を満たす場合のみ True を返す。
        return has_text and is_all_hiragana

    def _contains_kanji(self, text: str) -> bool:
        """文字列に漢字が含まれるかを判定する。
        処理概要:
            1. 文字列を走査してCJK統合漢字・拡張A範囲への該当を確認する。
            2. 1文字でも該当すれば True を返し、なければ False を返す。
        Args:
            text: 判定対象の文字列。
        Returns:
            漢字を1文字以上含む場合は True。
        """
        # 1. 文字列を走査してCJK統合漢字・拡張A範囲への該当を確認する。
        contains_kanji = any(
            (0x4E00 <= ord(ch) <= 0x9FFF) or (0x3400 <= ord(ch) <= 0x4DBF)
            for ch in text
        )
        # 2. 1文字でも該当すれば True を返し、なければ False を返す。
        return contains_kanji

    def _mora_candidates(self, base_mora: int, has_kanji: bool):
        """トークンごとのモーラ候補を返す。
        処理概要:
            1. 漢字を含まない語は解析値をそのまま唯一候補として返す。
            2. 漢字を含む語は解析誤差吸収のため基準値±1を候補に含める。
              - 最小値は1に下限補正する。
              - 重複を除去して昇順で返す。
        Args:
            base_mora: 解析結果の基準モーラ数。
            has_kanji: 対象トークンに漢字を含むかどうか。
        Returns:
            許容するモーラ数の候補配列。
            漢字を含む場合は基準値の ±1 を含む。
        """
        # 1. 漢字を含まない語は解析値をそのまま唯一候補として返す。
        if not has_kanji:
            return [base_mora]
        # 2. 漢字を含む語は解析誤差吸収のため基準値±1を候補に含める。
        # - 最小値は1に下限補正し、重複除去と昇順化を行って返す。
        return sorted({max(1, base_mora - 1), base_mora, base_mora + 1})

    def _boundary_penalty(self, analyzed, index: int) -> float:
        """句切れ境界の自然さに応じたペナルティを返す。
        処理概要:
            1. 末尾トークンの場合は境界評価不要として0.0を返す。
            2. 現在トークンと次トークンの情報を取得する。
            3. 規則に従って境界ペナルティを加減算する。
              - 助詞直後の切れは自然なので減点（優遇）する。
              - 活用連接（動詞/形容詞 + 助動詞）途中の切れは加点（抑制）する。
              - 漢字語直後のひらがな語境界は加点する。
              - 接尾語前の切れは加点する。
            4. 累積ペナルティを返す。
        Args:
            analyzed: 形態素解析済みタプル配列。
            index: 境界判定対象となる現在トークンのインデックス。
        Returns:
            境界の不自然さを表すペナルティ値。
            値が小さいほど自然な分割として扱う。
        """
        # 1. 末尾トークンの場合は境界評価不要として0.0を返す。
        if index >= len(analyzed) - 1:
            return 0.0

        # 2. 現在トークンと次トークンの情報を取得する。
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

        # 3. 規則に従って境界ペナルティを加減算する。
        penalty = 0.0
        # - 助詞直後の切れは自然なので減点（優遇）する。
        if cur_pos1 == "助詞":
            penalty -= 1.0
        # - 活用連接（動詞/形容詞 + 助動詞）途中の切れは加点（抑制）する。
        if cur_pos1 in {"動詞", "形容詞"} and next_pos1 in {"助動詞"}:
            penalty += 2.0
        # - 漢字語直後のひらがな語境界は加点する。
        if cur_has_kanji and self._is_hiragana_only(next_surface):
            penalty += 1.5
        # - 接尾語前の切れは加点する。
        if next_pos2 == "接尾":
            penalty += 1.0

        # 4. 累積ペナルティを返す。
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
                処理概要:
                        1. すべての句を満たしたかを終端条件で判定する。
                            - 全トークン消費かつ句途中残りなしなら解を返す。
                            - それ以外は不成立として None を返す。
                        2. トークンを使い切った場合は探索失敗として None を返す。
                        3. 現在トークンに対するモーラ候補を列挙し、再帰探索する。
                            - 現在句の目標を超える候補は枝刈りする。
                            - 句がちょうど完成した場合は次の句へ進める。
                            - 未完成なら同じ句でモーラを積算して進める。
                            - 候補ごとにモーラ補正ペナルティを加算する。
                        4. 見つかった候補のうち最小スコア解を返す。
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
        # 1. すべての句を満たしたかを終端条件で判定する。
        if target_index == len(targets):
            # - 全トークン消費かつ句途中残りなしなら解を返す。
            if index == len(analyzed) and current_mora == 0 and not current_tokens:
                return score, lines
            # - それ以外は不成立として None を返す。
            return None

        # 2. トークンを使い切った場合は探索失敗として None を返す。
        if index >= len(analyzed):
            return None

        # 3. 現在トークンに対するモーラ候補を列挙し、再帰探索する。
        surface, _reading, base_mora, has_kanji, _pos1, _pos2 = analyzed[index]
        best = None
        for mora in self._mora_candidates(base_mora, has_kanji):
            next_mora = current_mora + mora
            # - 現在句の目標を超える候補は枝刈りする。
            if next_mora > targets[target_index]:
                continue

            next_tokens = current_tokens + [surface]
            # - 候補ごとにモーラ補正ペナルティを加算する。
            mora_penalty = 0.25 * abs(mora - base_mora)
            # - 句がちょうど完成した場合は次の句へ進める。
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

            # 4. 見つかった候補のうち最小スコア解を返す。
            if found is not None and (best is None or found[0] < best[0]):
                best = found

        return best

    def _is_same_user_channel_message(self, next_message, message) -> bool:
        """待受対象メッセージかを判定する。
        処理概要:
            1. 投稿者がコマンド実行者と一致するか判定する。
            2. 投稿先チャンネルがコマンド実行チャンネルと一致するか判定する。
            3. 投稿者がBotでないことを判定する。
            4. 上記3条件をすべて満たす場合のみ True を返す。
        Args:
            next_message: wait_for で受信したメッセージ。
            message: 575コマンド起動時の元メッセージ。

        Returns:
            同一ユーザーかつ同一チャンネルで、Bot投稿でない場合は True。
        """
        # 1. 投稿者がコマンド実行者と一致するか判定する。
        is_same_author = next_message.author == message.author
        # 2. 投稿先チャンネルがコマンド実行チャンネルと一致するか判定する。
        is_same_channel = next_message.channel == message.channel
        # 3. 投稿者がBotでないことを判定する。
        is_not_bot = not next_message.author.bot
        # 4. 上記3条件をすべて満たす場合のみ True を返す。
        return is_same_author and is_same_channel and is_not_bot

    def _analyze_mora(self, text: str):
        """入力テキストを形態素単位で読みとモーラ数に分解する
        処理概要:
            1. 解析結果格納配列を初期化し、Janomeで入力文を形態素へ分割する。
            2. 各形態素について読み・モーラ数・漢字有無・品詞情報を算出する。
              - 読みがない場合は表層形で代替する。
              - ひらがなをカタカナへ正規化してからモーラ数を計算する。
            3. 単独漢字 + 直後ひらがなを送り仮名として連結する。
              - 連結時は先頭語側の品詞情報を維持する。
            4. 最終的な解析タプル配列を返す。
        補足:
            - 本メソッドの戻り値は、5-7-5判定だけでなく境界スコア計算でも利用する。
        Args:
            text: 解析対象の日本語テキスト。
        Returns:
            (表層形, 読み, モーラ数, 漢字を含むかどうか, 品詞大分類, 品詞細分類1)
            のタプル配列。
        """
        # 1. 解析結果格納配列を初期化する。
        analyzed = []

        # - Janomeで入力文を形態素へ分割する。
        tokens = self._tokenizer.tokenize(text)
        # 2. 各形態素について読み・モーラ数・漢字有無・品詞情報を算出する。
        for token in tokens:
            pos = token.part_of_speech.split(",")
            pos1 = pos[0] if len(pos) > 0 else "*"
            pos2 = pos[1] if len(pos) > 1 else "*"
            # - 読みがない場合は表層形で代替する。
            reading = (
                token.reading
                if token.reading and token.reading != "*"
                else token.surface
            )
            # - ひらがなをカタカナへ正規化してからモーラ数を計算する。
            reading = self._hiragana_to_katakana(reading)
            mora = self._count_mora(reading)
            has_kanji = self._contains_kanji(token.surface)
            # 3. 単独漢字 + 直後ひらがなを送り仮名として連結する。
            if analyzed and self._is_hiragana_only(token.surface):
                (
                    prev_surface,
                    prev_reading,
                    prev_mora,
                    prev_has_kanji,
                    prev_pos1,
                    prev_pos2,
                ) = analyzed[-1]
                # - 連結時は先頭語側の品詞情報を維持する。
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
                # 4. 最終的な解析タプル配列を返す。
        return analyzed

    def _split_575(self, analyzed):
        """解析済みトークン列を 5-7-5 に分割できるか判定する
        処理概要:
            1. 目標拍を [5, 7, 5] として定義する。
            2. 深さ優先探索で分割候補を探索する。
              - 漢字語はモーラ補正候補を含めて探索する。
              - 境界ペナルティ込みで最小スコア解を選ぶ。
            3. 探索結果がある場合は3行配列を返し、なければ None を返す。
        補足:
            - 助詞の直後は自然な切れ目として優遇する。
            - 活用の途中（動詞/形容詞 + 助動詞）や
              漢字語直後のひらがな語境界は不自然になりやすいため抑制する。
            - 戻り値は最小スコア解のみで、同点候補の全列挙は行わない。
        Args:
            analyzed: (表層形, 読み, モーラ数, 漢字を含むかどうか, 品詞大分類,
                品詞細分類1) のタプル配列。
        Returns:
            5-7-5 に分割できた場合は3行の文字列配列。
            分割できない場合は None。
        """
        # 1. 目標拍を [5, 7, 5] として定義する。
        targets = [5, 7, 5]

        # 2. 深さ優先探索で分割候補を探索する。
        result = self._search_best_575(analyzed, targets, 0, 0, 0, [], [], 0.0)
        # 3. 探索結果がある場合は3行配列を返し、なければ None を返す。
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
            1. セッション開始メッセージを送信する。
              - 同一ユーザー/同一チャンネル/Bot除外の待受条件を生成する。
              - 待受ループを開始し、120分でタイムアウトさせる。
              - タイムアウト時は終了案内を送信して処理を終了する。
            2. 受信したテキストを取り出す。
              - 受信テキストが /manjuuu 退勤 の場合は終了メッセージを送信して処理を終了する。
              - 受信テキストを形態素解析し、5-7-5に分割可能か判定する。
              - 5-7-5形式の場合はタイトルと句を送信する。
              - 5-7-5形式かつ季語リストの語を含む場合は「あっぱれ！」を送信する。
              - 5-7-5形式でない場合は送信せず、次の入力待機に戻る。
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
        # 1. セッション開始メッセージを送信する。
        #    利用者へ終了コマンドを明示し、対話の開始状態を揃える。
        await message.channel.send(
            "夏井先生です。終了する時は /manjuuu 退勤 と送ってください。"
        )

        # - 同一ユーザー/同一チャンネル/Bot除外の待受条件を生成する。
        #      コマンド実行者の発言だけを対象にして、他ユーザー投稿の混入を防ぐ。
        check = partial(self._is_same_user_channel_message, message=message)

        # - 待受ループを開始し、120分でタイムアウトさせる。
        #      有効な句が来るまで継続して受信し、同一セッション内で再判定を繰り返す。
        while True:
            # - メッセージ待機を実行する。
            #      timeout=7200秒(120分)を超えた場合は例外へ遷移する。
            try:
                next_msg = await client.wait_for("message", check=check, timeout=7200.0)
            except asyncio.TimeoutError:
                # - タイムアウト時は終了案内を送信して処理を終了する。
                #      長時間放置セッションを閉じ、再実行を促す。
                await message.channel.send(
                    "夏井先生退勤。もう一度コマンドを実行してください。"
                )
                return

            # 2. 受信したテキストを取り出す。
            #    このテキストを終了判定と5-7-5判定の入力として使う。
            text = next_msg.content

            # - 受信テキストが /manjuuu 退勤 の場合は終了する。
            #      明示的終了コマンドを受けたら即座にセッションを閉じる。
            if text == "/manjuuu 退勤":
                await message.channel.send("夏井先生退勤。")
                return

            # - 受信テキストを形態素解析し、5-7-5に分割可能か判定する。
            #      analyzedは読み・モーラ数・品詞を持つ中間データ。
            analyzed = self._analyze_mora(text)
            split_lines = self._split_575(analyzed)
            if split_lines is not None:
                # - 5-7-5形式の場合はタイトルと句を送信する。
                #      split_linesは[上五, 中七, 下五]を想定し、半角スペースで連結して表示する。
                await message.channel.send("今日の一句")
                await message.channel.send(" ".join(split_lines))
                # - 季語リストの語を含む場合は「あっぱれ！」を送信する。
                #      句の内容に対する追加リアクションとして評価メッセージを返す。
                if any(kigo in text for kigo in self._APPARE_KIGO):
                    await message.channel.send("あっぱれ！")
            else:
                # - 5-7-5形式でない場合は送信せず次の入力待機に戻る。
                #      不成立入力は破棄し、同一セッションで再チャレンジを受け付ける。
                continue
