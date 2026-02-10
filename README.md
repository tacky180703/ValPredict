# ValPredict - VALORANT Match Prediction Discord Bot

VALORANTの試合情報をVLR.ggから自動取得し、Discord上で勝敗予想イベントを開催できるボットです。
大学のプロジェクトやコミュニティサーバーでの利用を想定し、Tier 1公式戦に特化した運用が可能です。

## 🚀 主な機能

- **自動試合投稿**: 1時間ごとにVLR.ggをチェックし、Tier 1の新規試合を自動でチャンネルへ投稿。
- **簡単ボタン予想**: メッセージに付与されたボタンを押すだけで、誰でも手軽に予想に参加。
- **自動結果通知**: 試合終了を検知すると、的中・ハズレの結果をユーザーにダイレクトメッセージ（DM）で通知。
- **ユーザー統計**: `/stats` コマンドで的中率や累計的中数、過去の全履歴を表示。
- **マルチサーバー対応**: 各サーバーごとに個別の投稿チャンネル設定が可能。

## 🛠️ 技術スタック

- **言語**: Python 3.9+
- **ライブラリ**: `discord.py` (v2.x), `requests`, `python-dotenv`
- **データベース**: SQLite3 (サーバー別・試合別の投稿管理を最適化)
- **API**: VLR.gg API (vlrggapi.vercel.app)
- **動作環境**: macOS (MacBook Air 2020 動作確認済) / Linux

## 📂 プロジェクト構成

```text
ValPredict/
├── main.py              # ボットの起動・Cog読み込み
├── .env                 # Discordトークン管理
├── data/
│   └── predictions.db   # データベースファイル（自動生成）
├── cogs/
│   ├── poster.py        # 試合の自動投稿・Tier 1フィルタリング
│   ├── results.py       # 試合結果の監視・DM通知・DB更新
│   └── user.py          # ユーザーコマンド (/stats, /results, /upcoming)
└── utils/
    ├── db_manager.py    # SQLite操作ロジック
    ├── vlr_api.py       # VLR.gg APIとの通信
    └── helpers.py       # タイムスタンプやカラー設定の
