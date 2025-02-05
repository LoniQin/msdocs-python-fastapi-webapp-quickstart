from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, ForeignKey, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
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
    
class Feedback(Base):
    __tablename__ = "user_feedbacks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("chat_users.user_id"))
    contact = Column(String, default="")
    title = Column(String, default="")
    content = Column(String, default="")
    created_at = Column(TIMESTAMP, default=func.now())

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

def create_manager():
    DATABASE_URL = os.environ["POSTGRES_URL"]
    return DatabaseManager(db_url=DATABASE_URL)