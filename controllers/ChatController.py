from controllers.BaseController import BaseController
import os
import requests
from models import Messages, CommonResponse, ChatModel
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
import json
import uuid
def chunk_generator(data, chunk_size=1024):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

class ChatController(BaseController):

    def setup(self):
        app = self.app
        @app.post("/chat-models/")
        def chat_models():
            return CommonResponse(message="", data=self.chat_models())
            
        @app.post("/chat/completions/")
        def chat(message: Messages):
            if not message:
                raise HTTPException(status_code=400, detail="Message content cannot be empty")
            try:
                messages = message.messages
                if message.model == "gpt-4o-mini":
                    return self.chat_with_openai(messages)
                elif message.model == "DeepSeek-R1":
                    return self.chat_with_deepseek_r1(messages)
                else:
                    raise HTTPException(status_code=400, detail=f"Model does not exists.")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"{e}")
            
    def chat_models(self):
        return [
            ChatModel(id = str(uuid.uuid4()), model="gpt-4o-mini", displayName="gpt-4o-mini", provider="openai", description="gpt-4o-mini"),
            ChatModel(id = str(uuid.uuid4()), model="DeepSeek-R1", displayName="DeepSeek-R1", provider="DeepSeek-R1", description="DeepSeek-R1 excels at reasoning tasks using a step-by-step training process, such as language, scientific reasoning, and coding tasks. It features 671B total parameters with 37B active parameters, and 128k context length. DeepSeek-R1 builds on the progress of earlier reasoning-focused models that improved performance by extending Chain-of-Thought (CoT) reasoning. DeepSeek-R1 takes things further by combining reinforcement learning (RL) with fine-tuning on carefully chosen datasets. It evolved from an earlier version, DeepSeek-R1-Zero, which relied solely on RL and showed strong reasoning skills but had issues like hard-to-read outputs and language inconsistencies. To address these limitations, DeepSeek-R1 incorporates a small amount of cold-start data and follows a refined training pipeline that blends reasoning-oriented RL with supervised fine-tuning on curated datasets, resulting in a model that achieves state-of-the-art performance on reasoning benchmarks.")
        ]
    
    def chat_with_deepseek_r1(self, messages):
        """
        Sends a chat completion request to Azure OpenAI DeepSeek Service.

        Args:
            messages (list({role, content})): messages with role and content each item.
        Returns:
            dict: The JSON response from the API.
        """
        # Define the endpoint URL
        endpoint = "https://DeepSeek-R1-zxxnw.eastus2.models.ai.azure.com"
        api_key = os.environ["DEEPSEEK_APIKEY"]
        # Define the headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        items = []
        for item in messages:
            items.append({"role": item.role, "content": item.content})
        # Define the payload
        payload = {
            "messages": items,
            "max_tokens": 2048,
            "model": "DeepSeek-R1",
            "stream": True
        }
        # Send the POST request
        url = f"{endpoint}/chat/completions"
        response = requests.post(url, headers=headers, json=payload, stream=True)
        def content_stream():
            for i, item in enumerate(response.iter_lines()):
                yield item.decode()
        return StreamingResponse(content_stream(), media_type="text/plain")
        
    def chat_with_openai(self, messages, max_tokens=512, temperature=0.7):
        """
        Sends a chat completion request to Azure OpenAI.

        Args:
            messages (list({role, content})): messages with role and content each item.
            max_tokens (int): The maximum number of tokens to generate.
            temperature (float): The sampling temperature (0.0 to 1.0).

        Returns:
            dict: The JSON response from the API.
        """
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
        for item in messages:
            items.append({"role": item.role, "content": item.content})
        # Define the payload
        payload = {
            "messages": items,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True
        }
        response = requests.post(url, headers=headers, json=payload, stream=True)
        def content_stream():
            for i, item in enumerate(response.iter_lines()):
                yield item.decode()
        return StreamingResponse(content_stream(), media_type="text/plain")