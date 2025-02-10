from controllers.BaseController import BaseController
from utils.google_llm_provider import GeminiProvider
from models import Conversation, CommonResponse
from fastapi import HTTPException
import httpx
from utils.llm_providers import GPT4OMiniProvider, NVDIADeepSeekR1Provider, GPT4OMiniLangchainProvider, GPT4OMiniFunctionCallingProvider, DeepSeekR1Provider

def chat_providers(controller):
    return [
        GPT4OMiniProvider(controller),
        NVDIADeepSeekR1Provider(controller),
        GPT4OMiniFunctionCallingProvider(controller),
        GPT4OMiniLangchainProvider(controller),
        DeepSeekR1Provider(controller),
        GeminiProvider(controller)
    ]

class ChatController(BaseController):

    def setup(self):
        app = self.app
        timeout = httpx.Timeout(120.0)  # 120 seconds
        self.client = httpx.AsyncClient(timeout=timeout)
        self.providers = chat_providers(self)
        self.chat_models = []
        for provider in self.providers:
            self.chat_models.append(provider.get_model())

        @app.post("/chat-models/")
        def chat_models():
            return CommonResponse(message="", data=self.chat_models)
            
        @app.post("/chat/completions/")
        async def chat(conversation: Conversation):
            if not conversation:
                raise HTTPException(status_code=400, detail="Message content cannot be empty")
            try:
                selected_provider = None
                for provider in self.providers:
                    if provider.get_model().model == conversation.model:
                        selected_provider = provider
                        break
                if selected_provider:
                    return await selected_provider.execute(conversation)
                else:
                    return await self.providers[0].execute(conversation)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"{e}")
            
        @app.on_event("shutdown")
        async def shutdown_event():
            print("Shutting down")
            await self.client.aclose()