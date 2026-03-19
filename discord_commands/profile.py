"""
profile.py — In-Discord Command: @bot profile
Replies with the user's profile info as an embed.

To create a new in-discord command, copy this file structure:
  - async def handle(message: discord.Message)
  - Register it in dc_main.py DISCORD_COMMAND_MAP
"""

import discord


async def handle(message: discord.Message):
    user  = message.author
    embed = discord.Embed(
        title=f"👤 {user.display_name}'s Profile",
        color=0x3498DB
    )
    embed.add_field(name="Username",   value=str(user),               inline=True)
    embed.add_field(name="ID",         value=str(user.id),            inline=True)
    embed.add_field(name="Joined Discord",
                    value=user.created_at.strftime("%d %b %Y"),       inline=False)

    if hasattr(user, 'joined_at') and user.joined_at:
        embed.add_field(name="Joined Server",
                        value=user.joined_at.strftime("%d %b %Y"),    inline=True)

    embed.set_thumbnail(url=user.display_avatar.url)
    await message.reply(embed=embed, mention_author=False)
