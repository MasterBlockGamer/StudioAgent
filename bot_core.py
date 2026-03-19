import discord
import asyncio
import threading
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bot_entry
from discord_commands.dc_main import setup_discord_commands

# ── Global bot instance accessible by command modules ──
bot = discord.Client(intents=discord.Intents.all())
_loop = None
_ready_event = threading.Event()

@bot.event
async def on_ready():
    print(f"\033[90m  [Bot] Logged in as {bot.user}\033[0m")
    _ready_event.set()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await setup_discord_commands(bot, message)

def get_loop():
    return _loop

def run_bot():
    global _loop
    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)
    _loop.run_until_complete(bot.start(bot_entry.TOKEN))

def start_bot_thread():
    t = threading.Thread(target=run_bot, daemon=True)
    t.start()
    return _ready_event

# ── Utility: resolve channel name → channel object ──
def resolve_channel(channel_name: str):
    guild_id = int(bot_entry.GUILD_ID)
    guild = bot.get_guild(guild_id)
    if guild is None:
        return None
    name = channel_name.lstrip("#").lower()
    for ch in guild.text_channels:
        if ch.name.lower() == name:
            return ch
    return None

# ── Send a plain message ──
async def send_message(channel_name: str, content: str):
    ch = resolve_channel(channel_name)
    if ch is None:
        raise ValueError(f"Channel '{channel_name}' not found in server.")
    await ch.send(content)

# ── Send an embed message ──
async def send_embed(channel_name: str, content: str, color: int = 0x808080):
    ch = resolve_channel(channel_name)
    if ch is None:
        raise ValueError(f"Channel '{channel_name}' not found in server.")
    embed = discord.Embed(description=content, color=color)
    await ch.send(embed=embed)

# ── Send a file (+ optional message) ──
async def send_file(channel_name: str, filepath: str, content: str = None):
    ch = resolve_channel(channel_name)
    if ch is None:
        raise ValueError(f"Channel '{channel_name}' not found in server.")
    expanded = os.path.expanduser(filepath)
    if not os.path.isfile(expanded):
        raise FileNotFoundError(f"File not found: {expanded}")
    file = discord.File(expanded)
    await ch.send(content=content or "", file=file)
