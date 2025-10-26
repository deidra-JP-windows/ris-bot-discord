<Goals>
必ず日本語で出力
要約・解説・関連性を含めて出力
</Goals>
<ProjectLayout>
- バックエンド
  - 3層アーキテクチャ(Controller→Service→Repository(Repository+Model))を必ず採用
    - main.* ファイルをエントリポイントとし、controller.* に渡す構成を採用
      - バッチやツールなどServiceなどで解決する場合はエントリポイント+Serviceのみ
    - 必ずインターフェイスとクラスを利用
      - ～サービスのクラス
    - 必ず型定義
- フロントエンド
  - typescript を使用し、UIコンポーネント中心のシンプルなSPA構成を採用
    - index.ts がエントリポイント
    - 必ず型定義
</ProjectLayout>
<Code>
- 一般的な高級言語
  - エントリポイントの関数を除き、グローバル領域にはクラス定義とimport文のみを入れる
- ファイルの末尾には必ず改行を入れる
- import文、クラス、関数の間に2行の改行を入れる
</Code>
<Function>
- 関数名直下での引数・リターン付きのコメントを入れる
</Function>
