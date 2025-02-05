from controllers.BaseController import BaseController
from models import CommonResponse, FeedBackModel, FeedBackResponse
from database import Feedback
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy.exc import IntegrityError

class FeedbackController(BaseController):

    def setup(self):
        app = self.app
        @app.post("/feedback/")
        def feeedback(feedback: FeedBackModel):
            return self.createFeedBack(feedback=feedback)
            
    def createFeedBack(self, feedback):
        session = self.manager.Session()
        feedback = Feedback(
            user_id=feedback.user_id, 
            contact=feedback.contact, 
            title=feedback.title, 
            content=feedback.content,
            created_at=datetime.now()
        )
        try:
            session.add(feedback)
            session.commit()
            response = FeedBackResponse(id=feedback.id, contact=feedback.contact, title=feedback.title, content=feedback.content, created_at=feedback.created_at)
            return CommonResponse(message="Successfully Submit feedback", data=response)
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=400, detail="")
        finally:
            session.close()