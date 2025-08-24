# sports-webapi-go

サッカー（フットボール）の **チーム/選手** を扱う **読み取り中心 Web API**（Go + `net/http`）。  
**ローカルで即動く**・**ドキュメント/デモは `/docs/` に内蔵**。

## 使い方（最短）

```bash
# 1) 依存なし。プロジェクト直下で実行
go run ./cmd/api

# 2) ブラウザで開く
http://localhost:8000/docs/

# 3) 直接叩く例
curl "http://localhost:8000/health"
curl "http://localhost:8000/api/players?per_page=5"
```

## エンドポイント

- `GET /health` – 稼働確認
- `GET /api/teams` – 一覧（検索 `q`、フィルタ `league,country,min_rating`、ソート `name|rating|founded`、ページング）
- `GET /api/teams/{id}` – 詳細
- `GET /api/players` – 一覧（検索 `q`、フィルタ `team_id,position,nationality,min_rating,max_age`、ソート `name|rating|age|value`、ページング）
- `GET /api/players/{id}` – 詳細
- `GET /api/stats/summary` – 集計（件数、平均、上位）

### クエリの注意
- ソートは `sort=key`（昇順） / `sort=-key`（降順）。未知のキーは **400** を返す。
- `per_page` は 1..100 に制限。`page` は 1..100000。
- CORS：GET/OPTIONS は `*` を許可。

## よくある質問

- **データはどこから？**  
  起動時に **メモリ内にフェイクデータを生成**（再現性のため seed 固定）。DB は不要。

- **docs を別ポートで開きたい**  
  このプロジェクトは Go サーバが `/docs/` を配信します。必要なら `docs/` フォルダを `python3 -m http.server 3000` で配信してもOK（CORSは許可済み）。

- **ビルドして実行**  
  ```bash
  go build -o sports-api ./cmd/api
  ./sports-api
  ```

## ライセンス
MIT
