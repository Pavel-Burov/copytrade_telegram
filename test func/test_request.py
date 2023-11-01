from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

# Запустите веб-браузер и перейдите на страницу ChatGPT
# driver = webdriver.Chrome(executable_path='/путь_к_webdriver/chromedriver')  # Укажите путь к Chrome WebDriver
driver = webdriver.Chrome(executable_path="E:\python\Tinkoff\chatgpt_selenium_automation-master\chromedriver.exe")
driver.get("https://chat.openai.com/?model=text-davinci-002-render-sha")

# Найдите поле для ввода текста и введите ваш запрос
input_element = driver.find_element_by_id("prompt-textarea")  # Селектор поля ввода может измениться
input_element.send_keys("Напиши калькятор python")
input_element.send_keys(Keys.RETURN)  # Нажмите Enter

# Дождитесь ответа и получите его
time.sleep(5)  # Подождите некоторое время, чтобы ответ загрузился (может потребоваться настройка)
response_element = driver.find_element_by_class(".chat-response")  # Селектор ответа может измениться
response = response_element.text

# Выведите ответ
print(response)

# Закройте браузер
driver.quit()
