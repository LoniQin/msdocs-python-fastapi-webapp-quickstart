from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from database import create_manager
from controllers.AuthController import AuthController
from controllers.ChatController import ChatController
from controllers.FeedbackController import FeedbackController
from controllers.WebSocketControlller import WebSocketController
from controllers.OllamaWebSocketControlller import OllamaWebSocketController
from controllers.BlogController import BlogController
from controllers.BlogV2Controller import BlogV2Controller
from dotenv import load_dotenv
load_dotenv()
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
manager = create_manager()
session = manager.Session()
session.query()
for Controller in [AuthController, ChatController, FeedbackController, WebSocketController, OllamaWebSocketController, BlogController, BlogV2Controller]:
    cls = Controller(app, manager)
    cls.setup()   
def main():
    uvicorn.run('main:app', host='0.0.0.0', port=8000)
if __name__ == '__main__':
    main()