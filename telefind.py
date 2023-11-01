from telethon.sync import TelegramClient
import re, asyncio, time
from api_keys import Tokens
from request_gpt import RequestGpt
from get_tinkoff_v2 import Trade


import logging, asyncio, sys
from aiogram import Bot, Dispatcher, types, executor
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.channels import JoinChannelRequest



# async def start_telegram_bot():
#     API_TOKEN = Tokens.tele_bot  # Замените на свой токен, полученный от BotFather

#     # Инициализируем бот и диспетчер
#     bot = Bot(token=API_TOKEN)
#     dp = Dispatcher(bot)
#     logging.basicConfig(level=logging.INFO)

#     # Обработчик команды /sell
#     @dp.message_handler(commands=['sell'])
#     async def sell(message: types.Message):
#         try:
#             Trade.sell_all()
#         except Exception as ex:
#             await message.answer(f"Ошибка продажи: {ex}")
#             print((f"Ошибка продажи: {ex}"))
            
#         await message.answer("Успешно все продалось")
#         sys.exit()
        

api_id = Tokens.api_tele_id
api_hash = Tokens.api_tele_hash
phone_number = Tokens.tele_number

channel = "kwefqgfyuwegfyug"
tag = "Мои позы:"

gpt_request = RequestGpt()

# Действительные позиции на брокерском счете
real_positions = {"":0}

async def parse_message(client, channel, tag, real_position):
    async for message in client.iter_messages(channel):
        if message.text and (tag in message.text):
            #text its promt for chatgpt
            text = f"Заполни формулу, следуя табуляции и строчных символов по формуле, твой ответ не должен быть больше формулы, но может быть несколько формул в каждой строке, без посторонних слов, чистый ответ, исходя из текста. Формула:Тикер Акций Компании=Процентное число. Пример:ALRS=18. Текст: {message.text}"
            text = text.replace("\r", " ")
            text = text.replace("\n"," ")
            # message.text its message from telegram
            print(message.text)
            #response chatgpt
            response = gpt_request.request(prompt=text)
            print(f"gpt reponse: {response}")
            #создание словаря
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
            #новые позиции
            print(result)
            #словарь Тикер:процент от капитала
            time.sleep(20)
            # from tinkoff import process_orders
            #buy or sell
            Trade.process_orders(order_dict=result, real_positions=real_position, sandbox_mode=True)
            # update current positions
            real_positions = result


async def start():
    # await start_telegram_bot()
    
    async with TelegramClient(phone_number, api_id, api_hash) as client:
        while True:
            await parse_message(client, channel=channel, tag=tag, real_position=real_positions)
            await asyncio.sleep(20)


if __name__ == '__main__':
    asyncio.run(start())
    # asyncio.gather(main(), start_telegram_bot())
#WORK


#TASK
# Добавить обработчик не найденнгого тэга и не именнеенроого сообщенияы
# Карче нужно в цикле находить фиги по тикеру и срзу покупать (тикер все равно опрееляющий, тип функция - на вход берет тикер и процент от капитала, расчитывает процент, находить фиги и покупает методом апи тиенькоффа)
# то чего нету в сообщении из тг продовать надо
# проходить по словарю смотреть если одинноково то - скип, а если чего то не хватает то купить, если наобобород у нас больше - то продать
# создать словарь с текущеми бумагами на брокерском счете
# проценты от капила он не рассчитал
# находит процент не правильно и не передает аргумент на поеукпку
#Нужно создать функцию, которая будет находить текующую цену акций


# нужно переписать логику определения покупки или продажи (мейби засовывать весь портфель в чат джпт)

#когда цена акцйий в портфеле поднимется, то он начнет продавать, типо потому что он сравнивает цену акций в портфеле с процентом свободных денег (цена акций всегда меняется), нужно сравнивать кол-во акций
#кароче нужно жестко написать условия, логику с покупкой и продажей акций 
# сравниваем предыдущий процент с текущим процентом, если также - скип, больше - докупаем (нужно рассчитать сколько докупить еще), меньше - продать лишнее (то же, расчитать скоко)
# надо еще придумать как деньги выводить
# удобнее будет покупать/продовать функциями

# в поезде начинается сущий капец когда деньги докидывают на брокерский счет, текущий алгоритм там ващ офигивает (мб просто деньги не докидывать, или перед тем как закинуть продать все акции)

#tinkoff api 100 запросов в минуту