from fastapi import FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from fastapi import FastAPI, HTTPException
from database import manager
from models import Message, UserCreate, UserLogin
import psycopg2
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

@app.post('/hello', response_class=HTMLResponse)
async def hello(request: Request, name: str = Form(...)):
    if name:
        print('Request for hello page received with name=%s' % name)
        return templates.TemplateResponse('hello.html', {"request": request, 'name':name})
    else:
        print('Request for hello page received with no name or blank name -- redirecting')
        return RedirectResponse(request.url_for("index"), status_code=status.HTTP_302_FOUND)

@app.post("/chat/")
def chat(message: Message):
    if not message.content:
        raise HTTPException(status_code=400, detail="Message content cannot be empty")
    
    # Simple chatbot logic
    response = f"You said: {message.content}"
    return {"response": response}

@app.post("/signup/")
def signup(user: UserCreate):
    return manager.signup(user.email, user.username, user.password)

@app.post("/login/")
def login(user: UserLogin):
    return manager.login(user.email, user.password)

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000)

