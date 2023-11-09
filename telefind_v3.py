from telethon import TelegramClient, events
from api_keys import Tokens
from request_gpt import RequestGpt
from get_tinkoff_v3 import Trade
import asyncio

api_id = Tokens.api_tele_id
api_hash = Tokens.api_tele_hash
phone_number = Tokens.tele_number

# Инициализация глобальных переменных
last_message_id = None
last_message_text = None

async def get_channel(client):
    # Получаем список диалогов
    dialogs = await client.get_dialogs()
    # Ищем канал, который находится на втором месте сверху в списке диалогов
    for i, dialog in enumerate(dialogs, start=1):
        if dialog.is_channel:
            if i == 2:
                print(dialog.name)
                return dialog.entity

async def main():
    async with TelegramClient(phone_number, api_id, api_hash) as client:
        channel_entity = await get_channel(client)

        @client.on(events.NewMessage(chats=[channel_entity]))
        async def new_message_handler(event):
            global last_message_id, last_message_text
            new_message = event.message
            # Проверяем, не является ли это сообщение редактированием предыдущего
            if new_message.id != last_message_id:
                # Обновляем информацию о последнем сообщении
                last_message_id = new_message.id
                last_message_text = new_message.text if new_message.text else ""
                print(f"Новое сообщение: {last_message_text}")
                # Запускаем задачу для отслеживания изменений в сообщении
                client.loop.create_task(track_message_editing(client, new_message))

        async def track_message_editing(client, message):
            global last_message_text
            while True:
                # Ждем одну секунду перед следующей проверкой
                await asyncio.sleep(0.2)
                # Получаем обновленное сообщение
                updated_message = await client.get_messages(channel_entity, ids=message.id)
                # Проверяем, является ли результат списком сообщений
                if isinstance(updated_message, list):
                    updated_message = updated_message[0]
                # Проверяем, изменился ли текст сообщения
                if updated_message.text != last_message_text or '#сделка' in last_message_text:
                    print(f"Сообщение изменилось или сообщение готово: {updated_message.text}")
                    last_message_text = updated_message.text
                    # Обрабатываем измененное сообщение
                    if '#сделка' in last_message_text:
                        # Обрабатываем сделку
                        prompt = ("исходя из текста выведи формулу:company ticker=Buy Sell Short, без лишних слов, твой ответ должен составлять только из формулы. Текст: " + last_message_text).replace("\r", " ").replace("\n", " ")
                        response = gpt_request.request(prompt=prompt)
                        print(response)
                        # Создаем словарь для обработки заказов
                        result = {}
                        lines = response.split('\n')
                        for line in lines:
                            parts = line.strip().split('=')
                            if len(parts) == 2:
                                key = parts[0].strip()
                                value = parts[1].strip()
                                result[key] = value
                        # Обрабатываем заказы
                        Trade.process_orders(result=result, sandbox_mode=True)
                        break

                # Если ID последнего сообщения изменился, прекращаем отслеживание
                if updated_message.id != last_message_id:
                    break

        # Запускаем клиент
        await client.start()
        await client.run_until_disconnected()

if __name__ == '__main__':
    gpt_request = RequestGpt()
    asyncio.run(main())


#task
# stop loss price error