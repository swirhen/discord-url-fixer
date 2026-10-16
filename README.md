# discord-url-fixer

特定の URL を含む発言に、変換後の URL を返信し、元発言の埋め込みを非表示にする常駐 bot。
元発言が削除されたら bot の返信も削除する（bot の起動中に返信したものだけ）。

## Bot の準備（Discord Developer Portal）

1. New Application → Bot → Reset Token でトークンを取得する
2. Bot ページの **Message Content Intent** をオンにする
3. OAuth2 → URL Generator で scope `bot`、権限 `View Channels` / `Send Messages` / `Read Message History` / `Manage Messages` を選び、生成した URL でサーバーに招待する

## セットアップ

```bash
git clone https://github.com/swirhen/discord-url-fixer.git
cd discord-url-fixer
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Windows の場合は `python -m venv .venv` のあと `.venv\Scripts\python.exe -m pip install -r requirements.txt` とする。

- トークンは `token.txt` に書くか、環境変数 `DISCORD_TOKEN` に設定する
- 変換ルールは `rules.example.json` を `rules.json` にコピーして編集する（`rules.json` が無ければ example を使う）。`pattern` は Python の正規表現で、URL 1 つずつに `re.sub` を順に適用する

## ローカル起動（テスト）

```bash
.venv/bin/python bot.py
```

Windows の場合は `.venv\Scripts\python.exe bot.py`。

## サーバー起動（任意のLinuxサーバー）

任意のディレクトリ（例：`/home/<ユーザー名>/discord-url-fixer`）にクローンし、venv はリポジトリ内の `.venv` に作る。systemd のシステムサービスとして常駐させる。
同梱の `discord-url-fixer.service` は `/home/swirhen/discord-url-fixer` に置く前提なので、実行ユーザーとパス（8〜10行目の `User` / `WorkingDirectory` / `ExecStart`）を自分の環境に合わせて書き換えること。
起動前にリポジトリ直下へ `token.txt` を置いておく。

```bash
git clone https://github.com/swirhen/discord-url-fixer.git ~/discord-url-fixer
cd ~/discord-url-fixer
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
# token.txt を置き、discord-url-fixer.service の 8〜10 行目を編集してから
sudo cp discord-url-fixer.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now discord-url-fixer
```

- 更新：`git pull && sudo systemctl restart discord-url-fixer`
- ログ：`journalctl -u discord-url-fixer -f`
