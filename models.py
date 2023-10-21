from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from flask_login import UserMixin
from datetime import datetime

engine = create_engine('sqlite:///my_chat_app.db')
Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    sender_id = Column(Integer, ForeignKey('users.id'))
    chat_room_id = Column(Integer, ForeignKey('chat_rooms.id'))
    sender = relationship('User')

class ChatRoom(Base):
    __tablename__ = 'chat_rooms'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    users = relationship('User', secondary='chat_room_users')
    messages = relationship('Message')

class ChatRoomUser(Base):
    __tablename__ = 'chat_room_users'
    chat_room_id = Column(Integer, ForeignKey('chat_rooms.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)

# User class defined after ChatRoom and related classes
class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True)
    password = Column(String(255))
    profile_picture = Column(String(255))
    chat_rooms = relationship('ChatRoom', secondary='chat_room_users')

    def is_active(self):
        return True  # Change this logic based on your application's requirements

    # Other User class methods (if any)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)