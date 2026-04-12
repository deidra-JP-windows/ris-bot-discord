# Discord Bot開発メモ

## プロジェクト構成
- ローカルBot: `bots/local/ris-client-info-manjuuu/`
- バッチBot: `bots/batch/ris-bot-birthday-manjuuu/`
- テスト: `bots/tests/`

## ローカルBotの基本パターン
- `main.py` で `discord.Client` を継承したクラスを定義する。
- `on_message` で文字列一致によるコマンド分岐を行う。
- 実処理は `services/` 配下のクラスへ委譲する。

## バッチBotの基本パターン
- `on_ready` で必要なサービスを初期化する。
- 各サービスのメイン処理を `await` で順に実行する。
- 実行後に `client.close()` で終了する。

## 変更時のチェックポイント
1. `DISCORD_BOT_TOKEN` を `.env` から取得しているか。
2. Bot自身の投稿を無視する分岐があるか（`message.author == self.user`）。
3. コマンド文字列が既存と衝突していないか。
4. I/O処理は `services/` 側へ分離されているか。
5. 非同期処理の `await` 漏れがないか。

## テスト観点
- コマンド入力ごとの分岐が期待どおりか。
- 例外時にBotが停止しない設計になっているか。
- ランダム分岐（確率処理）をテスト時に制御できるか。
