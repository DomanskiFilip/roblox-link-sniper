"""
Roblox Link Sniper - Discord Self-Bot
======================================
Listens to a specific Discord channel for messages containing keywords,
then auto-launches the Roblox deeplink found in the message.

⚠️  WARNING: Self-bots violate Discord's Terms of Service.
    Your account may be banned. Use at your own risk.
"""

import re
import subprocess
import sys
import platform
import asyncio

USER_TOKEN = "" # Replace with your Discord user token. Keep this private and secure!

# best way to get:
# on the discord website open inspect tab
# go to the network tab
# click open discord in browser
# filter for api
# click on any api request and go to the request headers tab
# scroll down to the authorization header and copy the value (thats your discord user token)

TARGET_CHANNEL_ID = 1234567890123456789  # Replace with the ID of the channel you want to monitor

KEYWORDS = [
    "Glitched",
    "Glitch",
    "Dreamspace",
    "Cyberspace",
]

IGNORE_KEYWORDS = [
]

COOLDOWN_SECONDS = 3

# ─────────────────────────────────────────────

try:
    import discord
except ImportError:
    print("discord.py-self not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "discord.py-self"])
    import discord

ROBLOX_LINK_RE = re.compile(
    r"https?://(?:www\.)?roblox\.com/"
    r"(?:games/(\d+)/[^\s?/]+(?:\?[^\s]*privateServerLinkCode=([^&\s]+))?|share\?code=([A-Za-z0-9_-]+))",
    re.IGNORECASE
)


def convert_to_deeplink(url: str) -> str | None:
    """Convert a Roblox web URL to a roblox:// deeplink."""
    m = re.match(r"https?://(?:www\.)?roblox\.com/share\?code=([^&\s]+)", url, re.IGNORECASE)
    if m:
        return f"roblox://navigation/share_links?code={m.group(1)}&type=Server&pid=share&is_retargeting=true"
    m = re.match(r"https?://(?:www\.)?roblox\.com/games/(\d+)/[^\s?]+(?:\?[^\s]*privateServerLinkCode=([^&\s]+))?", url, re.IGNORECASE)
    if m:
        place_id = m.group(1)
        link_code = m.group(2)
        if link_code:
            return f"roblox://placeID={place_id}&linkCode={link_code}"
        return f"roblox://placeID={place_id}"
    return None


def launch_deeplink(deeplink: str):
    """Open the Roblox deeplink to auto-join the game."""
    system = platform.system()
    print(f"[LAUNCH] Opening: {deeplink}")
    try:
        if system == "Windows":
            import os
            os.startfile(deeplink)
        elif system == "Darwin":
            subprocess.Popen(["open", deeplink])
        else:
            subprocess.Popen(["xdg-open", deeplink])
    except Exception as e:
        print(f"[ERROR] Failed to launch deeplink: {e}")


class SniperClient(discord.Client):
    def __init__(self):
        super().__init__()
        self._last_launch = 0.0
        self._processed_ids: set[int] = set()

    async def on_ready(self):
        print(f"[READY] Logged in as {self.user} ({self.user.id})")
        channel = self.get_channel(TARGET_CHANNEL_ID)
        if channel:
            print(f"[READY] Monitoring channel: #{channel.name} in {channel.guild.name}")
        else:
            print(f"[WARN] Channel {TARGET_CHANNEL_ID} not found in cache yet — will still receive messages.")
        print(f"[READY] Watching for keywords: {KEYWORDS}")
        print("-" * 50)

    async def on_message(self, message: discord.Message):
        if message.channel.id != TARGET_CHANNEL_ID:
            return

        if message.id in self._processed_ids:
            return

        text = message.content.lower()

        for kw in IGNORE_KEYWORDS:
            if kw.lower() in text:
                print(f"[SKIP] Ignored keyword '{kw}' found in message {message.id}")
                self._processed_ids.add(message.id)
                return

        matched_kw = [kw for kw in KEYWORDS if kw.lower() in text]
        if not matched_kw:
            return

        print(f"[HIT]  Message {message.id} matched keywords: {matched_kw}")
        print(f"       Content: {message.content[:120]}")

        links = ROBLOX_LINK_RE.findall(message.content)
        raw_links = ROBLOX_LINK_RE.findall(message.content)

        full_links = ROBLOX_LINK_RE.finditer(message.content)
        roblox_urls = [m.group(0) for m in full_links]

        if not roblox_urls:
            print(f"[SKIP] No Roblox link found in message {message.id}")
            self._processed_ids.add(message.id)
            return

        if len(roblox_urls) > 1:
            print(f"[SKIP] Multiple Roblox links found ({len(roblox_urls)}), skipping to avoid wrong join.")
            self._processed_ids.add(message.id)
            return

        url = roblox_urls[0]
        deeplink = convert_to_deeplink(url)

        if not deeplink:
            print(f"[ERROR] Could not convert URL to deeplink: {url}")
            self._processed_ids.add(message.id)
            return

        now = asyncio.get_event_loop().time()
        if now - self._last_launch < COOLDOWN_SECONDS:
            remaining = COOLDOWN_SECONDS - (now - self._last_launch)
            print(f"[COOL] Cooldown active, {remaining:.1f}s remaining. Skipping.")
            self._processed_ids.add(message.id)
            return

        self._last_launch = now
        self._processed_ids.add(message.id)

        print(f"[GO]   Launching deeplink: {deeplink}")
        launch_deeplink(deeplink)


def main():
    if USER_TOKEN == "YOUR_DISCORD_USER_TOKEN_HERE":
        print("ERROR: Please set your USER_TOKEN in the script before running.")
        print("See the instructions at the top of the file.")
        sys.exit(1)

    if TARGET_CHANNEL_ID == 1234567890123456789:
        print("ERROR: Please set your TARGET_CHANNEL_ID in the script before running.")
        sys.exit(1)

    client = SniperClient()
    print("[START] Starting Roblox Link Sniper...")
    client.run(USER_TOKEN)


if __name__ == "__main__":
    main()
