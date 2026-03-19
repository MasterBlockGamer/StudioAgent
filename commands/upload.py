"""
upload.py — File upload handler.
png/gif → inline image on Discord.
other   → attached file.
"""

import os
import bot_core
import discord

IMAGE_EXTS = {'.png', '.gif', '.jpg', '.jpeg', '.webp'}


async def handle_upload(channel: str, content: str = None, filepath: str = None):
    if not filepath:
        return

    ch_name  = channel.lstrip('#')
    ch       = bot_core.resolve_channel(ch_name)
    if ch is None:
        raise ValueError(f"Channel '{channel}' not found.")

    expanded = os.path.expanduser(filepath.strip())
    if not os.path.isfile(expanded):
        raise FileNotFoundError(f"File not found: {expanded}")

    ext = os.path.splitext(expanded)[1].lower()

    try:
        file = discord.File(expanded)
        if ext in IMAGE_EXTS:
            # Discord auto-inlines images — just send the file
            await ch.send(content=content or "", file=file)
        else:
            # Non-image: shows as attachment
            await ch.send(content=content or "", file=file)
        print(f"\033[32m  ✔ File '{os.path.basename(expanded)}' uploaded to {channel}\033[0m")
    except Exception as e:
        raise RuntimeError(f"Upload failed: {e}")
