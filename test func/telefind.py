from telethon.sync import TelegramClient
import re, asyncio
from api_keys import Tokens
from yaml import Token

api_id = Tokens.api_tele_id
api_hash = Tokens.api_tele_hash
phone_number = Tokens.tele_number
channel = "kwefqgfyuwegfyug"
tag = "ALRS"
    
async def parse_message(client, channel, tag):
    async for message in client.iter_messages(channel):
        if message.text and (tag in message.text):
            text = message.text
            Tokens.prompt = text
            print(text)
            
            hashtags = re.findall(r'#\w+', message.text)
            usernames = re.findall(r'@[\w_]+', message.text)
            
            # if hashtags:
            #     print("Hashtags:", ", ".join(hashtags))
            
            # if usernames:
            #     print("Mentioned Usernames:", ", ".join(usernames))
            
async def main():
    async with TelegramClient(phone_number, api_id, api_hash) as client:
        while True:
            await parse_message(client, channel=channel, tag=tag)
            await asyncio.sleep(10)


if __name__ == '__main__':
    asyncio.run(main())
#WORK