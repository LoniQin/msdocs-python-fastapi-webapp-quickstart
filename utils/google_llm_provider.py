from utils.llm_provider import LLMProvider
import uuid
from models import ChatModel, CommonResponse, Message
from fastapi.responses import StreamingResponse
import os
import google.generativeai as genai

class GeminiProvider(LLMProvider):

    def __init__(self, chat_controller):
        super().__init__(chat_controller)
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
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
        response = chat_session.send_message(conversation.messages[-1].content)
        print(response)
        return CommonResponse(
            message="", 
            data=[Message(role="assistant", content=response.text)]
        ) 