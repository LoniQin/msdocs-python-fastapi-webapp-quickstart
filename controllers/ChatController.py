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
import json 
from tools import get_tools, handle_tool_call
from openai import OpenAI

class LLMProvider:

    def __init__(self, chat_controller):
        self.chat_controller = chat_controller
        

    def get_model(self):
        return None

    async def execute(self, conversation):
        pass

    async def common_request(self, url, headers, payload, stream):
        async def stream_chat_completion():
            async with self.chat_controller.client.stream("POST", url, json=payload, headers=headers) as response:
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

def get_gpt4omini_client():
    api_key = os.environ["API_KEY"]
    api_version = "2024-05-01-preview"
    client = openai.AzureOpenAI(
        azure_endpoint="https://ai-lonnieqin6583ai982841037486.openai.azure.com/",
        api_key=api_key,
        api_version=api_version
    )
    return client

class GPT4OMiniProvider(LLMProvider):

    def get_model(self):
        return ChatModel(
            id = str(uuid.uuid4()), 
            model="gpt-4o-mini", 
            displayName="gpt-4o-mini", 
            provider="OpenAI", 
            stream=True,
            description="GPT-4o-Mini, a cutting-edge AI language model designed to offer powerful AI capabilities in a compact and accessible format. Building on the successes of its predecessors, GPT-4o-Mini retains the advanced understanding and language generation abilities that have made the GPT series a favorite among developers and researchers."
        )

    async def execute(self, conversation):
        deployment = "gpt-4o-mini"
        client = get_gpt4omini_client()
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

class GPT4OMiniFunctionCallingProvider(LLMProvider):

    def get_model(self):
        return ChatModel(
            id = str(uuid.uuid4()), 
            model="gpt-4o-mini-function-calling", 
            displayName="gpt-4o-mini(Function Calling)", 
            provider="OpenAI", 
            stream=False,
            description="GPT-4o-Mini, a cutting-edge AI language model designed to offer powerful AI capabilities in a compact and accessible format. Building on the successes of its predecessors, GPT-4o-Mini retains the advanced understanding and language generation abilities that have made the GPT series a favorite among developers and researchers."
        )

    async def execute(self, conversation):
        deployment = "gpt-4o-mini"
        client = get_gpt4omini_client()
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
                    print(f"Return a response:{response}")
            final_response = client.chat.completions.create(
                model=deployment,
                messages=messages,
            )
            msg = final_response.choices[0].message
            return CommonResponse(message="", data=[Message(role=msg.role, content=msg.content)])
        else:
            msg = response.choices[0].message
            return CommonResponse(message="", data=[Message(role=msg.role, content=msg.content)])

class GPT4OMiniLangchainProvider(LLMProvider):

    def get_model(self):
        return ChatModel(
            id = str(uuid.uuid4()), 
            model="gpt-4o-mini-langchain", 
            displayName="gpt-4o-mini(Langchain)", 
            provider="Azure", 
            stream=False,
            description="GPT-4o-Mini, a cutting-edge AI language model designed to offer powerful AI capabilities in a compact and accessible format. Building on the successes of its predecessors, GPT-4o-Mini retains the advanced understanding and language generation abilities that have made the GPT series a favorite among developers and researchers."
        )

    async def execute(self, conversation):
        deployment = "gpt-4o-mini"
        client = get_gpt4omini_client()
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
                    print(f"Return a response:{response}")
            final_response = client.chat.completions.create(
                model=deployment,
                messages=messages,
            )
            msg = final_response.choices[0].message
            return CommonResponse(message="", data=[Message(role=msg.role, content=msg.content)])
        else:
            msg = response.choices[0].message
            return CommonResponse(message="", data=[Message(role=msg.role, content=msg.content)])
               
class NVDIADeepSeekR1Provider(LLMProvider):

    def get_model(self):
        return ChatModel(
            id = str(uuid.uuid4()), 
            model="nvdia-deepseek-r1", 
            displayName="DeepSeek-R1", 
            provider="NVDIA", 
            stream=True,
            description="DeepSeek R1 in NVDIA"
        )

    async def execute(self, conversation):
        client = OpenAI(
            base_url = "https://integrate.api.nvidia.com/v1",
            api_key = os.environ["NVDIA_DEEPSEEK_API_KEY"]
        )
        messages = []
        for message in conversation.messages:
            messages.append({"role": message.role, "content": message.content})
        
        async def stream_chat_completion():
            response = client.chat.completions.create(
                model="deepseek-ai/deepseek-r1",
                messages=messages,
                temperature=0.6,
                top_p=0.7,
                max_tokens=4096,
                stream=True
            )
            for chunk in response:
                yield "data: " + json.dumps(chunk.to_dict()) + "\n"
        return StreamingResponse(
            stream_chat_completion(),
            media_type="text/event-stream"
        )
    
class DeepSeekR1Provider(LLMProvider):
 
    def get_model(self):
        return ChatModel(
            id = str(uuid.uuid4()), 
            model="DeepSeek-R1", 
            displayName="DeepSeek-R1", 
            provider="DeepSeek", 
            stream=True,
            description="DeepSeek-R1 excels at reasoning tasks using a step-by-step training process, such as language, scientific reasoning, and coding tasks. It features 671B total parameters with 37B active parameters, and 128k context length. DeepSeek-R1 builds on the progress of earlier reasoning-focused models that improved performance by extending Chain-of-Thought (CoT) reasoning. DeepSeek-R1 takes things further by combining reinforcement learning (RL) with fine-tuning on carefully chosen datasets. It evolved from an earlier version, DeepSeek-R1-Zero, which relied solely on RL and showed strong reasoning skills but had issues like hard-to-read outputs and language inconsistencies. To address these limitations, DeepSeek-R1 incorporates a small amount of cold-start data and follows a refined training pipeline that blends reasoning-oriented RL with supervised fine-tuning on curated datasets, resulting in a model that achieves state-of-the-art performance on reasoning benchmarks."
        )

    async def execute(self, conversation):
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
    
         
def chat_providers(controller):
    return [
        GPT4OMiniProvider(controller),
        NVDIADeepSeekR1Provider(controller),
        GPT4OMiniFunctionCallingProvider(controller),
        GPT4OMiniLangchainProvider(controller),
        DeepSeekR1Provider(controller) 
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
                    raise HTTPException(status_code=400, detail=f"Model does not exists.")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"{e}")
            
        @app.on_event("shutdown")
        async def shutdown_event():
            print("Shutting down")
            await self.client.aclose()