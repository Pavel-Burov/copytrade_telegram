from handler.chatgpt_selenium_automation import ChatGPTAutomation

class RequestGpt:
    def __init__(self):
        # Define the path where the chrome driver is installed on your computer
        self.chrome_driver_path = r"E:\python\Tinkoff\chatgpt_selenium_automation-master\chromedriver.exe"

        # the sintax r'"..."' is required because of the space in "Program Files" 
        # in my chrome_path
        self.chrome_path = r'"C:\Program Files\Google\Chrome\Application\chrome.exe"'

        # Create an instance
        self.chatgpt = ChatGPTAutomation(self.chrome_path, self.chrome_driver_path)

    def request(self, prompt):
        # Initialize the chatgpt instance
        # self.chatgpt.initialize()

        # Define a prompt and send it to chatGPT
        text = prompt
        self.chatgpt.send_prompt_to_chatgpt(text)

        # Retrieve the last response from chatGPT
        response = self.chatgpt.return_last_response()
        return response

        # Save the conversation to a text file
        # file_name = "conversation.txt"
        # chatgpt.save_conversation(file_name)

        # Close the browser and terminate the WebDriver session
        # self.chatgpt.quit()
        # input()

# gpt_request = RequestGpt()
# print(gpt_request.request("Как дела?"))