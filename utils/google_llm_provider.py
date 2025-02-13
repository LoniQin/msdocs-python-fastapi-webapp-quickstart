from utils.llm_provider import LLMProvider
import uuid
from models import ChatModel, CommonResponse, Message
import os
import base64
from PIL import Image
from google.genai import types, Client

def get_current_weather(location: str) -> str:
    """Get the current whether in a given location.

    Args:
        location: required, The city and state, e.g. San Franciso, CA
        unit: celsius or fahrenheit
    """
    print(f'Called with: {location=}')
    return "23C"

def convert_base64_to_file(base64_string, fileName):
    images_path = os.path.expanduser("images")
    if not os.path.exists(images_path):
        os.makedirs(images_path)
    output_file_path = os.path.join(images_path, fileName)
    # Decode the Base64 string
    binary_data = base64.b64decode(base64_string)
    
    # Write the binary data to a file
    with open(output_file_path, 'wb') as file:
        file.write(binary_data)
    print(f"File saved as: {output_file_path}")
    return output_file_path

class GeminiProvider(LLMProvider):

    def __init__(self, chat_controller):
        super().__init__(chat_controller)
        self.client = Client(api_key=os.environ["GEMINI_API_KEY"])


    def get_model(self):
        return ChatModel(
            id = str(uuid.uuid4()), 
            model="gemini-2.0-flash", 
            displayName="Gemini 2.0 Flash", 
            provider="Google", 
            stream=False,
            description="Gemini"
        )
    
    async def execute(self, conversation):
        messages = []
        for i in range(len(conversation.messages) - 1):
            message = conversation.messages[i]
            role = ""
            if message.role == "user":
                role = "user"
            else:
                role = "model" 
            messages.append(types.Part.from_text(message.content))
        user_message = conversation.messages[-1]
       
        if len(user_message.files) > 0:
            contents = [user_message.content]
            for file in user_message.files:
                if file.mine_type == "image/jpeg":
                    file_path = convert_base64_to_file(file.content, file.file_name)
                    print(f"Saved file to {file_path}")
                    img = Image.open(file_path)
                    contents.append(img)
            try:
                response = self.client.models.generate_content(
                    model='gemini-2.0-flash', 
                    contents=contents
                )
                print("Response:", response)
                return CommonResponse(
                    message="", 
                    data=[Message(role="assistant", content=response.candidates[0].content.parts[0].text)]
                )
            except Exception as e:
                print("error", e)
                return CommonResponse(
                    message="Error", 
                    data=[]
                ) 
        else:
            try:
                messages.append(types.Part.from_text(user_message.content))
                response = self.client.models.generate_content(
                    model='gemini-2.0-flash', 
                    contents=messages
                )
                print("response:", response)
                return CommonResponse(
                    message="", 
                    data=[Message(role="assistant", content=response.candidates[0].content.parts[0].text)]
                ) 
            except Exception as e:
                print("error", e)
                return CommonResponse(
                    message="Error", 
                    data=[]
                ) 
            
                