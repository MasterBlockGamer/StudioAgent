"""
msg.py — Command: #channel !msg [~/dir]
Opens nano, user writes message, sends to Discord on save+exit.
"""

import os
import tempfile
import subprocess
import bot_core
from commands.upload import handle_upload


async def handle_msg(channel: str, filepath: str = None):
    # ── Open nano for message composition ──
    tmp = tempfile.NamedTemporaryFile(
        mode='w', suffix='.txt',
        prefix='studio_msg_',
        delete=False
    )
    tmp_path = tmp.name
    tmp.write("# Write your message below. Save (Ctrl+O, Enter) then exit (Ctrl+X).\n")
    tmp.write("# This line and lines starting with # are ignored.\n\n")
    tmp.close()

    subprocess.call(['nano', tmp_path])

    # ── Read back content ──
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
            await handle_upload(channel, content, filepath)
        else:
            await bot_core.send_message(ch_name, content)
        print(f"\033[32m  ✔ Message successfully sent to {channel}\033[0m")
    except Exception as e:
        print(f"\033[31m  ✘ Failed: {e}\033[0m")
