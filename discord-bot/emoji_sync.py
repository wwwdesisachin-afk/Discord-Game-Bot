
"""
Sync external custom emojis as Application Emojis so the bot can use them anywhere.

On startup the bot:
  1. Fetches existing application emojis
  2. For any missing one, downloads the image from Discord CDN by original ID
  3. Uploads it as an application emoji owned by this bot
  4. Patches data.TIMELINE_EMOJIS, data.TOSS_HEAD_EMOJI, data.TOSS_TAIL_EMOJI
     so the rest of the codebase gets the correct <:name:id> strings.
"""

from __future__ import annotations
import aiohttp
import discord

import data

# key → (app_emoji_name, original_id, animated)
_SOURCE: dict[str, tuple[str, int, bool]] = {
    "toss_head":    ("cs_head",    1482453280679264319, False),
    "toss_tail":    ("cs_tail",    1482453206205464658, False),
    "timeline_0":   ("cs_dot",     1483444731383119965, False),
    "timeline_1":   ("cs_1run",    1483442692192075957, False),
    "timeline_2":   ("cs_2run",    1483442723599155240, False),
    "timeline_3":   ("cs_3run",    1483442748802728178, False),
    "timeline_4":   ("cs_4run",    1480816551996162048, True),
    "timeline_6":   ("cs_6run",    1480816170067165274, True),
    "timeline_W":   ("cs_wicket",  1480816418982330491, False),
    "timeline_NB":  ("cs_noball",  1483444755613614341, False),
    "timeline_NB1": ("cs_noball1", 1484027767774380102, False),
}

# Timeline key → data.TIMELINE_EMOJIS key
_TIMELINE_MAP = {
    "timeline_0":   "0",
    "timeline_1":   "1",
    "timeline_2":   "2",
    "timeline_3":   "3",
    "timeline_4":   "4",
    "timeline_6":   "6",
    "timeline_W":   "W",
    "timeline_NB":  "NB",
    "timeline_NB1": "NB+1",
}


async def sync_emojis(bot: discord.Client) -> None:
    print("[EmojiSync] Starting emoji sync…")

    try:
        existing = {e.name: e for e in await bot.fetch_application_emojis()}
    except Exception as exc:
        print(f"[EmojiSync] Could not fetch application emojis: {exc}")
        return

    async with aiohttp.ClientSession() as session:
        for key, (name, original_id, animated) in _SOURCE.items():
            emoji_str = _build_str(name, original_id, animated)  # fallback

            if name in existing:
                e = existing[name]
                emoji_str = _fmt(e.name, e.id, animated)
                print(f"[EmojiSync] Already exists: {name} → {emoji_str}")
            else:
                ext = "gif" if animated else "png"
                url = f"https://cdn.discordapp.com/emojis/{original_id}.{ext}"
                try:
                    async with session.get(url) as resp:
                        if resp.status != 200:
                            print(f"[EmojiSync] CDN fetch failed for {key} ({url}): {resp.status}")
                            _patch(key, emoji_str)
                            continue
                        image_bytes = await resp.read()

                    created = await bot.create_application_emoji(name=name, image=image_bytes)
                    emoji_str = _fmt(created.name, created.id, animated)
                    print(f"[EmojiSync] Uploaded {name} → {emoji_str}")
                except Exception as exc:
                    print(f"[EmojiSync] Error on {key}: {exc}")

            _patch(key, emoji_str)

    print(f"[EmojiSync] Done. Timeline: {list(data.TIMELINE_EMOJIS.values())}")


def _fmt(name: str, emoji_id: int, animated: bool) -> str:
    prefix = "a" if animated else ""
    return f"<{prefix}:{name}:{emoji_id}>"


def _build_str(name: str, original_id: int, animated: bool) -> str:
    """Fallback using the original server emoji ID (may still fail if bot isn't there)."""
    return _fmt(name, original_id, animated)


def _patch(key: str, emoji_str: str) -> None:
    if key == "toss_head":
        data.TOSS_HEAD_EMOJI = emoji_str
    elif key == "toss_tail":
        data.TOSS_TAIL_EMOJI = emoji_str
    elif key in _TIMELINE_MAP:
        data.TIMELINE_EMOJIS[_TIMELINE_MAP[key]] = emoji_str
