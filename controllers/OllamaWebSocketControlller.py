
from controllers.BaseController import BaseController
from fastapi import  WebSocket, WebSocketDisconnect, Query
import json
import os 
import openai
from database import User

gpt4o_api_version = "2024-05-01-preview"

def get_gpt4omini_client():
    api_key = os.environ["AZURE_OPENAI_API_KEY"]
    
    client = openai.AzureOpenAI(
        azure_endpoint="https://ai-lonnieqin6583ai982841037486.openai.azure.com/",
        api_key=api_key,
        api_version=gpt4o_api_version
    )
    return client

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}
        self.storage = {}

    async def connect(self, user: User, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user.user_id] = websocket
        self.storage[user.user_id] = user

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)
            return True
        return False

class OllamaWebSocketController(BaseController):

    def setup(self):
        self.connection_manager = ConnectionManager()
        self.gpt_4o = get_gpt4omini_client()
        app = self.app
        @app.websocket("/ollama")
        def websocket(
            websocket: WebSocket,
            user_id: str = Query(..., description="User ID to identify connection"),
            access_token: str = Query(..., description="Access token")
        ):
            return self.websocket_endpoint(
                websocket=websocket, 
                user_id=user_id,
                access_token=access_token
            )
            
    async def websocket_endpoint(
        self,
        websocket: WebSocket,
        user_id: str = Query(..., description="User ID to identify connection"),
        access_token: str = Query(..., description="Access token")
    ):
        user = self.authenticate(user_id=user_id, access_token=access_token)
        print(f"User: {user}")
        if user == None:
            await websocket.send_text("Invalid JSON format")
            await websocket.close()
            return

        await self.connection_manager.connect(user, websocket)
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    message_data = json.loads(data)
                    target_user = message_data.get("to")
                    message = message_data.get("message")
                    if f"{target_user}".lower() == "gpt-4o-mini":
                        response = self.gpt_4o.chat.completions.create(
                            messages=[
                                {"role": "user", "content": message}
                            ],
                            model="gpt-4o-mini",
                            stream=False
                        )
                        await websocket.send_text(f"gpt-4o-mini: {response.choices[0].message.content}")
                    elif target_user and message:
                        all_message = f"{user_id}: {message}"
                        await self.connection_manager.send_personal_message(
                            all_message, 
                            target_user
                        )
                        await websocket.send_text(all_message)
                    else:
                        await websocket.send_text("Invalid message format")
                except json.JSONDecodeError:
                    await websocket.send_text("Invalid JSON format")
        except WebSocketDisconnect:
            self.connection_manager.disconnect(user_id)
            await websocket.close()