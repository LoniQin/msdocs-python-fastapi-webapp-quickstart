
class BaseController:

    def __init__(self, app, manager):
        self.app = app
        self.manager = manager

    def setup(self):
        pass
        
    def create_session(self):
        return self.manager.Session()