"""
DarkForums.su Leaks Tracker made by SwagMix8 (Go check t.me/Joytechlegion)
"""
import requests
from bs4 import BeautifulSoup
import time
import json
import os
from datetime import datetime
import re
import asyncio
from telegram import Bot
from telegram.error import TelegramError

# Config (You can Change the State File and Interval if u want)
URL = "https://darkforums.su/Forum-Databases"
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"
CHECK_INTERVAL = 10  # This time is on seconds
STATE_FILE = "last_leaks_state.json"

class LeakScraper:
    def __init__(self, url, bot_token, chat_id):
        self.url = url
        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
    def fetch_page(self):
        try:
            response = self.session.get(self.url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return None
    
    def extract_threads(self, html):
        """HTML Parser / ONLY EDIT IF THE SITE CHANGES"""
        soup = BeautifulSoup(html, 'html.parser')
        threads = []
        
        thread_rows = soup.find_all('tr', class_='inline_row')
        
        for row in thread_rows:
            try:
                title_elem = row.find('span', class_=re.compile(r'subject_'))
                if not title_elem:
                    continue
                    
                title_link = title_elem.find('a')
                if not title_link:
                    continue
                    
                title = title_link.get_text(strip=True)
                thread_url = title_link.get('href')
                if thread_url and not thread_url.startswith('http'):
                    thread_url = f"https://darkforums.su/{thread_url}"

                prefix_elem = row.find('span', class_='rf_tprefix')
                prefix = prefix_elem.get_text(strip=True) if prefix_elem else ""

                author_elem = row.find('div', class_='author')
                if author_elem:
                    author_link = author_elem.find('a')
                    author = author_link.get_text(strip=True) if author_link else "Unknown"
                else:
                    author = "Unknown"

                date_elem = row.find('span', class_='forum-display__thread-date')
                date = date_elem.get_text(strip=True) if date_elem else ""

                replies_elem = row.find('td', align='center')
                if replies_elem:
                    replies_link = replies_elem.find('a')
                    replies = replies_link.get_text(strip=True) if replies_link else "0"
                    replies = replies.replace(',', '')
                else:
                    replies = "0"
                
                views_elem = None
                for td in row.find_all('td', align='center'):
                    if td.get_text(strip=True).isdigit() and len(td.get_text(strip=True)) > 2:
                        views_elem = td
                        break
                views = views_elem.get_text(strip=True) if views_elem else "0"
                views = views.replace(',', '')

                lastpost_elem = row.find('td', class_='forumdisplay_regular', style='white-space: nowrap; text-align: right;')
                if lastpost_elem:
                    lastpost_text = lastpost_elem.get_text(strip=True)
                    lastpost_match = re.search(r'(\d+\s+\w+.*?ago|\d+-\d+-\d+.*?[AP]M)', lastpost_text)
                    lastpost = lastpost_match.group(1) if lastpost_match else ""
                else:
                    lastpost = ""
                
                thread_info = {
                    'title': title,
                    'url': thread_url,
                    'prefix': prefix,
                    'author': author,
                    'date': date,
                    'replies': int(replies) if replies.isdigit() else 0,
                    'views': int(views) if views.isdigit() else 0,
                    'lastpost': lastpost,
                    'timestamp': time.time()
                }
                
                threads.append(thread_info)
                
            except Exception as e:
                print(f"Error parsing thread row: {e}")
                continue
        
        return threads
    
    def get_latest_threads(self, threads, limit=15):
        return threads[:limit]
    
    def load_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def save_state(self, state):
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump(state, f, indent=2)
        except IOError as e:
            print(f"Error saving state: {e}")
    
    def is_new_leak(self, thread, previous_threads):
        for prev_thread in previous_threads:
            if prev_thread.get('url') == thread.get('url'):
                return False
        return True
    
    def format_telegram_message(self, thread):
        """You can edit this if you dont like the output"""
        prefix_tag = f"[{thread['prefix']}] " if thread['prefix'] else ""
        
        message = f"🔴 *NEW LEAK DETECTED!*\n\n"
        message += f"📌 *Title:* {prefix_tag}{thread['title']}\n"
        message += f"👤 *Author:* {thread['author']}\n"
        message += f"💬 *Replies:* {thread['replies']}\n"
        message += f"👁️ *Views:* {thread['views']}\n"
        message += f"🕐 *Last Post:* {thread['lastpost']}\n"
        message += f"🔗 *Link:* {thread['url']}\n\n"
        message += f"⏰ *Detected:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return message
    
    async def send_telegram_notification(self, message):
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=False
            )
            print(f"Telegram notification sent at {datetime.now()}")
        except TelegramError as e:
            print(f"Telegram error: {e}")
    
    async def check_and_notify(self):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking for new leaks...")
        
        # Fetch page
        html = self.fetch_page()
        if not html:
            print("Failed to fetch page")
            return
        
        # Extract threads
        all_threads = self.extract_threads(html)
        if not all_threads:
            print("No threads found")
            return
        
        # Here gets the lasts 15 leaks, if you want can filter it to get more or less
        latest_threads = self.get_latest_threads(all_threads, 15)
        
        previous_state = self.load_state()
        previous_threads = previous_state.get('threads', [])

        new_threads = []
        for thread in latest_threads:
            if self.is_new_leak(thread, previous_threads):
                new_threads.append(thread)

        if new_threads:
            print(f"Found {len(new_threads)} new leaks!")
            for thread in reversed(new_threads):
                message = self.format_telegram_message(thread)
                await self.send_telegram_notification(message)
                await asyncio.sleep(1)  # Small delay between messages to avoid rate limiting
        else:
            print("No new leaks found")

        current_state = {
            'threads': latest_threads,
            'last_check': datetime.now().isoformat()
        }
        self.save_state(current_state)
    
    async def run_forever(self):
        """Run the scraper continuously"""
        print(f"Leak scraper started. Checking {self.url} every {CHECK_INTERVAL} seconds")
        print(f"Sending notifications to Telegram chat ID: {self.chat_id}")
        
        # Do initial check immediately
        await self.check_and_notify()
        
        # Then loop
        while True:
            await asyncio.sleep(CHECK_INTERVAL)
            await self.check_and_notify()

def main():

    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("ERROR: Please set your Telegram bot token in the TELEGRAM_BOT_TOKEN variable")
        print("Get a bot token from @BotFather on Telegram")
        return
    
    if TELEGRAM_CHAT_ID == "YOUR_CHAT_ID_HERE":
        print("ERROR: Please set your Telegram chat ID in the TELEGRAM_CHAT_ID variable")
        print("Get your chat ID by sending a message to @userinfobot on Telegram")
        return
    
    scraper = LeakScraper(URL, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    
    # Run the scraper
    try:
        asyncio.run(scraper.run_forever())
    except KeyboardInterrupt:
        print("\nScraper stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
