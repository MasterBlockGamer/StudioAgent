"""
dc_main.py — In-Discord Command Handler
When someone @mentions the bot, this parses the command and
routes it to the correct discord_commands/*.py file.

To add a new in-discord command:
  1. Create discord_commands/yourcommand.py with a handle(message) coroutine.
  2. Add an entry to DISCORD_COMMAND_MAP below.
"""

import discord
from discord_commands import profile   # ← import new command files here

# ────────────────────────────────────────────────────────────
#  Command map: keyword → handler module
#  Handler must expose:  async def handle(message: discord.Message)
# ────────────────────────────────────────────────────────────
DISCORD_COMMAND_MAP = {
    "profile": profile,
    # "stats":  stats,     ← future commands go here
}


async def setup_discord_commands(bot: discord.Client, message: discord.Message):
    """Called from bot_core on_message."""

    # Only respond when the bot is directly mentioned
    if bot.user not in message.mentions:
        return

    # Strip the mention and get the command keyword
    content = message.content
    for mention in [f'<@{bot.user.id}>', f'<@!{bot.user.id}>']:
        content = content.replace(mention, '').strip()

    keyword = content.split()[0].lower() if content.split() else ""

    if keyword in DISCORD_COMMAND_MAP:
        await DISCORD_COMMAND_MAP[keyword].handle(message)
    else:
        await message.reply(
            f"Unknown command `{keyword}`. "
            f"Available: {', '.join(f'`{k}`' for k in DISCORD_COMMAND_MAP)}",
            mention_author=False
        )
