from database import User

class BaseController:

    def __init__(self, app, manager):
        self.app = app
        self.manager = manager

    def authenticate(self, user_id, access_token, session = None):
        if session is None:
            session = self.manager.Session()
        # Check if the email already exists
        user = session.query(User).filter(User.user_id == user_id, User.access_token == access_token).first()
        if user:
            return user
        return None

    def setup(self):
        pass