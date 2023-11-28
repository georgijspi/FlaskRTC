# models.py
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask_login import UserMixin

engine = create_engine('sqlite:///my_chat_app.db')
Base = declarative_base()

class User(Base, UserMixin):  # Add UserMixin to your User class
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True)
    password = Column(String(255))

    def is_active(self):
        return True

# Other User class methods (if any)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
