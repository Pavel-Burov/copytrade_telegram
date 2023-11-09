import re, asyncio, time, sys
from api_keys import Tokens
from request_gpt import RequestGpt
from get_tinkoff_v2 import Trade

from telethon import events
from aiogram import Bot, Dispatcher, types, executor
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.channels import JoinChannelRequest


api_id = Tokens.api_tele_id
api_hash = Tokens.api_tele_hash
phone_number = Tokens.tele_number

async def get_channel(client):
    dialogs = await client.get_dialogs()
    for i, dialog in enumerate(dialogs, start=1):
        if dialog.is_channel:
            if i == 1:
                print(dialog.name)
                return dialog.entity
            


tag = "мои позиции:"


# Действительные позиции на брокерском счете
real_positions = {"ALRS":"18", "VTBR":"50"}

async def parse_message(client, channel, tag, real_position):
    async for message in client.iter_messages(channel):
        if message.text and (tag in message.text):
            #text its promt for chatgpt
            text = f"Заполни формулу, следуя табуляции и строчных символов по формуле, твой ответ не должен быть больше формулы, но может быть несколько формул в каждой строке, без посторонних слов, чистый ответ, исходя из текста. Формула:Тикер Акций Компании=Процентное число. Пример:ALRS=18. Текст: {message.text}"
            text = f"исходя из текста выведи формулу:Ticker=Buy/Sell текст: {message.text}"
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
            real_positions.update(result)


async def sell(client):
    async for message in client.iter_messages("me"):
        if message.text and ("all sell" in message.text):
            try:
                await Trade.sell_all(sandbox_mode=True)
            except Exception as ex:
                print((f"Ошибка продажи: {ex}"))   
            sys.exit()    


async def start():
    async with TelegramClient(phone_number, api_id, api_hash) as client:
        while True:
            # await sell(client)
            channel = await get_channel(client)
            print("Получил канал")
            await parse_message(client, channel=channel, tag=tag, real_position=real_positions)
            # await Trade.get_portfolio(sandbox_mode=True)
            await asyncio.sleep(20)


if __name__ == '__main__':
    gpt_request = RequestGpt()
    asyncio.run(start())
    
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

# Берет процент от доустпных денег а нет капиатала (100к было купил 50% 50к, и еще 50% это уже 25к т.к. 50% от 50к это 25к)


# Скидываем свои позы и новые позы, и пусть чат джпт сам счаитает чо сколько купить


# добавить основной запускающий скрипт 
# Добавить метод находжения закрепленного сообщения
# обработчик новых сообщений

# git add .
# git commit -m ""
# git push -f origin 