# Roblox Link Sniper

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=FFD43B)
![Discord](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)
![Roblox](https://img.shields.io/badge/Roblox-E8141C?style=for-the-badge&logo=roblox&logoColor=white)

a self discord bot that monitors a Discord channel for messages containing specific keywords and automatically launches the Roblox deeplink to join the game instantly

---

## Features

-  watches for custom keywords like `Glitched`, `Dreamspace`, `Cyberspace` and more (egzample usage is SOL game)
-  converts Roblox web URLs to `roblox://` deeplinks and opens them automatically
-  skip messages containing certain words even if they match
-  prevents accidental multi-launches
-  works on Windows, macOS, and Linux
-  suports  `/games/` URLs and `/share?code=` private server links

---

## Requirements

- Python 3.8 or higher
- A Discord account
- `discord.py-self` package

---

## Installation

**1. Install Python** (if not already installed):

```
py installer is available separately or download from python.org
```
> ⚠️ Make sure to check **"Add Python to PATH"** during installation on Windows.

**2. Install the dependency:**

```bash
pip install discord.py-self
```

**3. Clone or download this repo:**

```bash
git clone https://github.com/DomanskiFilip/roblox-link-sniper.git
cd roblox-link-sniper
```

---

## Configuration

Open `roblox_sniper.py` and edit the values at the top:

```python
USER_TOKEN = "YOUR_DISCORD_USER_TOKEN_HERE"
TARGET_CHANNEL_ID = 1234567890123456789
KEYWORDS = ["Glitched", "Glitch", "Dreamspace", "Cyberspace"]
IGNORE_KEYWORDS = []
COOLDOWN_SECONDS = 3
```

### Getting your Discord Token

1. Open Discord in your **browser** at [discord.com](https://discord.com)
2. Press `F12` → **Network** tab
3. Filter requests by `api`
4. Click any request → **Headers** tab
5. Find the `authorization` header — that's your token

>  **Never share your token with anyone. It gives full access to your account.**

### Getting your Channel ID

1. Open Discord Settings → **Advanced** → enable **Developer Mode**
2. Right-click the channel you want to monitor
3. Click **Copy Channel ID**

---

## Usage

```bash
python roblox_sniper.py
```

or

```bash
py roblox_sniper.py
```

or just double click the file

**Example output:**

```
[START] Starting Roblox Link Sniper...
[READY] Logged in as YourName#1234 (123456789)
[READY] Monitoring channel: #drops in CoolServer
[READY] Watching for keywords: ['Glitched', 'Glitch', 'Dreamspace', 'Cyberspace']
--------------------------------------------------
[HIT]   Message 987654321 matched keywords: ['Glitched']
        Content: Glitched server drop! https://www.roblox.com/games/123/GameName?privateServerLinkCode=abc123
[GO]    Launching deeplink: roblox://placeID=123&linkCode=abc123
```

---

## How It Works

1. Logs into Discord using your user token via `discord.py-self`
2. Listens for new messages in the specified channel
3. Checks if the message contains any of your configured keywords
4. Skips the message if it contains any ignore keywords
5. Extracts the Roblox URL from the message
6. Converts it to a `roblox://` deeplink
7. Opens the deeplink on your system to auto-join the game

---

## ⚠️ Disclaimer

> **Using a self-bot (logging into Discord with a user account token via automation) violates [Discord's Terms of Service](https://discord.com/terms). Your account may be suspended or permanently banned. Use this at your own risk. I take no responsibility for any account actions taken by Discord. I made it for a friend who understands potential risks**

---
