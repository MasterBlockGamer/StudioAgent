"""
qms.py — Command: #channel !qms "message" [~/dir]
Quick send — no editor, message is inline in the command.
"""

import bot_core
from commands.upload import handle_upload


async def handle_qms(channel: str, text: str, filepath: str = None):
    ch_name = channel.lstrip('#')
    try:
        if filepath:
            await handle_upload(channel, text, filepath)
        else:
            await bot_core.send_message(ch_name, text)
        print(f"\033[32m  ✔ Message successfully sent to {channel}\033[0m")
    except Exception as e:
        print(f"\033[31m  ✘ Failed: {e}\033[0m")
