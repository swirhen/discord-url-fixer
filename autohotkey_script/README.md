# discord-paste-fixer（AutoHotkey v2）

Discord に Ctrl+V で貼り付けるときだけ、クリップボード中の x.com / twitter.com の URL を fxtwitter.com に変換して貼り付ける Windows 用スクリプト。bot を使わずに、自分の発言だけを変換したいとき向け。

- 他のアプリでの貼り付けには影響しない
- 貼り付け後、クリップボードは元の内容に戻る
- 対象は Discord のデスクトップアプリ（`Discord.exe` / `DiscordPTB.exe` / `DiscordCanary.exe`）と、Stack Next SE で Discord を開いているとき（ウィンドウタイトルに `Discord` を含むときだけ）。ブラウザ版 Discord は対象外

## 使い方

1. [AutoHotkey v2](https://www.autohotkey.com/) をインストールする
2. `discord-paste-fixer.ahk` をダブルクリックして起動する（タスクトレイに常駐する）
3. Windows 起動時に自動で起動したい場合は、`Win+R` で `shell:startup` を開き、`.ahk` のショートカットを置く

## 変換ルールの追加

スクリプト先頭の `RULES` に `[正規表現, 置換後]` を追加する。正規表現は AutoHotkey（PCRE）の書式で、先頭の `i)` は大文字小文字を区別しない指定。
