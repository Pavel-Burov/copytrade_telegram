from telethon import TelegramClient, events
from api_keys import Tokens
from request_gpt import RequestGpt
from get_tinkoff_v2 import Trade
import asyncio

api_id = Tokens.api_tele_id
api_hash = Tokens.api_tele_hash
phone_number = Tokens.tele_number


async def get_channel(client):
    dialogs = await client.get_dialogs()
    for i, dialog in enumerate(dialogs, start=1):
        if dialog.is_channel:
            if i == 2: # ПО СЧЕТУ СВЕРХУ 
                print(dialog.name)
                return dialog.entity

async def main():
    async with TelegramClient(phone_number, api_id, api_hash) as client:

        # Получаем ID канала
        channel_id = await get_channel(client)

        # Обработчик для новых сообщений из определенного чата
        @client.on(events.NewMessage(chats=[channel_id]))
        async def new_message_handler(event):
            # Получаем сообщение
            message = event.message.to_dict()
            
            # Проверяем, что сообщение текстовое
            if 'message' in message and message['message']:
                if '#сделка' in message['message']:
                    # Выводим сообщение в консоль
                    # print(f"Новое сообщение из чата {channel_id.title}: {message['message']}")
                    prompt = (f"исходя из текста выведи формулу:company ticker=Buy or Sell, без лишних слов, твой ответ должен составлять только из формулы. Текст: {message["message"]}".replace("\r", " ")).replace("\n"," ")
                    response = gpt_request.request(prompt=prompt)
                    # создание словаря
                    result = {}
                    # Разбиваем строку на строки по переводам строк
                    lines = response.split('\n')
                    print(lines)
                    for line in lines:
                        # Разбиваем каждую строку по знаку равенства 
                        print(line)
                        parts = line.strip().split('=')
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            result[key] = value
                    print(result)
                    # Ticker=Buy or Sell


    # Запускаем клиента
    await client.start()
    await client.run_until_disconnected()

# Запускаем асинхронный main
if __name__ == '__main__':
    gpt_request = RequestGpt()
    asyncio.run(main())


# task
# add stop loss