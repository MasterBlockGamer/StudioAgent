"""
embed_msg.py — Command: #channel $msg ^color [~/dir]
Opens nano, sends message as a Discord embed with colored left bar.
Supports ^red, ^blue, ^#FF5733, etc.
"""

import os
import tempfile
import subprocess
import bot_core
from commands.upload import handle_upload

# ── Named color map ──
COLOR_NAMES = {
    "red":     0xE74C3C,
    "blue":    0x3498DB,
    "green":   0x2ECC71,
    "yellow":  0xF1C40F,
    "orange":  0xE67E22,
    "purple":  0x9B59B6,
    "pink":    0xFF69B4,
    "cyan":    0x1ABC9C,
    "white":   0xFFFFFF,
    "black":   0x000000,
    "grey":    0x808080,
    "gray":    0x808080,
    "gold":    0xFFD700,
}

def parse_color(color_str: str) -> int:
    s = color_str.lower().lstrip('^')
    if s in COLOR_NAMES:
        return COLOR_NAMES[s]
    # hex
    s = s.lstrip('#')
    try:
        return int(s, 16)
    except ValueError:
        print(f"\033[33m  [!] Unknown color '{color_str}', using grey.\033[0m")
        return 0x808080


async def handle_embed_msg(channel: str, color_str: str = None, filepath: str = None):
    color = parse_color(color_str) if color_str else 0x808080

    # ── Open nano ──
    tmp = tempfile.NamedTemporaryFile(
        mode='w', suffix='.txt',
        prefix='studio_embed_',
        delete=False
    )
    tmp_path = tmp.name
    tmp.write("# Write your embed message below. Save (Ctrl+O, Enter) then exit (Ctrl+X).\n")
    tmp.write("# Lines starting with # are ignored.\n\n")
    tmp.close()

    subprocess.call(['nano', tmp_path])

    with open(tmp_path, 'r') as f:
        lines = [l for l in f.readlines()
                 if not l.startswith('#')]
    os.unlink(tmp_path)

    content = ''.join(lines).strip()
    if not content:
        print("\033[33m  [!] Empty message — nothing sent.\033[0m")
        return

    ch_name = channel.lstrip('#')

    try:
        if filepath:
            # Send embed first, then file
            await bot_core.send_embed(ch_name, content, color)
            await handle_upload(channel, None, filepath)
        else:
            await bot_core.send_embed(ch_name, content, color)
        print(f"\033[32m  ✔ Embed successfully sent to {channel}\033[0m")
    except Exception as e:
        print(f"\033[31m  ✘ Failed: {e}\033[0m")
