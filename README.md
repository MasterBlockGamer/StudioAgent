<div align="center">

```
   ╔══════════════════════════════════════╗
   ║     MasterBlock Studio — Discord     ║
   ╚══════════════════════════════════════╝

        S T U D I O   A G E N T
```

**A Raspberry Pi Discord bot with its own terminal command center.**  
Type commands from your Pi. Messages appear on Discord. Simple as that.

![Python](https://img.shields.io/badge/Python-3.10+-3670A0?style=flat-square&logo=python&logoColor=white)
![Discord](https://img.shields.io/badge/Discord.py-2.3+-5865F2?style=flat-square&logo=discord&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-C51A4A?style=flat-square&logo=raspberrypi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)

</div>

---

## What is this?

StudioAgent runs on a **Raspberry Pi** and gives you a slick terminal interface to control a Discord bot. No web dashboard, no browser — just you, your Pi, and a glowing command line.

Boot it up with `studio`, and you get a full CLI to send messages, drop files, send styled embeds, and even schedule posts for later — all firing straight into your Discord server.

---

## Quickstart

### Prerequisites

- Raspberry Pi (tested on Pi 3+)
- Python 3.10+
- A Discord Bot Token ([create one here](https://discord.com/developers/applications))

### Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/StudioAgent.git
cd StudioAgent

# Install dependencies
pip3 install discord.py aiohttp aiofiles pyfiglet colorama

# Add your credentials
nano bot_entry.py
```

Fill in `bot_entry.py`:
```python
TOKEN = "your_bot_token_here"
GUILD_ID = "your_server_id_here"
```

> ⚠️ Never commit `bot_entry.py` — it's already in `.gitignore`

### Enable Discord Intents

Go to [discord.com/developers/applications](https://discord.com/developers/applications) → your bot → **Bot** tab → enable all three **Privileged Gateway Intents**.

### Create the shortcut command

```bash
sudo nano /usr/local/bin/studio
```
```bash
#!/bin/bash
cd /home/youruser/StudioAgent
python3 studio.py
```
```bash
sudo chmod +x /usr/local/bin/studio
```

### Launch

```bash
studio
```

---

## Terminal Commands

All commands are typed at the `»` prompt after boot.

### Send a Message

```
#channel !msg
#channel !message
```
Opens **nano** — write your message, save (`Ctrl+O` `Enter`) and exit (`Ctrl+X`). Message fires to Discord.

Supports Discord formatting: `@everyone`, `**bold**`, `*italic*`, `:joy:`, URLs with auto-embed.

---

### Quick Message

```
#channel !qms "your message here"
```
No editor. Message is inline. Fires immediately.

```bash
# Example
#general !qms "Guys join Minecraft fast"
#notifications !qms "@everyone Event starts in 10 mins!"
```

---

### Embed Message

```
#channel $msg ^color
#channel $message ^color
```
Opens nano. Message sends inside a Discord embed box with a colored left bar.

**Color formats — both supported:**
```bash
#general $msg ^red
#general $msg ^#FF5733
#general $msg ^blue
```

Available named colors: `red` `blue` `green` `yellow` `orange` `purple` `pink` `cyan` `white` `grey` `gold`

---

### File Upload

Attach any file to any command using `~/path/to/file`:

```bash
# Upload only
#general ~/desktop/pikachu.png

# Message + file
#general !msg ~/discord/banner.gif

# Quick message + file
#general !qms "Check this out" ~/downloads/video.mp4

# Embed + file
#general $msg ^blue ~/images/chart.png
```

> `png`, `gif`, `jpg` → inline image on Discord  
> Other files → attachment

---

### Scheduled Messages

```
%dd.mm.yyyy-hh:mm #channel !command
```

Schedule any command to fire at a future date and time **(IST)**. Schedules **survive Pi reboots** — saved to `schedules.json`.

```bash
# Schedule a quick message
%25.03.2026-18:00 #general !qms "Event starts now!"

# Schedule a nano message
%01.04.2026-09:00 #announcements !msg

# Schedule an embed
%20.03.2026-20:00 #general $msg ^gold

# Cancel all pending schedules
%cancel
```

After setting a schedule you'll see:
```
✔ Schedule set for 25.03.2026 at 18:00. Stay tuned.
```

---

### Exit

```
studio exit
```

---

## File Structure

```
StudioAgent/
├── studio.py                  # Boot + terminal UI
├── bot_core.py                # Discord bot engine
├── bot_entry.py               # 🔒 Token + Guild ID (not committed)
├── schedules.json             # Persistent schedule store
├── requirements.txt
│
├── commands/                  # Terminal command modules
│   ├── registry.py            # Command router (add new commands here)
│   ├── msg.py                 # !msg / !message
│   ├── qms.py                 # !qms
│   ├── embed_msg.py           # $msg / $message
│   ├── upload.py              # File upload handler
│   └── schedule.py            # %schedule / %cancel
│
└── discord_commands/          # In-Discord command modules
    ├── dc_main.py             # @bot mention router
    └── profile.py             # @bot profile command
```

### Adding a New Terminal Command

1. Create `commands/yourcommand.py` with an `async def handle_...()` function
2. Add one line to `commands/registry.py` — import + regex match + dispatch call
3. Done. No touching any other file.

### Adding a New In-Discord Command

1. Create `discord_commands/yourcommand.py` with `async def handle(message)`
2. Add one line to `discord_commands/dc_main.py` in `DISCORD_COMMAND_MAP`
3. Done.

---

## Roadmap

- [ ] `@bot` in-discord commands (structure ready, commands coming)
- [ ] `studio status` — show bot uptime, pending schedules, server info
- [ ] `#channel !poll "question" "opt1" "opt2"` — create Discord polls
- [ ] `studio logs` — view recent sent messages from terminal
- [ ] Multi-server support
- [ ] `%recurring` — repeat scheduled messages daily/weekly

---

## Built With

- [discord.py](https://discordpy.readthedocs.io/) — Discord API wrapper
- [pyfiglet](https://github.com/pwaller/pyfiglet) — ASCII art banner
- [colorama](https://github.com/tartley/colorama) — Terminal colors

---

<div align="center">

Built on a Raspberry Pi. Runs at 3am. No complaints.

**MasterBlock Studio © 2026**

Join Discord server : https://discord.gg/xyTKTFY2

</div>
