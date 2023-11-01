from telegram import InputMessageContent
from telethon.sync import TelegramClient

api_id = 20851124
api_hash = '8ed3a8116f93e2daa1ffc936a0900dd7'
phone_number = '6288290550110'

channel = "kwefqgfyuwegfyug"

client = TelegramClient(phone_number, api_id, api_hash)

async def get_pinned_message():
    async with client:
        # Replace 'your_channel_username' with the actual username of your channel
        channel_entity = await client.get_entity(channel)

        # Retrieve pinned message from the channel
        async for message in client.iter_messages(channel_entity, filter=InputMessageContent):
            print(message.text)

if __name__ == '__main__':
    client.loop.run_until_complete(get_pinned_message())
    #NO WORK!!!!!!!!!!!!!!!