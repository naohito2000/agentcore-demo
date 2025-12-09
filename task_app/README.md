# AgentCore Task App

DevOps Assistant用のタスク管理アプリ（React SPA）

## セットアップ

### 1. 依存関係インストール
```bash
npm install
```

### 2. 環境変数設定
`.env`ファイルを作成:
```
REACT_APP_AWS_REGION=ap-northeast-1
REACT_APP_AWS_ACCESS_KEY_ID=your_access_key_id
REACT_APP_AWS_SECRET_ACCESS_KEY=your_secret_access_key
```

### 3. ローカル起動
```bash
npm start
```

## デプロイ

### S3 + CloudFront

1. ビルド
```bash
npm run build
```

2. S3バケット作成
```bash
aws s3 mb s3://agentcore-task-app --region ap-northeast-1
```

3. 静的ウェブサイトホスティング有効化
```bash
aws s3 website s3://agentcore-task-app --index-document index.html
```

4. アップロード
```bash
aws s3 sync build/ s3://agentcore-task-app/ --delete
```

5. CloudFront Distribution作成（オプション）

## 機能

- タスク一覧表示
- ステータスフィルタ（All/Todo/In Progress/Done）
- 優先度表示（High/Medium/Low）
- 担当者・期限表示
