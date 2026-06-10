# DarkForums Leak Tracker

A Python-based monitoring tool designed to track newly published database leaks on **darkforums.su** and deliver real-time notifications through Telegram.

## Overview

DarkForums Leak Tracker continuously monitors the **Databases** section of DarkForums, identifies newly created leak threads, and alerts users as soon as new content becomes available. The project is intended for **research, threat intelligence, and cybersecurity awareness purposes**, providing a simple way to stay informed about emerging leak activity.

The scraper maintains a local state file to avoid duplicate notifications and only reports threads that have not been previously detected.

## Features

* Real-time monitoring of the DarkForums databases section.
* Automatic detection of newly published leak threads.
* Telegram notifications with detailed leak information.
* Local state management to prevent duplicate alerts.
* Extraction of useful metadata, including:

  * Thread title
  * Author
  * Reply count
  * View count
  * Last activity timestamp
  * Direct thread link
* Continuous operation with configurable polling intervals.
* Lightweight and easy to deploy.

## Requirements

* Python 3.9+
* Telegram Bot Token
* Telegram Chat ID

## Installation

```bash
git clone https://github.com/NexoProyect/DarkForums-Tracker.git
cd darkforums-leak-tracker

pip install requests beautifulsoup4 python-telegram-bot
```

Also you can get the file directly from [Releases](https://github.com/NexoProyect/DarkForums-Tracker/releases)

## Configuration

Edit the following variables inside the script:

```python
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"
CHECK_INTERVAL = 10  # seconds
```

To obtain a Telegram bot token:

1. Open Telegram.
2. Contact `@BotFather`.
3. Create a new bot using `/newbot`.
4. Copy the generated token.

To obtain your chat ID:

1. Send a message to `@userinfobot`.
2. Copy your Chat ID from the bot's response.

## Usage

Run the tracker using:

```bash
python main.py
```

Once started, the application will:

1. Retrieve the latest threads from the configured forum section.
2. Compare them against the previously saved state.
3. Identify newly published leaks.
4. Send Telegram notifications for each new thread detected.
5. Repeat the process at the configured interval.

## Example Notification

```
🔴 NEW LEAK DETECTED!

📌 Title: [DATABASE] Example Leak
👤 Author: ExampleUser
💬 Replies: 15
👁️ Views: 320
🕐 Last Post: 5 minutes ago
🔗 Link: https://darkforums.su/...

⏰ Detected: 2026-06-10 14:35:22
```

## Disclaimer

This project is provided **for educational, research, and threat intelligence purposes only**. The software is intended solely to monitor publicly accessible information and should not be used to facilitate unauthorized access, distribution of stolen data, or any activity that violates applicable laws or regulations. Users are solely responsible for ensuring that their use of this project complies with all relevant legal and ethical requirements.

## License

This project is released under the **GNU GENERAL PUBLIC LICENSE**. See the `LICENSE` file for additional details.
