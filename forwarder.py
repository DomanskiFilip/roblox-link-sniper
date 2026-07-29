"""
Roblox Link Forwarder - Discord Self-Bot
=================================================
Listens to a specific source Discord channel for messages containing keywords,
then forwards matching messages to a target destination channel.

⚠️ WARNING: Self-bots violate Discord's Terms of Service.
   Your account may be banned. Use at your own risk.
"""

import asyncio
import subprocess
import sys

USER_TOKEN = ""  # Replace with your Discord user token. Keep this private and secure!

# Channel where the bot listens for keywords
SOURCE_CHANNEL_ID = 1234567890123456789  # Replace with the source channel ID

# Channel where the bot will forward matching messages
DESTINATION_CHANNEL_ID = 9876543210987654321  # Replace with your destination channel ID

KEYWORDS = [
    "Glitched",
    "Glitch",
    "Dreamspace",
    "Cyberspace",
]

IGNORE_KEYWORDS = []

COOLDOWN_SECONDS = 3

# ─────────────────────────────────────────────

try:
    import discord
except ImportError:
    print("discord.py-self not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "discord.py-self"])
    import discord


class ForwarderClient(discord.Client):
    def __init__(self):
        super().__init__()
        self._last_forward = 0.0
        self._processed_ids: set[int] = set()

    async def on_ready(self):
        print(f"[READY] Logged in as {self.user} ({self.user.id})")
        
        src_channel = self.get_channel(SOURCE_CHANNEL_ID)
        dst_channel = self.get_channel(DESTINATION_CHANNEL_ID)

        if src_channel:
            print(f"[READY] Source channel: #{src_channel.name}")
        else:
            print(f"[WARN] Source channel {SOURCE_CHANNEL_ID} not cached yet — will still monitor incoming events.")

        if dst_channel:
            print(f"[READY] Destination channel: #{dst_channel.name}")
        else:
            print(f"[WARN] Destination channel {DESTINATION_CHANNEL_ID} not cached yet — will attempt fetch on forward.")

        print(f"[READY] Watching for keywords: {KEYWORDS}")
        print("-" * 50)

    async def on_message(self, message: discord.Message):
        # Ignore messages not coming from the target source channel
        if message.channel.id != SOURCE_CHANNEL_ID:
            return

        # Prevent duplicate processing
        if message.id in self._processed_ids:
            return

        text = message.content.lower()

        # Check ignored keywords
        for kw in IGNORE_KEYWORDS:
            if kw.lower() in text:
                print(f"[SKIP] Ignored keyword '{kw}' found in message {message.id}")
                self._processed_ids.add(message.id)
                return

        # Check target keywords
        matched_kw = [kw for kw in KEYWORDS if kw.lower() in text]
        if not matched_kw:
            return

        print(f"[HIT]  Message {message.id} matched keywords: {matched_kw}")

        # Cooldown check
        now = asyncio.get_event_loop().time()
        if now - self._last_forward < COOLDOWN_SECONDS:
            remaining = COOLDOWN_SECONDS - (now - self._last_forward)
            print(f"[COOL] Cooldown active, {remaining:.1f}s remaining. Skipping.")
            self._processed_ids.add(message.id)
            return

        self._last_forward = now
        self._processed_ids.add(message.id)

        # Retrieve destination channel
        dest_channel = self.get_channel(DESTINATION_CHANNEL_ID)
        if not dest_channel:
            try:
                dest_channel = await self.fetch_channel(DESTINATION_CHANNEL_ID)
            except Exception as e:
                print(f"[ERROR] Could not fetch destination channel: {e}")
                return

        # Construct and send payload
        try:
            forward_text = f"**[Keyword Match: {', '.join(matched_kw)}]**\n{message.content}"
            
            # Preserve attachments if any were sent with the message
            files = []
            for attachment in message.attachments:
                files.append(await attachment.to_file())

            await dest_channel.send(content=forward_text, files=files)
            print(f"[SUCCESS] Message {message.id} forwarded to channel {DESTINATION_CHANNEL_ID}")
        except Exception as e:
            print(f"[ERROR] Failed to send message: {e}")


def main():
    if USER_TOKEN in ("", "YOUR_DISCORD_USER_TOKEN_HERE"):
        print("ERROR: Please set your USER_TOKEN in the script before running.")
        sys.exit(1)

    if SOURCE_CHANNEL_ID == 1234567890123456789:
        print("ERROR: Please update SOURCE_CHANNEL_ID to your target channel ID.")
        sys.exit(1)

    if DESTINATION_CHANNEL_ID == 9876543210987654321:
        print("ERROR: Please set your DESTINATION_CHANNEL_ID before running.")
        sys.exit(1)

    client = ForwarderClient()
    print("[START] Starting Message Forwarder...")
    client.run(USER_TOKEN)


if __name__ == "__main__":
    main()
