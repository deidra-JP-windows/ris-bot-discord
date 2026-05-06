---
name: discord-bot
description: "このリポジトリのDiscord Bot（Python）を拡張するときに使うスキル。on_messageコマンド追加、サービス分割、環境変数設定、バッチBot実行フロー、テスト観点の整理で使う。"
argument-hint: "やりたい変更（例: コマンド追加、通知処理追加、テスト追加）を指定してください"
user-invocable: true
---

# Discord Bot実装スキル

## このスキルでできること
- ローカルBotへの新規コマンド追加（`on_message`分岐の設計）
- サービス層（`services/`）への責務分離
- バッチBot（`on_ready`起動型）の処理追加
- `.env`依存設定（`DISCORD_BOT_TOKEN`）の確認
- 既存テスト構成に沿ったテスト観点の提案

## 使うタイミング
- `/manjuuu ...` コマンドを追加したいとき
- 誕生日通知やニュース投稿などの定期・バッチ処理を追加したいとき
- Botロジックを `main.py` から `services/` へ分離したいとき
- 変更後にどこまでテストすべきか整理したいとき

## 進め方
1. 変更対象がローカルBotかバッチBotかを特定する。
2. `main.py` のイベントハンドラ変更点を定義する。
3. 具体ロジックを `services/` へ実装し、`main.py` は呼び出しに限定する。
4. 既存コマンドとの競合やメッセージ条件分岐を確認する。
5. 必要なテスト（ユニット/動作確認）を追加または更新する。

## 参照メモ
- [Discord Bot開発メモ](./references/DiscordBot開発メモ.md)
