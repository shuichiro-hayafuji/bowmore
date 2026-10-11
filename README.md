# Bowmore

iPhone向け英会話学習アプリの開発準備用リポジトリです。現在は要件・100件のメニュー案・ローカル抽選処理までで、iPhoneアプリは未実装です。

## ローカル確認

Python 3の標準ライブラリだけで実行できます。

```sh
python3 -m unittest discover -s tests -v
python3 tools/preview_learning_pattern.py --check
python3 tools/preview_learning_pattern.py --profile owner --seed 42
python3 tools/preview_learning_pattern.py --stage express_opinion --seed 42
```

`bowmore.learning.select_for_stages` は利用者の現在の難易度を受け取り、該当するメニューから均等に抽選します。能力の測定・自動判定はしません。本人用・友人用の区分は初期設定のプレビューです。直前メニューの除外・再抽選・苦手への重み付けは未合意のため追加していません。

メニューの時間配分・英語例文・評価条件は設計案です。音声、英語教材の人による確認、学習効果、iPhone上の動作は未検証です。履歴保存・認証・音声方式・東京リージョンは未確定です。

要件と依存関係は [ロードマップ](docs/roadmap.md)、[エピック](docs/epics.md)、[PBI一覧](docs/pbis.json) を参照してください。原本は基準コミットに保持しています。
