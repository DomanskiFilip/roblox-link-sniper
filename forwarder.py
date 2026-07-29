"""
Roblox Link Forwarder - Discord Self-Bot
========================================================================
Fixed: Solves TypeError where send() doesn't accept 'embeds' argument.

⚠️ WARNING: Self-bots violate Discord's Terms of Service.
   Your account may be banned. Use at your own risk.
"""

import asyncio
import subprocess
import sys

USER_TOKEN = ""  # Replace with your Discord user token

SOURCE_CHANNEL_IDS = [
    1234567890123456789,
    # Add your source channel IDs here
]

DESTINATION_CHANNEL_ID = 1122334455667788990  # Replace with your destination channel ID

KEYWORDS = [
    "glitched",
    "glitch",
    "dreamspace",
    "cyberspace",
]

IGNORE_KEYWORDS = []

COOLDOWN_SECONDS = 1

# ─────────────────────────────────────────────

try:
    import discord
except ImportError:
    print("discord.py-self not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "discord.py-self"])
    import discord


def extract_full_text(message: discord.Message) -> str:
    """Safely extracts all text from content and embeds for keyword matching."""
    parts = []
    if message.content:
        parts.append(str(message.content))

    for embed in message.embeds:
        if embed.title:
            parts.append(str(embed.title))
        if embed.description:
            parts.append(str(embed.description))
        if embed.author and embed.author.name:
            parts.append(str(embed.author.name))
        if embed.footer and embed.footer.text:
            parts.append(str(embed.footer.text))
        
        for field in embed.fields:
            if field.name:
                parts.append(str(field.name))
            if field.value:
                parts.append(str(field.value))

    return " ".join(parts)


def sanitize_embed(original_embed: discord.Embed) -> discord.Embed:
    """
    Sanitizes embed structure by parsing raw dictionary structures.
    Prevents HTTP 50035 (Invalid Form Body) errors.
    """
    data = original_embed.to_dict()
    clean_data = {}

    if "title" in data:
        clean_data["title"] = str(data["title"])[:256]
    if "description" in data:
        clean_data["description"] = str(data["description"])[:4096]
    if "url" in data and str(data["url"]).startswith("http"):
        clean_data["url"] = str(data["url"])
    if "color" in data:
        clean_data["color"] = data["color"]

    # Clean Author
    if "author" in data and isinstance(data["author"], dict):
        author = {}
        if "name" in data["author"]:
            author["name"] = str(data["author"]["name"])[:256]
        if "icon_url" in data["author"] and str(data["author"]["icon_url"]).startswith("http"):
            author["icon_url"] = str(data["author"]["icon_url"])
        if "url" in data["author"] and str(data["author"]["url"]).startswith("http"):
            author["url"] = str(data["author"]["url"])
        if author.get("name"):
            clean_data["author"] = author

    # Clean Footer
    if "footer" in data and isinstance(data["footer"], dict):
        footer = {}
        if "text" in data["footer"]:
            footer["text"] = str(data["footer"]["text"])[:2048]
        if "icon_url" in data["footer"] and str(data["footer"]["icon_url"]).startswith("http"):
            footer["icon_url"] = str(data["footer"]["icon_url"])
        if footer.get("text"):
            clean_data["footer"] = footer

    # Clean Images
    if "thumbnail" in data and isinstance(data["thumbnail"], dict):
        if str(data["thumbnail"].get("url", "")).startswith("http"):
            clean_data["thumbnail"] = {"url": str(data["thumbnail"]["url"])}

    if "image" in data and isinstance(data["image"], dict):
        if str(data["image"].get("url", "")).startswith("http"):
            clean_data["image"] = {"url": str(data["image"]["url"])}

    # Clean Fields
    if "fields" in data and isinstance(data["fields"], list):
        clean_fields = []
        for field in data["fields"]:
            if isinstance(field, dict):
                name = str(field.get("name", "")).strip() or "\u200b"
                value = str(field.get("value", "")).strip() or "\u200b"
                clean_fields.append({
                    "name": name[:256],
                    "value": value[:1024],
                    "inline": bool(field.get("inline", False))
                })
        if clean_fields:
            clean_data["fields"] = clean_fields

    return discord.Embed.from_dict(clean_data)


def embed_to_plain_text(embed: discord.Embed) -> str:
    """
    Fallback converter: converts an embed structure into clean, formatted text.
    """
    lines = []
    if embed.title:
        lines.append(f"**{embed.title}**")
    if embed.description:
        lines.append(embed.description)

    for field in embed.fields:
        lines.append(f"**{field.name}**\n{field.value}")

    if embed.footer and embed.footer.text:
        lines.append(f"_\n{embed.footer.text}_")

    return "\n\n".join(lines)


class MultiChannelForwarderClient(discord.Client):
    def __init__(self):
        super().__init__()
        self._last_forward = 0.0
        self._processed_ids: set[int] = set()

    async def on_ready(self):
        print(f"[READY] Logged in as {self.user} ({self.user.id})")
        print(f"[READY] Monitoring {len(SOURCE_CHANNEL_IDS)} channels...")
        print(f"[READY] Watching for keywords: {KEYWORDS}")
        print("-" * 50)

    async def process_message_event(self, message: discord.Message, event_type: str = "CREATE"):
        if message.channel.id not in SOURCE_CHANNEL_IDS:
            return

        full_text = extract_full_text(message)
        text_lower = full_text.lower()

        for kw in IGNORE_KEYWORDS:
            if kw.lower() in text_lower:
                return

        matched_kw = [kw for kw in KEYWORDS if kw.lower() in text_lower]
        if not matched_kw:
            return

        if message.id in self._processed_ids:
            return

        channel_name = getattr(message.channel, 'name', str(message.channel.id))
        print(f"[HIT] ({event_type}) Message {message.id} in #{channel_name} matched: {matched_kw}")

        now = asyncio.get_event_loop().time()
        if now - self._last_forward < COOLDOWN_SECONDS:
            print("[COOL] Cooldown active. Skipping.")
            return

        self._last_forward = now
        self._processed_ids.add(message.id)

        dest_channel = self.get_channel(DESTINATION_CHANNEL_ID)
        if not dest_channel:
            try:
                dest_channel = await self.fetch_channel(DESTINATION_CHANNEL_ID)
            except Exception as e:
                print(f"[ERROR] Could not fetch destination channel: {e}")
                return

        try:
            header = f"**[Match: {', '.join(matched_kw)}]** | *From #{channel_name}*"
            base_content = f"{header}\n{message.content}" if message.content else header

            # Clean and sanitize embeds
            cleaned_embeds = []
            for e in message.embeds:
                try:
                    cleaned_embeds.append(sanitize_embed(e))
                except Exception as embed_err:
                    print(f"[WARN] Failed to sanitize embed: {embed_err}")

            files = []
            for attachment in message.attachments:
                try:
                    files.append(await attachment.to_file())
                except Exception:
                    pass

            # Attempt 1: Try sending with 'embeds=' (standard discord.py list format)
            try:
                if cleaned_embeds:
                    await dest_channel.send(content=base_content, embeds=cleaned_embeds, files=files)
                else:
                    await dest_channel.send(content=base_content, files=files)
                print(f"[SUCCESS] Message {message.id} forwarded via embeds list!")
                return

            except TypeError:
                # 'embeds' keyword is not supported in your library version, falling through...
                pass
            except discord.HTTPException as http_err:
                print(f"[WARN] Failed sending with 'embeds=' ({http_err}). Trying single embed/text fallback...")

            # Attempt 2: Try sending with 'embed=' (singular format for libraries that only accept single embed)
            if cleaned_embeds:
                try:
                    await dest_channel.send(content=base_content, embed=cleaned_embeds[0], files=files)
                    print(f"[SUCCESS] Message {message.id} forwarded via single embed!")
                    return
                except (TypeError, discord.HTTPException) as single_err:
                    print(f"[WARN] Single embed dispatch failed ({single_err}). Converting to plain text...")

            # Attempt 3: Guaranteed Text-Only Fallback
            embed_text_blocks = [embed_to_plain_text(e) for e in cleaned_embeds if embed_to_plain_text(e)]
            fallback_content = base_content
            if embed_text_blocks:
                fallback_content += "\n\n" + "\n---\n".join(embed_text_blocks)

            await dest_channel.send(content=fallback_content[:2000], files=files)
            print(f"[SUCCESS] Message {message.id} forwarded via text-only fallback!")

        except Exception as e:
            print(f"[ERROR] Critical failure when forwarding: {e}")

    async def on_message(self, message: discord.Message):
        await self.process_message_event(message, event_type="NEW")

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        await self.process_message_event(after, event_type="EDIT")


def main():
    if USER_TOKEN in ("", "YOUR_DISCORD_USER_TOKEN_HERE"):
        print("ERROR: Please set your USER_TOKEN in the script before running.")
        sys.exit(1)

    client = MultiChannelForwarderClient()
    print("[START] Starting Multi-Channel Embed Forwarder...")
    client.run(USER_TOKEN)


if __name__ == "__main__":
    main()
