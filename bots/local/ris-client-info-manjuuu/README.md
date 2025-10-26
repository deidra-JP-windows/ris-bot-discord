# ris-client-info-manjuuu クライアント概要

このクライアントは Discord サーバー上で動作する Python 製のBotです。

## 主な機能
- `/manjuuu ヘルスチェック` : Botの稼働確認メッセージを返します。
- `/manjuuu こんにちは` : 挨拶メッセージを返します。
- `/manjuuu ランダム文字列` : 12文字のランダムな英数字文字列を返します。
    - 5%の確率で、過去1週間分のチャットからランダムな一行を返します。

## 技術構成
- discord.py
- Python 3.12
- .envによるトークン管理

## 実装ファイル
- `main.py` : クライアント本体
- `services/randam_string_service.py` : ランダム文字列・チャット取得等のサービス

# ローカル動作確認
```
export DISCORD_BOT_TOKEN=${開発管理者から取得}
python main.py
```
---
質問や機能追加要望はリポジトリ管理者までご連絡ください。