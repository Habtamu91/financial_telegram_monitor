import os
import re
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from telethon import TelegramClient, errors

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

# Load from root .env
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env')) 

class TelegramScraper:
    def __init__(self):
        self.api_id = os.getenv('API_ID')
        self.api_hash = os.getenv('API_HASH')
        
        if not self.api_id or not self.api_hash:
            raise ValueError("Missing Telegram API credentials in .env file")
        
        self.client = TelegramClient('anon', int(self.api_id), self.api_hash)
        
        # Path to root data/raw folder
        self.data_dir = os.path.join(
            os.path.dirname(__file__), 
            '../../data/raw'
        )
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Medical product keywords
        self.keywords = [
            "paracetamol", "ibuprofen", "vaccine",
            "antibiotic", "cream", "pills"
        ]

    async def scrape_channel(self, channel_name):
        try:
            entity = await self.client.get_entity(channel_name)
            logging.info(f"Scraping {channel_name} (ID: {entity.id})")
            
            messages = []
            async for message in self.client.iter_messages(entity, limit=300):
                if message.text:
                    mentions = [
                        kw for kw in self.keywords 
                        if kw in message.text.lower()
                    ]
                    
                    messages.append({
                        "id": message.id,
                        "text": re.sub(r'http\S+', '', message.text),
                        "date": message.date.isoformat(),
                        "mentions": mentions,
                        "has_media": bool(message.media),
                        "channel": channel_name
                    })
            
            if messages:
                filename = os.path.join(
                    self.data_dir, 
                    f"{channel_name}_{datetime.now().date()}.json"
                )
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(messages, f, indent=2, ensure_ascii=False)
                logging.info(f"Saved {len(messages)} messages to {filename}")
                return True
            
            logging.warning(f"No messages found in {channel_name}")
            return False
            
        except errors.UsernameNotOccupiedError:
            logging.error(f"Channel @{channel_name} doesn't exist")
        except errors.ChannelPrivateError:
            logging.error(f"Channel @{channel_name} is private")
        except Exception as e:
            logging.error(f"Error scraping @{channel_name}: {str(e)}")
        return False

async def main():
    scraper = TelegramScraper()
    async with scraper.client:
        with open('channels.txt', 'r') as f:
            channels = [line.strip() for line in f if line.strip()]
        
        for channel in channels:
            await scraper.scrape_channel(channel)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())