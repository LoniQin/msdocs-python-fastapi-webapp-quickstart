from database import User
from fastapi import HTTPException

class BaseController:

    def __init__(self, app, manager):
        self.app = app
        self.manager = manager

    def authenticate_with_api_key(self, access_token, session = None):
        if session is None:
            session = self.manager.Session()
        # Check if the email already exists
        user = session.query(User).filter(User.access_token == access_token).first()
        if user:
            return user
        return None
    
    def authenticate(self, user_id, access_token, session = None):
        if session is None:
            session = self.manager.Session()
        # Check if the email already exists
        user = session.query(User).filter(User.user_id == user_id, User.access_token == access_token).first()
        if user:
            return user
        return None
    
    def raise_401(self):
        raise HTTPException(401, detail="You don't have permission.")

    def raise_404(self):
        raise HTTPException(404, detail="Not found")
    
    def setup(self):
        pass