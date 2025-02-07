from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from fastapi import FastAPI
from database import create_manager
from controllers.AuthController import AuthController
from controllers.ChatController import ChatController
from controllers.FeedbackController import FeedbackController
from dotenv import load_dotenv
load_dotenv()
manager = create_manager()
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
for Controller in [AuthController, ChatController, FeedbackController]:
    cls = Controller(app, manager)
    cls.setup()
def main():
    uvicorn.run('main:app', host='0.0.0.0', port=8000)
if __name__ == '__main__':
    main()
    

