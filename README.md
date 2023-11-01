
# Цели:
- Создать торгового робота исходя из тех. анализа акции и нвостоного фона на основе chat gpt
- Подлючить его к Tinkoff API, для совершения сделок


# Принцип работы

Программа на сервере будет спрашивать у chat gpt (selenium мб или api) исходя из бюджета и имеющих акций в портфеле что купить продать или держать, основаясь на тех анализ MACD, RSI, BB, EMA, STOCH, RSI. (Покупает дешевле, продает дороже) исходящий ответ чат джпт идет в tinkoff api, где покупапет (так же ставит стоп лоссы, которе дал нам бот)
# Архетиктура

1) Python скрипт, используя selenium, создает окно и вводит заранее поготовленный промт в chat gpt 
2) Диалог должен быть один, chat gpt должна делать выбор на основе тех анализа, новостей, а так же анализирую телеграмм канал (https://t.me/birzhevikstocksofficial2), делать выбор исходя из обучающих постов и новостных с итогами (+ как истоник - основной) изначально в диологе нужно обработать все посты, и режиме real life анализировать посты (каждые 3 запроса новая история)
 P.S. обучать на постах скорее всего не варик, ибо он забывает, либо ждать обновы
1) В свою очередь chat gpt использует расширение (Portfolio Pilot, **Boolio Invest**), в промт передается:
	1) Дата
	2) Портфель
	3) Открытые позиции (так же ср. стоимость, кол-во, доход в %)
	4) интервалы в свечах (которые нужно анализировать)
	5) ответы должны быть списком (типа price=1000, чтобы потом сохранить в переменную значения)
	6) посты телеграмм канала
	7) еще что то
2) Ответ chat gpt, используя selenium сохраняется в переменную, сортируются
3) Отсортированные значения принимает Tinkoff API, и открывет/закрывает сделки 
# Sandbox
Для проверки торговой стратегии запустить одноврменно 3-4 варианта:
	1) Опираясь на расширение (Только ChatGPT)
	2) Опираясь на расширение и тех анализ
	3) Опираясь на расширение, тех анализ, посты телеграмм каналов
	4) Premium канал биржевик, опираться только на канал

# Способ - 4, парсинг канала
Промт:
Заполни формулу, следуя табуляции и строчных символов по формуле, твой ответ не должен быть больше формулы, но может быть несколько формул в каждой строке, без посторонних слов, чистый ответ, исходя из текста. 
Формула:Комания=% 
Текст:{Спаршинные текст с откртыими позициями}
Текст:Мои открытые позы: Сбербанк - 17% от капитала Алроса - 19% от капитала (Пример)



# Поступление запросов в api
1) мониторим позы в канале
	циклом словарь используем
2) мониторим новые посты
	отправляем сообщение джпт с постом, и просим ее вывести которткий вывод: купить/продать ТИКЕР Процент
	


# Пример не автоматизированной системы
![[Pasted image 20230918104640.png]]
![[Pasted image 20230918104657.png]]![[Pasted image 20230918110022.png]]



# chatgpt_selenium_automation

ChatGPT Automation is a Python project that aims to automate interactions with OpenAI's ChatGPT using Selenium WebDriver. Currently, it requires human interaction for log-in and human verification. It handles launching Chrome, connecting to ChatGPT, sending prompts, and retrieving responses. This tool can be useful for experimenting with ChatGPT or building similar web automation tools.


## Prerequisites

1. Make sure you have installed the required libraries, as specified in the `requirements.txt` file.
2. Download the appropriate version of `chromedriver.exe` and save it to a known location on your system.


## Example Usage

 ```python
from handler.chatgpt_selenium_automation import ChatGPTAutomation

# Define the path where the chrome driver is installed on your computer
chrome_driver_path = r"C:\Users\user\Desktop\chromedriver.exe"

# the sintax r'"..."' is required because the space in "Program Files" in the chrome path
chrome_path = r'"C:\Program Files\Google\Chrome\Application\chrome.exe"'

# Create an instance
chatgpt = ChatGPTAutomation(chrome_path, chrome_driver_path)

# Define a prompt and send it to chatgpt
prompt = "What are the benefits of exercise?"
chatgpt.send_prompt_to_chatgpt(prompt)

# Retrieve the last response from ChatGPT
response = chatgpt.return_last_response()
print(response)

# Save the conversation to a text file
file_name = "conversation.txt"
chatgpt.save_conversation(file_name)

# Close the browser and terminate the WebDriver session
chatgpt.quit()
   ```
   
   
## Note 

After instantiating the ChatGPTAutomation class, chrome will open up to chatgpt page, it will require you to manually complete the register/ log-in / Human-verification. After that, you must tell the program to continue, in the console type 'y'. After Those steps, the program will be able to continue autonomously.

## Note on Changing Tabs or Conversations

Please be aware that changing tabs or switching to another conversation while the script is running might cause errors or lead to the methods being applied to unintended chats. For optimal results and to avoid unintended consequences, it is recommended to avoid to manually interact with the browser (after the log-in/human verification) while the automation script is running.

   
   
## Note on Errors and Warnings

While running the script, you may see some error messages or warnings in the console, such as:
- DevTools listening on ws://...
- INFO: Created TensorFlow Lite XNNPACK delegate for CPU.
- ERROR: Couldn't read tbsCertificate as SEQUENCE
- ERROR: Failed parsing Certificate
   

These messages are related to the underlying libraries or the browser, and you can safely ignore them if the script works as expected. If you encounter any issues with the script, please ensure that you have installed the correct dependencies and are using the correct ChromeDriver version compatible with your Chrome browser.

   
   

