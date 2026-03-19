"""
schedule.py — %schedule and %cancel commands.
Schedules persist to schedules.json so they survive Pi reboots.
"""

import os
import json
import asyncio
import tempfile
import subprocess
import threading
from datetime import datetime
import zoneinfo

IST = zoneinfo.ZoneInfo("Asia/Kolkata")

import bot_core
from commands.embed_msg import parse_color

SCHEDULE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'schedules.json'
)

_timers: dict[str, threading.Timer] = {}   # id → Timer


# ────────────────────────────────────────────────────────────
#  Persistence helpers
# ────────────────────────────────────────────────────────────
def _load_schedules() -> list:
    if not os.path.isfile(SCHEDULE_FILE):
        return []
    with open(SCHEDULE_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def _save_schedules(schedules: list):
    with open(SCHEDULE_FILE, 'w') as f:
        json.dump(schedules, f, indent=2)

def _remove_schedule(sid: str):
    schedules = _load_schedules()
    schedules = [s for s in schedules if s['id'] != sid]
    _save_schedules(schedules)


# ────────────────────────────────────────────────────────────
#  Execution
# ────────────────────────────────────────────────────────────
def _execute_schedule(sid: str, channel: str, content: str,
                      is_embed: bool, color: int,
                      filepath: str = None):
    loop = bot_core.get_loop()
    if loop is None:
        return

    async def _run():
        ch_name = channel.lstrip('#')
        try:
            if filepath:
                from commands.upload import handle_upload
                if is_embed:
                    await bot_core.send_embed(ch_name, content, color)
                    await handle_upload(channel, None, filepath)
                else:
                    await handle_upload(channel, content, filepath)
            elif is_embed:
                await bot_core.send_embed(ch_name, content, color)
            else:
                await bot_core.send_message(ch_name, content)
            print(f"\n\033[32m  ✔ Scheduled message sent to {channel}\033[0m")
        except Exception as e:
            print(f"\n\033[31m  ✘ Scheduled send failed: {e}\033[0m")
        finally:
            _remove_schedule(sid)
            if sid in _timers:
                del _timers[sid]

    asyncio.run_coroutine_threadsafe(_run(), loop)


def _arm_timer(entry: dict):
    """Given a schedule entry, arm a threading.Timer for it."""
    sid      = entry['id']
    target   = datetime.fromisoformat(entry['target_iso'])
    delay    = (target - datetime.now(tz=IST).replace(tzinfo=None)).total_seconds()

    if delay <= 0:
        # Missed while Pi was off — fire immediately
        delay = 0

    t = threading.Timer(
        delay,
        _execute_schedule,
        kwargs={
            'sid':      sid,
            'channel':  entry['channel'],
            'content':  entry['content'],
            'is_embed': entry.get('is_embed', False),
            'color':    entry.get('color', 0x808080),
            'filepath': entry.get('filepath'),
        }
    )
    t.daemon = True
    t.start()
    _timers[sid] = t


def restore_schedules():
    """Call once at startup to re-arm all saved schedules."""
    for entry in _load_schedules():
        _arm_timer(entry)


# ────────────────────────────────────────────────────────────
#  Nano helper
# ────────────────────────────────────────────────────────────
def _open_nano(prefix='studio_sched_') -> str:
    tmp = tempfile.NamedTemporaryFile(
        mode='w', suffix='.txt', prefix=prefix, delete=False
    )
    tmp_path = tmp.name
    tmp.write("# Write your scheduled message below.\n")
    tmp.write("# Save (Ctrl+O, Enter) then exit (Ctrl+X).\n\n")
    tmp.close()
    subprocess.call(['nano', tmp_path])
    with open(tmp_path, 'r') as f:
        lines = [l for l in f.readlines() if not l.startswith('#')]
    os.unlink(tmp_path)
    return ''.join(lines).strip()


# ────────────────────────────────────────────────────────────
#  handle_schedule
# ────────────────────────────────────────────────────────────
async def handle_schedule(dt_str: str, channel: str, rest: str):
    """
    dt_str  : "19.03.2026-04:00"
    channel : "#general"
    rest    : the command part e.g. "!msg" or "$msg ^red ~/dir"
    """
    import re, uuid

    # ── Parse datetime ──
    try:
        # Support both single and double digit hours (5:40 or 05:40)
        if dt_str.count(':') == 1:
            date_part, time_part = dt_str.rsplit('-', 1)
            h, m = time_part.split(':')
            dt_str = f"{date_part}-{int(h):02d}:{m}"
        target = datetime.strptime(dt_str, "%d.%m.%Y-%H:%M")
    except ValueError:
        print("\033[31m  ✘ Invalid date format. Use %dd.mm.yyyy-hh:mm\033[0m")
        return

    if target <= datetime.now(tz=IST).replace(tzinfo=None):
        print("\033[31m  ✘ Scheduled time is in the past.\033[0m")
        return

    is_embed = False
    color    = 0x808080
    filepath = None
    content  = ""

    rest = rest.strip()

    # ── Detect file path ──
    fp_match = re.search(r'(~\/\S+)$', rest)
    if fp_match:
        filepath = fp_match.group(1)
        rest = rest[:fp_match.start()].strip()

    # ── Branch on command type ──
    if re.match(r'^\$(?:msg|message)', rest, re.IGNORECASE):
        is_embed = True
        color_match = re.search(r'\^(\S+)', rest)
        if color_match:
            color = parse_color(color_match.group(1))
        content = _open_nano()

    elif re.match(r'^!qms\s+"([^"]+)"', rest, re.IGNORECASE):
        qms_match = re.match(r'^!qms\s+"([^"]+)"', rest, re.IGNORECASE)
        content = qms_match.group(1)

    elif re.match(r'^!(?:msg|message)', rest, re.IGNORECASE):
        content = _open_nano()

    else:
        print(f"\033[33m  [!] Unrecognised schedule command: '{rest}'\033[0m")
        return

    if not content and not filepath:
        print("\033[33m  [!] Empty message — schedule not created.\033[0m")
        return

    # ── Persist ──
    sid = str(uuid.uuid4())[:8]
    entry = {
        'id':         sid,
        'target_iso': target.isoformat(),
        'channel':    channel,
        'content':    content,
        'is_embed':   is_embed,
        'color':      color,
        'filepath':   filepath,
    }
    schedules = _load_schedules()
    schedules.append(entry)
    _save_schedules(schedules)

    _arm_timer(entry)

    fmt_date = target.strftime("%d.%m.%Y")
    fmt_time = target.strftime("%H:%M")
    print(f"\033[36m  ✔ Schedule set for {fmt_date} at {fmt_time}. Stay tuned.\033[0m")


# ────────────────────────────────────────────────────────────
#  handle_cancel
# ────────────────────────────────────────────────────────────
async def handle_cancel():
    for sid, t in list(_timers.items()):
        t.cancel()
    _timers.clear()
    _save_schedules([])
    print("\033[36m  ✔ All scheduled messages cancelled.\033[0m")
