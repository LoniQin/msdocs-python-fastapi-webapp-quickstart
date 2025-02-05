from controllers.BaseController import BaseController
import os
import requests
from models import Messages, CommonResponse
from fastapi import HTTPException

class ChatController(BaseController):

    def setup(self):
        app = self.app
        @app.post("/chat/")
        def chat(message: Messages):
            if not message:
                raise HTTPException(status_code=400, detail="Message content cannot be empty")
            try:
                messages = message.messages
                response = self.send_chat_completion(messages)
                return CommonResponse(message="", data=response)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"{e}")
        
    def send_chat_completion(self, messages, max_tokens=512, temperature=0.7):
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
            "temperature": temperature
        }
        # Send the POST request
        response = requests.post(url, headers=headers, json=payload)
        # Check if the request was successful
        if response.status_code == 200:
            return response.json()  # Return the JSON response
        else:
            raise Exception(f"Request failed with status code {response.status_code}: {response.text}")