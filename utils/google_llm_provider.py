from utils.llm_provider import LLMProvider
import uuid
from models import ChatModel, CommonResponse, Message
import os
import google.generativeai as genai
import base64
from PIL import Image

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
        # Create the model
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain"
        }
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=generation_config,
        )

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
                    response = self.model.generate_content(
                        contents=contents
                    )
                    return CommonResponse(
                        message="", 
                        data=[Message(role="assistant", content=response.text)]
                    ) 
                except Exception as e:
                    print("error", e)
                    return CommonResponse(
                        message="Error", 
                        data=[]
                    ) 
                
        else:
            history = []
            for i in range(len(conversation.messages) - 1):
                message = conversation.messages[i]
                role = ""
                if message.role == "user":
                    role = "user"
                else:
                    role = "model" 
                history.append({
                    "role": role,
                    "parts": [
                        message.content
                    ]
                })
            chat_session = self.model.start_chat(
                history=history
            )
            response = chat_session.send_message(user_message.content)
            print(response)
            return CommonResponse(
                message="", 
                data=[Message(role="assistant", content=response.text)]
            ) 