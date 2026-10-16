# AI開発エージェント向け運用ルール

README.md は汎用環境向けの手順。この環境（swirhen）では以下のとおり運用している。

## プロジェクト概要

- 特定の URL を含む発言に変換後の URL を返信し、元発言の埋め込みを非表示にする Discord bot（`bot.py` のみ）。
- 変換ルールは `rules.json`（無ければ `rules.example.json`）。本番は現在 `rules.example.json` を使っている。

## ローカル開発（Windows）

- Python の venv はリポジトリ内の `.venv` ではなく、リポジトリ外の `~\.venv\discord-url-fixer` に PC ごとに作る（ソースは OneDrive で PC 間共有するため）。
  作成: `python -m venv $env:USERPROFILE\.venv\discord-url-fixer; & $env:USERPROFILE\.venv\discord-url-fixer\Scripts\python.exe -m pip install -r requirements.txt`
- 起動: `& $env:USERPROFILE\.venv\discord-url-fixer\Scripts\python.exe bot.py`
- 本番と同じトークンを使うので、ローカルで起動すると 1 つの発言に返信が 2 つ付く。テストが終わったら必ず止める。

## 本番（prod-checker）

- 配置先は `/home/swirhen/discord-url-fixer`。venv はリポジトリ内の `.venv`。
- systemd のシステムサービス `discord-url-fixer.service`（リポジトリ同梱のファイルを `/etc/systemd/system/` にコピー済み）で常駐。
- リリース: GitHub へプッシュした後、
  `ssh prod-checker "cd /home/swirhen/discord-url-fixer && git pull --ff-only && sudo systemctl restart discord-url-fixer"`
  を実行し、`ssh prod-checker "systemctl is-active discord-url-fixer"` で `active` を確認する。
- `requirements.txt` を変えたときは、再起動の前に `.venv/bin/pip install -r requirements.txt` を実行する。
- ユニットファイルを変えたときは、再度 `/etc/systemd/system/` にコピーして `sudo systemctl daemon-reload` を実行する。
- ログ: `journalctl -u discord-url-fixer -f`

## 秘密情報

- `token.txt` は Bot トークン。内容を表示・コミットしない。本番へはローカルから scp で転送し、権限は `600`。
- このリポジトリは公開。個人環境の秘密情報を README・AGENTS.md・コミットに含めない。
