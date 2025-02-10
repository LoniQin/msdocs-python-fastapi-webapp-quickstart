import asyncio
import httpx
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from models import CommonResponse
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