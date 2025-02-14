from utils.llm_provider import LLMProvider
import uuid
from models import ChatModel, CommonResponse, Message
import os
import openai

def get_gpt4omini_client():
    api_key = os.environ["AZURE_OPENAI_API_KEY"]
    api_version = "2024-05-01-preview"
    client = openai.AzureOpenAI(
        azure_endpoint="https://ai-lonnieqin6583ai982841037486.openai.azure.com/",
        api_key=api_key,
        api_version=api_version
    )
    return client

class ContentCreationProvider(LLMProvider):

    def get_model(self):
        return ChatModel(
            id = str(uuid.uuid4()), 
            model="gpt-4o-mini-content-creation", 
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