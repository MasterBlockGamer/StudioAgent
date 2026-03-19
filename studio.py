#!/usr/bin/env python3
"""
studio.py — MasterBlock Studio
Entry point. Run with: studio
"""

import sys
import os
import time
import itertools
import threading

from colorama import init as colorama_init, Fore, Style
colorama_init(autoreset=True, strip=False)

import pyfiglet


# ────────────────────────────────────────────────────────────
#  Helpers
# ────────────────────────────────────────────────────────────
def clear():
    os.system('clear')

def loading_bar(label: str, duration: float = 2.0, steps: int = 30):
    sys.stdout.write(f"  {Fore.CYAN}{label} [")
    sys.stdout.flush()
    for i in range(steps):
        time.sleep(duration / steps)
        sys.stdout.write(f"{Fore.CYAN}█")
        sys.stdout.flush()
    sys.stdout.write(f"{Fore.CYAN}] {Fore.GREEN}OK{Style.RESET_ALL}\n")
    sys.stdout.flush()

def spinner_wait(label: str, stop_event: threading.Event):
    frames = ['|', '\\', '/', '∕', '∖']
    cyc    = itertools.cycle(frames)
    while not stop_event.is_set():
        f = next(cyc)
        sys.stdout.write(f"\r  {Fore.CYAN}{f}  {label}{Style.RESET_ALL}  ")
        sys.stdout.flush()
        time.sleep(0.12)
    sys.stdout.write("\r" + " " * 60 + "\r")
    sys.stdout.flush()

def print_banner():
    line1 = pyfiglet.figlet_format("MasterBlock", font="cybermedium")
    line2 = pyfiglet.figlet_format("Studio", font="cybermedium")
    print(Fore.BLUE + Style.BRIGHT + line1.rstrip())
    print(Fore.BLUE + Style.BRIGHT + line2.rstrip())
    print(Fore.RED + "\n  Welcome to Studio Agents terminal\n")

def prompt_spinner():
    """
    Spinner runs for 1.5s, stops cleanly, then input() takes over.
    No thread is active during input() to avoid terminal collisions.
    """
    frames     = ['|', '\\', '/', '∕', '∖']
    cyc        = itertools.cycle(frames)
    stop_event = threading.Event()
    done_event = threading.Event()

    def _spin():
        while not stop_event.is_set():
            f = next(cyc)
            sys.stdout.write(f"\r  {Fore.CYAN}{f}{Style.RESET_ALL}  Waiting for your command.  ")
            sys.stdout.flush()
            time.sleep(0.15)
        sys.stdout.write('\r' + ' ' * 55 + '\r')
        sys.stdout.flush()
        done_event.set()

    t = threading.Thread(target=_spin, daemon=True)
    t.start()
    time.sleep(1.5)
    stop_event.set()
    done_event.wait()

    # Disable bracketed paste mode so PuTTY doesn't inject extra chars
    sys.stdout.write("\x1b[?2004l")
    sys.stdout.write(f"  {Fore.CYAN}»{Style.RESET_ALL} ")
    sys.stdout.flush()

    try:
        # Use raw stdin with explicit UTF-8 to handle pasted unicode (channel names etc)
        sys.stdout.flush()
        raw_bytes = sys.stdin.buffer.readline()
        result = raw_bytes.decode('utf-8', errors='replace').rstrip('\n').rstrip('\r')
    except (KeyboardInterrupt, EOFError):
        result = "studio exit"

    return result


# ────────────────────────────────────────────────────────────
#  Startup sequence
# ────────────────────────────────────────────────────────────
def startup():
    clear()

    print(f"\n{Fore.CYAN}  ╔══════════════════════════════════════╗")
    print(f"  ║     MasterBlock Studio — Booting     ║")
    print(f"  ╚══════════════════════════════════════╝{Style.RESET_ALL}\n")
    time.sleep(0.5)

    loading_bar("Loading configuration    ", 0.8)
    loading_bar("Initialising bot core   ", 0.8)
    loading_bar("Connecting to Discord   ", 0.5)

    from bot_core import start_bot_thread
    ready_event = start_bot_thread()

    stop_spin = threading.Event()
    spin_t    = threading.Thread(
        target=spinner_wait,
        args=("Waiting for Discord handshake...", stop_spin),
        daemon=True
    )
    spin_t.start()
    connected = ready_event.wait(timeout=30)
    stop_spin.set()
    spin_t.join()

    if not connected:
        print(f"{Fore.RED}  ✘ Bot failed to connect. Check TOKEN in bot_entry.py{Style.RESET_ALL}")
        sys.exit(1)

    loading_bar("Restoring schedules     ", 0.6)
    from commands.schedule import restore_schedules
    restore_schedules()

    time.sleep(0.3)
    clear()
    print_banner()

    return connected


# ────────────────────────────────────────────────────────────
#  Command loop
# ────────────────────────────────────────────────────────────
def main():
    startup()

    from bot_core import get_loop
    from commands.registry import dispatch

    loop = get_loop()

    print(f"  {Fore.YELLOW}Type  studio exit  to shut down.{Style.RESET_ALL}\n")

    while True:
        try:
            raw = prompt_spinner()
        except (KeyboardInterrupt, EOFError):
            raw = "studio exit"

        if not raw.strip():
            continue

        keep_running = dispatch(raw, loop)
        if not keep_running:
            print(f"\n{Fore.BLUE}  Shutting down Studio. Goodbye.{Style.RESET_ALL}\n")
            os._exit(0)


if __name__ == "__main__":
    main()
