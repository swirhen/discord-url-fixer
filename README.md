# discord-url-fixer

特定の URL を含む発言に、変換後の URL を返信し、元発言の埋め込みを非表示にする常駐 bot。
元発言が削除されたら bot の返信も削除する（bot の起動中に返信したものだけ）。

## Bot の準備（Discord Developer Portal）

1. New Application → Bot → Reset Token でトークンを取得する
2. Bot ページの **Message Content Intent** をオンにする
3. OAuth2 → URL Generator で scope `bot`、権限 `View Channels` / `Send Messages` / `Read Message History` / `Manage Messages` を選び、生成した URL でサーバーに招待する

## セットアップ

```powershell
python -m venv $HOME\.venv\discord-url-fixer
& $HOME\.venv\discord-url-fixer\Scripts\python.exe -m pip install -r requirements.txt
```

- トークンは `token.txt` に書くか、環境変数 `DISCORD_TOKEN` に設定する
- 変換ルールは `rules.example.json` を `rules.json` にコピーして編集する（`rules.json` が無ければ example を使う）。`pattern` は Python の正規表現で、URL 1 つずつに `re.sub` を順に適用する

## 起動

```powershell
& $HOME\.venv\discord-url-fixer\Scripts\python.exe bot.py
```

## 本番サーバー（prod-checker）

`/home/swirhen/discord-url-fixer` にクローンし、venv はリポジトリ内の `.venv` に作る。systemd のシステムサービスとして常駐させる。

```bash
cd ~/discord-url-fixer
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
sudo cp discord-url-fixer.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now discord-url-fixer
```

- 更新：`git pull && sudo systemctl restart discord-url-fixer`
- ログ：`journalctl -u discord-url-fixer -f`
