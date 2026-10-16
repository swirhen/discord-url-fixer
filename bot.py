"""特定の URL を含む発言に、変換後の URL を返信し、元発言の埋め込みを非表示にする Discord bot。

変換ルールは rules.json（無ければ rules.example.json）から読み込む。
トークンは環境変数 DISCORD_TOKEN か、同じフォルダの token.txt に置く。
"""

import json
import logging
import os
import re
import sys
from pathlib import Path

import discord

BASE_DIR = Path(__file__).resolve().parent

# <https://...> のように山括弧で囲まれた URL は投稿者が埋め込みを抑止しているので対象外にする
URL_PATTERN = re.compile(r"(?<!<)https?://[^\s<>|]+")

# 元メッセージ ID → bot の返信メッセージ ID（元発言が削除されたら返信も消すため）
reply_map: dict[int, int] = {}
REPLY_MAP_LIMIT = 1000

# メッセージの flags で埋め込み非表示を表すビット
SUPPRESS_EMBEDS_FLAG = 1 << 2

log = logging.getLogger("url-fixer")


def load_token() -> str:
    token = os.environ.get("DISCORD_TOKEN")
    if token:
        return token.strip()
    token_file = BASE_DIR / "token.txt"
    if token_file.exists():
        return token_file.read_text(encoding="utf-8").strip()
    sys.exit("DISCORD_TOKEN 環境変数か token.txt にトークンを設定してください")


def load_rules() -> list[tuple[re.Pattern[str], str]]:
    path = BASE_DIR / "rules.json"
    if not path.exists():
        path = BASE_DIR / "rules.example.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    rules = [(re.compile(r["pattern"]), r["replace"]) for r in data]
    log.info("%s から %d 件のルールを読み込みました", path.name, len(rules))
    return rules


def convert_urls(content: str, rules: list[tuple[re.Pattern[str], str]]) -> list[str]:
    """発言中の URL のうち、ルールで変換されたものを変換後の形で返す（重複除去・出現順）。"""
    converted: list[str] = []
    for url in URL_PATTERN.findall(content):
        new_url = url
        for pattern, replace in rules:
            new_url = pattern.sub(replace, new_url)
        if new_url != url and new_url not in converted:
            converted.append(new_url)
    return converted


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
RULES: list[tuple[re.Pattern[str], str]] = []


@client.event
async def on_ready() -> None:
    log.info("ログインしました: %s (id=%s)", client.user, client.user.id if client.user else "?")


@client.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return

    urls = convert_urls(message.content, RULES)
    if not urls:
        return

    reply = await message.reply("\n".join(urls), mention_author=False)
    reply_map[message.id] = reply.id
    if len(reply_map) > REPLY_MAP_LIMIT:
        reply_map.pop(next(iter(reply_map)))

    await suppress_embeds(message)


async def suppress_embeds(message: discord.Message | discord.PartialMessage) -> None:
    """元発言の埋め込みを非表示にする（Manage Messages 権限が必要）。"""
    try:
        await message.edit(suppress=True)
    except discord.Forbidden:
        log.warning("埋め込みを非表示にする権限がありません（#%s）", getattr(message.channel, "name", "?"))
    except discord.HTTPException as e:
        log.warning("埋め込みの非表示に失敗しました: %s", e)


@client.event
async def on_raw_message_edit(payload: discord.RawMessageUpdateEvent) -> None:
    # 埋め込みは投稿より遅れて付くことがあり、先に非表示にしても後から表示されてしまう。
    # 返信済みの発言に埋め込みが付いたら、もう一度非表示にする
    if payload.message_id not in reply_map:
        return
    data = payload.data
    if not data.get("embeds") or int(data.get("flags", 0)) & SUPPRESS_EMBEDS_FLAG:
        return
    channel = client.get_channel(payload.channel_id)
    if not isinstance(channel, discord.abc.Messageable):
        return
    log.info("後から付いた埋め込みを非表示にします（message=%s）", payload.message_id)
    await suppress_embeds(channel.get_partial_message(payload.message_id))  # type: ignore[attr-defined]


@client.event
async def on_raw_message_delete(payload: discord.RawMessageDeleteEvent) -> None:
    # 元発言が消されたら bot の返信も消す
    reply_id = reply_map.pop(payload.message_id, None)
    if reply_id is None:
        return
    channel = client.get_channel(payload.channel_id)
    if not isinstance(channel, discord.abc.Messageable):
        return
    try:
        await channel.get_partial_message(reply_id).delete()  # type: ignore[attr-defined]
    except discord.HTTPException:
        pass


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    RULES.extend(load_rules())
    client.run(load_token(), log_handler=None)


if __name__ == "__main__":
    main()
