from fastapi import FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from fastapi import FastAPI, HTTPException
from database import manager
from models import Messages, UserCreate, UserLogin, CommonResponse, FeedBackModel

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    print('Request for index page received')
    return templates.TemplateResponse('index.html', {"request": request})

@app.get('/favicon.ico')
async def favicon():
    file_name = 'favicon.ico'
    file_path = './static/' + file_name
    return FileResponse(path=file_path, headers={'mimetype': 'image/vnd.microsoft.icon'})

@app.post("/chat/")
def chat(message: Messages):
    print("Message:{message}")
    if not message:
        raise HTTPException(status_code=400, detail="Message content cannot be empty")
    try:
        messages = message.messages
        response = manager.send_chat_completion(messages)
        return CommonResponse(message="", data=response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")

@app.post("/signup/")
def signup(user: UserCreate):
    return manager.signup(user.email, user.username, user.password)

@app.post("/login/")
def login(user: UserLogin):
    return manager.login(user.email, user.password)

@app.post("/feedback/")
def login(feedback: FeedBackModel):
    return manager.createFeedBack(feedback=feedback)

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000)

