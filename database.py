from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, ForeignKey, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from fastapi import HTTPException
from dotenv import load_dotenv
import os
import hashlib
load_dotenv()
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from models import UserResponse, CommonResponse
import uuid
# Define the base class for declarative models
Base = declarative_base()
# Define a sample table model

class User(Base):
    __tablename__ = "chat_users"
    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=False, nullable=False)
    username = Column(String, unique=False, nullable=False)
    password = Column(String, unique=False, nullable=False)
    access_token = Column(String, unique=False, nullable=False)
    token_expire_date =Column(TIMESTAMP, default=func.now()) 
    created_at = Column(TIMESTAMP, default=func.now())



class Conversation(Base):
    __tablename__ = "conversations"
    conversation_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=False, nullable=True)
    user_id = Column(Integer, ForeignKey("chat_users.user_id"))
    created_at = Column(TIMESTAMP, default=func.now())

class Message(Base):
    __tablename__ = "messages"
    message_id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.conversation_id"))
    message_text = Column(Text, nullable=False)
    is_bot_message = Column(Boolean, default=False)
    sent_at = Column(TIMESTAMP, default=func.now())

class Preference(Base):
    __tablename__ = "preferences"
    preference_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("chat_users.user_id"))
    language = Column(String, default="en")
    theme = Column(String, default="light")
    

# Assuming the User model is defined as shown in your initial code
class DatabaseManager:

    _instance = None

    def __new__(cls, db_url):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.__init__(db_url)
        return cls._instance
    
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        self.connect_and_create_table(db_url=db_url)
        self.Session = sessionmaker(bind=self.engine)
        print("Init DatabaseManager")

    # Function to connect to the remote PostgreSQL database and create tables
    def connect_and_create_table(self, db_url):
        try:
            # Create an engine to connect to the database
            engine = create_engine(db_url)

            # Create a configured "Session" class
            Session = sessionmaker(bind=engine)

            # Create a Session instance
            session = Session()

            # Create all tables defined in the Base
            Base.metadata.create_all(engine)

            print("Table(s) created successfully!")

            # Close the session
            session.close()

        except Exception as e:
            print(f"An error occurred: {e}")

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def signup(self, email, username, password):
        session = self.Session()
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
            print("Error: Email or username already exists.")
            raise HTTPException(status_code=400, detail="Email or username already exists.")
        finally:
            session.close()

    def login(self, email, password):
        session = self.Session()
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
        session = self.Session()
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

DATABASE_URL = os.environ["POSTGRES_URL"]

manager = DatabaseManager(db_url=DATABASE_URL)