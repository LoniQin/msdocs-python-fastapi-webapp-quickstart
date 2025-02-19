import os 
import openai
from models import Message, CommonResponse, ChatModel
from tools import get_tools
from fastapi.responses import StreamingResponse
from tools import get_tools, handle_tool_call
from openai import OpenAI
import json
import uuid
from utils.llm_provider import LLMProvider

def get_gpt4omini_client():
    api_key = os.environ["AZURE_OPENAI_API_KEY"]
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
        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
        from langchain_openai import AzureOpenAI
        print("environment", os.environ)
        llm = AzureOpenAI(
            azure_deployment="gpt-4o-mini",  # or your deployment
            api_version="=2024-05-01-preview",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        print(1, llm)
        messages = [
            (
                "system",
                "You are a helpful assistant that translates English to French. Translate the user sentence.",
            ),
            ("human", "I love programming."),
        ]
        result1 = await llm.invoke(messages)
        print("3", result1)
        messages = []
        for message in conversation.messages:
            if message.role == "user":
                messages.append(HumanMessage(message.content))
            if message.role == "assistant":
                messages.append(AIMessage(message.content))
            if message.role == "system":
                messages.append(SystemMessage(message.content))
        print("3")
        try:
            result = llm.invoke(messages)
        except:
            print("Fail")
        return CommonResponse(message="", data=[Message(role="assistant", content=result)])
  
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