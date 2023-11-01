import asyncio
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

API_ID = 20851124
API_HASH = "8ed3a8116f93e2daa1ffc936a0900dd7"
phone_number = "+6288290550110"

# Создаем строку сессии и сохраняем ее в файл
with TelegramClient(StringSession(), API_ID, API_HASH, loop=asyncio.get_event_loop()) as client:
    print(client.session.save())
