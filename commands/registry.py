"""
registry.py — Command Router
  Parses user input and dispatches to the correct command module.
  To add a new command: create a new file in commands/ and add its
  handler to COMMAND_MAP below. That's it.
"""

import re
import asyncio
import bot_core

# ── Import command handlers ──
from commands.msg       import handle_msg
from commands.qms       import handle_qms
from commands.embed_msg import handle_embed_msg
from commands.schedule  import handle_schedule, handle_cancel

# ────────────────────────────────────────────────────────────
#  Regex patterns
# ────────────────────────────────────────────────────────────
# #channel !msg [~/dir]
RE_MSG      = re.compile(
    r'^(#[^!$~\s]+)\s*!(?:msg|message)(\s+~\/\S+)?$', re.IGNORECASE)

# #channel !qms "text" [~/dir]
RE_QMS      = re.compile(
    r'^(#\S+)\s+!qms\s+"([^"]+)"(\s+~\/\S+)?$', re.IGNORECASE)

# #channel $msg ^color [~/dir]
RE_EMBED    = re.compile(
    r'^(#[^!$~\s]+)\s*\$(?:msg|message)\s*\^?(\S+)?(\s+~\/\S+)?$', re.IGNORECASE)

# #channel ~/dir  (file only upload)
RE_UPLOAD   = re.compile(r'^(#[^!$~\s]+)\s*(~\/\S+)$')

# %schedule <datetime> #channel <rest of command>
RE_SCHEDULE = re.compile(
    r'^%(\d{2}\.\d{2}\.\d{4}-\d{1,2}:\d{2})\s+(#[^!$~\s]+)\s*([!$~].+)$', re.IGNORECASE)

# %cancel
RE_CANCEL   = re.compile(r'^%cancel$', re.IGNORECASE)

# studio exit
RE_EXIT     = re.compile(r'^studio\s+exit$', re.IGNORECASE)


# ────────────────────────────────────────────────────────────
#  Main dispatch
# ────────────────────────────────────────────────────────────
def dispatch(raw: str, loop: asyncio.AbstractEventLoop):
    """
    Parse raw terminal input and run the matching command.
    Returns True  → keep running
    Returns False → exit studio
    """
    # Strip bracketed paste mode artifacts (PuTTY adds these when pasting)
    # e.g. ESC[?2004h adds chars like "1" or "0" prefix
    import re as _re
    inp = raw.strip()
    # Remove any leading non-command characters that aren't #, !, $, %, a-z, A-Z
    inp = _re.sub(r'^[^#!$%a-zA-Z]+', '', inp).strip()

    # ── exit ──
    if RE_EXIT.match(inp):
        return False

    # ── %cancel ──
    if RE_CANCEL.match(inp):
        asyncio.run_coroutine_threadsafe(handle_cancel(), loop).result(timeout=15)
        return True

    # ── %schedule ──
    m = RE_SCHEDULE.match(inp)
    if m:
        dt_str, channel, rest = m.group(1), m.group(2), m.group(3)
        asyncio.run_coroutine_threadsafe(
            handle_schedule(dt_str, channel, rest), loop
        ).result(timeout=15)
        return True

    # ── file-only upload ──
    m = RE_UPLOAD.match(inp)
    if m:
        channel, filepath = m.group(1), m.group(2)
        from commands.upload import handle_upload
        try:
            asyncio.run_coroutine_threadsafe(
                handle_upload(channel, None, filepath), loop
            ).result(timeout=15)
        except (FileNotFoundError, RuntimeError, ValueError) as e:
            print(f"\033[31m  ✘ {e}\033[0m")
        return True

    # ── #channel !msg [~/dir] ──
    m = RE_MSG.match(inp)
    if m:
        channel  = m.group(1)
        filepath = m.group(2).strip() if m.group(2) else None
        try:
            asyncio.run_coroutine_threadsafe(
                handle_msg(channel, filepath), loop
            ).result(timeout=60)
        except (FileNotFoundError, RuntimeError, ValueError) as e:
            print(f"\033[31m  ✘ {e}\033[0m")
        return True

    # ── #channel !qms "text" [~/dir] ──
    m = RE_QMS.match(inp)
    if m:
        channel  = m.group(1)
        text     = m.group(2)
        filepath = m.group(3).strip() if m.group(3) else None
        try:
            asyncio.run_coroutine_threadsafe(
                handle_qms(channel, text, filepath), loop
            ).result(timeout=15)
        except (FileNotFoundError, RuntimeError, ValueError) as e:
            print(f"\033[31m  ✘ {e}\033[0m")
        return True

    # ── #channel $msg ^color [~/dir] ──
    m = RE_EMBED.match(inp)
    if m:
        channel  = m.group(1)
        color    = m.group(2)
        filepath = m.group(3).strip() if m.group(3) else None
        try:
            asyncio.run_coroutine_threadsafe(
                handle_embed_msg(channel, color, filepath), loop
            ).result(timeout=60)
        except (FileNotFoundError, RuntimeError, ValueError) as e:
            print(f"\033[31m  ✘ {e}\033[0m")
        return True

    # ── unknown ──
    print(f"\033[33m  [!] Unknown command: '{inp}'\033[0m")
    print( "  \033[90mTip: Try #channel !msg | !qms \"text\" | $msg ^color | ~/dir\033[0m")
    return True
