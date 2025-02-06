import json.scanner
from controllers.BaseController import BaseController
import os
from models import Conversation, Message, CommonResponse, ChatModel
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
import uuid
import httpx
import asyncio
import httpx
import openai
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
import json 
from tools import get_tools, handle_tool_call

class ChatController(BaseController):

    def setup(self):
        app = self.app
        timeout = httpx.Timeout(120.0)  # 120 seconds
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
                    return await self.chat_with_azure_gpt4omini(conversation)
                elif conversation.model == "gpt-4o-mini-function-calling":
                    return await self.chat_with_gpt4omini_function_calling(conversation)
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
            ChatModel(id = str(uuid.uuid4()), model="gpt-4o-mini", displayName="gpt-4o-mini", provider="OpenAI", description="GPT-4o-Mini, a cutting-edge AI language model designed to offer powerful AI capabilities in a compact and accessible format. Building on the successes of its predecessors, GPT-4o-Mini retains the advanced understanding and language generation abilities that have made the GPT series a favorite among developers and researchers."),
            ChatModel(id = str(uuid.uuid4()), model="gpt-4o-mini-function-calling", displayName="gpt-4o-mini-function-calling", provider="OpenAI", description="GPT-4o-Mini, a cutting-edge AI language model designed to offer powerful AI capabilities in a compact and accessible format. Building on the successes of its predecessors, GPT-4o-Mini retains the advanced understanding and language generation abilities that have made the GPT series a favorite among developers and researchers."),
            ChatModel(id = str(uuid.uuid4()), model="DeepSeek-R1", displayName="DeepSeek-R1", provider="DeepSeek", description="DeepSeek-R1 excels at reasoning tasks using a step-by-step training process, such as language, scientific reasoning, and coding tasks. It features 671B total parameters with 37B active parameters, and 128k context length. DeepSeek-R1 builds on the progress of earlier reasoning-focused models that improved performance by extending Chain-of-Thought (CoT) reasoning. DeepSeek-R1 takes things further by combining reinforcement learning (RL) with fine-tuning on carefully chosen datasets. It evolved from an earlier version, DeepSeek-R1-Zero, which relied solely on RL and showed strong reasoning skills but had issues like hard-to-read outputs and language inconsistencies. To address these limitations, DeepSeek-R1 incorporates a small amount of cold-start data and follows a refined training pipeline that blends reasoning-oriented RL with supervised fine-tuning on curated datasets, resulting in a model that achieves state-of-the-art performance on reasoning benchmarks.")
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
    
    def get_gpt4omini_client(self):
        api_key = os.environ["API_KEY"]
        api_version = "2024-05-01-preview"
        client = openai.AzureOpenAI(
            azure_endpoint="https://ai-lonnieqin6583ai982841037486.openai.azure.com/",
            api_key=api_key,
            api_version=api_version
        )
        return client
    
    async def chat_with_azure_gpt4omini(self, conversation):
        deployment = "gpt-4o-mini"
        client = self.get_gpt4omini_client()
        async def stream_chat_completion():
            response = client.chat.completions.create(
                messages=conversation.messages,
                model=deployment,
                stream=True
            )
            for chunk in response:
                yield "data: " + chunk.to_json() + "\n"
        if conversation.stream:
            return StreamingResponse(
                stream_chat_completion(),
                media_type="text/event-stream"
            )
        else:
            response = client.chat.completions.create(
                messages=conversation.messages,
                model=deployment,
                stream=False
            )
            return CommonResponse(message="", data=response.to_json())
    
    async def chat_with_gpt4omini_function_calling(self, conversation):
        deployment = "gpt-4o-mini"
        client = self.get_gpt4omini_client()
        tools = get_tools()
        messages = []
        for message in conversation.messages:
            messages.append({"role": message.role, "content": message.content})
        response = client.chat.completions.create(
            messages=messages,
            model=deployment,
            tools=tools,
            tool_choice="auto"
        )
        response_message = response.choices[0].message 
        messages.append(response_message)
            # Handle function calls
        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                response = handle_tool_call(tool_call)
                if response != None:
                    messages.append(response)
                    print(f"Returne a response:{response}")
            final_response = client.chat.completions.create(
                model=deployment,
                messages=messages,
            )
            msg = final_response.choices[0].message
            return CommonResponse(message="", data=[Message(role=msg.role, content=msg.content)])
        else:
            msg = response.choices[0].message
            return CommonResponse(message="", data=[Message(role=msg.role, content=msg.content)])
       
        
        
    async def chat_with_azure_deepseek_r1(self, conversation):
        api_key = os.environ["DEEPSEEK_APIKEY"]
        # set the deployment name for the model we want to use
        deployment = "DeepSeek-R1"
        
        client = ChatCompletionsClient(
            endpoint="https://DeepSeek-R1-zxxnw.eastus2.models.ai.azure.com/",
            credential=AzureKeyCredential(api_key)
        )
        messages = []
        for message in conversation.messages:
            if message.role == "user":
                messages.append(UserMessage(message.content))
            if message.role == "system":
                messages.append(SystemMessage(message.content))
            if message.role == "assistant":
                messages.append(AssistantMessage(message.content))
        async def stream_chat_completion():
            response = client.complete(
                messages=messages,
                max_tokens=4096,
                model=deployment,
                stream=True
            )
            for chunk in response:
                yield "data: " + json.dumps(chunk.as_dict()) + "\n"
        if conversation.stream:
            return StreamingResponse(
                stream_chat_completion(),
                media_type="text/event-stream"
            )
        else:
            response = client.complete(
                messages=messages,
                max_tokens=4096,
                model=deployment
            )
            return CommonResponse(message="", data=response.to_json())
                            
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
                async with self.client.post(url, headers=headers, json=payload) as response:
                    response.raise_for_status()
                    json = await response.json()
                    return CommonResponse(message="", data=json)
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))