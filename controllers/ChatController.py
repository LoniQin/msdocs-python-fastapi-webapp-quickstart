from controllers.BaseController import BaseController
import os
from models import Conversation, CommonResponse, ChatModel
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
import uuid
import httpx
import asyncio
import httpx

class ChatController(BaseController):

    def setup(self):
        app = self.app
        timeout = httpx.Timeout(30.0)  # 30 seconds
        self.client = httpx.AsyncClient(timeout=timeout)
        @app.post("/chat-models/")
        def chat_models():
            return CommonResponse(message="", data=self.chat_models())
            
        @app.post("/chat/completions/")
        async def chat(conversation: Conversation):
            if not conversation:
                raise HTTPException(status_code=400, detail="Message content cannot be empty")
            try:
                if conversation.model == "gpt-4o-mini":
                    return await self.chat_with_openai(conversation)
                elif conversation.model == "DeepSeek-R1":
                    return await self.chat_with_deepseek_r1(conversation)
                else:
                    raise HTTPException(status_code=400, detail=f"Model does not exists.")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"{e}")
            
        @app.on_event("shutdown")
        async def shutdown_event():
            print("Shutting down")
            await self.client.aclose()

    def chat_models(self):
        return [
            ChatModel(id = str(uuid.uuid4()), model="gpt-4o-mini", displayName="gpt-4o-mini", provider="openai", description="gpt-4o-mini"),
            ChatModel(id = str(uuid.uuid4()), model="DeepSeek-R1", displayName="DeepSeek-R1", provider="DeepSeek-R1", description="DeepSeek-R1 excels at reasoning tasks using a step-by-step training process, such as language, scientific reasoning, and coding tasks. It features 671B total parameters with 37B active parameters, and 128k context length. DeepSeek-R1 builds on the progress of earlier reasoning-focused models that improved performance by extending Chain-of-Thought (CoT) reasoning. DeepSeek-R1 takes things further by combining reinforcement learning (RL) with fine-tuning on carefully chosen datasets. It evolved from an earlier version, DeepSeek-R1-Zero, which relied solely on RL and showed strong reasoning skills but had issues like hard-to-read outputs and language inconsistencies. To address these limitations, DeepSeek-R1 incorporates a small amount of cold-start data and follows a refined training pipeline that blends reasoning-oriented RL with supervised fine-tuning on curated datasets, resulting in a model that achieves state-of-the-art performance on reasoning benchmarks.")
        ]
        
    async def chat_with_deepseek_r1(self, conversation):
        # Define the endpoint URL
        endpoint = "https://DeepSeek-R1-zxxnw.eastus2.models.ai.azure.com"
        api_key = os.environ["DEEPSEEK_APIKEY"]
        # Define the headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        items = []
        for item in conversation.messages:
            items.append({"role": item.role, "content": item.content})
        # Define the payload
        payload = {
            "messages": items,
            "max_tokens": 2048,
            "model": "DeepSeek-R1",
            "stream": conversation.stream
        }
        # Send the POST request
        url = f"{endpoint}/chat/completions"
        return await self.common_request(url, headers, payload, conversation.stream)
        
    async def chat_with_openai(self, conversation, max_tokens=512, temperature=0.7):
        # Define the endpoint URL
        api_key = os.environ["API_KEY"]
        endpoint = "https://ai-lonnieqin6583ai982841037486.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions"
        api_version = "2024-05-01-preview"
        url = f"{endpoint}?api-version={api_version}"
        # Define the headers
        headers = {
            "api-key": api_key,
            "Content-Type": "application/json"
        }
        items = []
        for item in conversation.messages:
            items.append({"role": item.role, "content": item.content})
        # Define the payload
        payload = {
            "messages": items,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": conversation.stream
        }
        return await self.common_request(url, headers, payload, conversation.stream)
                            
    async def common_request(self, url, headers, payload, stream):
        async def stream_chat_completion():
            async with self.client.stream("POST", url, json=payload, headers=headers) as response:
                async for chunk in response.aiter_text():
                    yield chunk
                    await asyncio.sleep(0.1) 
        if stream:
            return StreamingResponse(
                stream_chat_completion(),
                media_type="text/event-stream"
            )
        else:
            try:
                print(0, payload)
                response = await self.client.post(url, headers=headers, json=payload)
                print(1, response)
                response.raise_for_status()
                print(2, response)
                json = response.json()
                print(3, json)
                return CommonResponse(message="", data=json)
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))