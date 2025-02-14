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
        
        @app.post("/feedback/user/{user_id}")  # New endpoint for querying by user_id
        def get_feedback_by_user(user_id: int):
            return self.get_feedback_by_user_handler(user_id=user_id) # New handler

            
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

    def get_feedback_by_user_handler(self, user_id: int):
        session = self.manager.Session()
        print("Feedbacks")
        try:
            feedbacks = session.query(Feedback).filter(Feedback.user_id == user_id).all()
            feedback_responses = []
            for feedback in feedbacks:
                feedback_responses.append(FeedBackResponse(
                    id=feedback.id,
                    contact=feedback.contact,
                    title=feedback.title,
                    content=feedback.content,
                    created_at=feedback.created_at
                ))
            print(f"Feedbacks count: {len(feedback_responses)}")
            return CommonResponse(message="Successfully retrieved feedbacks", data=feedback_responses)
        except Exception as e: # Catching general exceptions for now
            print(f"Length: {len(feedback_responses)}")
            raise HTTPException(status_code=500, detail=f"Error retrieving feedbacks: {e}") # More informative error
        finally:
            session.close()