from controllers.BaseController import BaseController
import hashlib
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from models import UserResponse, CommonResponse, UserCreate, UserLogin
import uuid
from database import User

class AuthController(BaseController):

    def setup(self):
        app = self.app
        @app.post("/signup/")
        def signup(user: UserCreate):
            return self.signup(user.email, user.username, user.password)

        @app.post("/login/")
        def login(user: UserLogin):
            return self.login(user.email, user.password)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def signup(self, email, username, password):
        session = self.manager.Session()
        # Check if the email already exists
        existing_user = session.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists.")
        access_token = str(uuid.uuid4())
        new_user = User(
            email=email,
            username=username,
            password=self.hash_password(password),
            access_token=access_token,
            token_expire_date=datetime.now() + timedelta(days=1), # Set token expire date to 1 day from now
            created_at=datetime.now()  # Set created_at to current UTC time
        )
        try:
            session.add(new_user)
            session.commit()
            session.refresh(new_user) 
            data = UserResponse(user_id=new_user.user_id, email=new_user.email, username=new_user.username,access_token=new_user.access_token)
            return CommonResponse(message="User signed up successfully!", data=data)
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=400, detail="Email or username already exists.")
        finally:
            session.close()

    def login(self, email, password):
        session = self.manager.Session()
        user = session.query(User).filter_by(email=email).first()
        try:
            if user and user.password == self.hash_password(password):
                user.access_token = str(uuid.uuid4())
                # TBD Check token_expire_date
                user.token_expire_date=datetime.now() + timedelta(days=1)
                # Commit the change to the database
                session.commit()
                data = UserResponse(user_id=user.user_id, email=user.email, username=user.username,access_token=user.access_token)
                return CommonResponse(message="User login successfully!", data=data)
            else:
                raise HTTPException(status_code=401, detail="Invalid email or password.")
        except IntegrityError:
            print("Error: Email or username already exists.")
            raise HTTPException(status_code=400, detail="Email or username already exists.")
        finally:
            session.close() 

    def find_password_by_email(self, email):
        session = self.manager.Session()
        user = session.query(User).filter_by(email=email).first()
        try:
            if user:
                # Here, implement your email sending logic
                return {"message": f"Password recovery email sent to {email}."}
            else:
                print("No user found with that email.")
                return {"message": "No user found with that email."}
        except IntegrityError:
            raise HTTPException(status_code=400, detail="Email or username already exists.")
        finally:
            session.close()