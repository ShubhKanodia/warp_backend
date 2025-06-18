from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from .config import DATABASE_URL

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    tasks = relationship("Task", back_populates="user")
    events = relationship("Event", back_populates="user")
    messages = relationship("Message", back_populates="user")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(Text)
    deadline = Column(DateTime)
    priority = Column(Integer)
    status = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="tasks")

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="events")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    priority = Column(Integer)
    status = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="messages")

class AgentLog(Base):
    __tablename__ = "agent_logs"
    
    id = Column(Integer, primary_key=True)
    agent_type = Column(String)
    query = Column(Text)
    response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test data seeding
def seed_test_data():
    db = SessionLocal()
    try:
        # Create test user
        test_user = User(email="test@example.com")
        db.add(test_user)
        db.commit()
        
        # Create sample tasks
        tasks = [
            Task(
                title="Complete project proposal",
                description="Write up the project proposal document",
                deadline=datetime.utcnow(),
                priority=1,
                status="pending",
                user_id=test_user.id
            ),
            Task(
                title="Schedule team meeting",
                description="Coordinate with team for weekly sync",
                deadline=datetime.utcnow(),
                priority=2,
                status="pending",
                user_id=test_user.id
            )
        ]
        db.add_all(tasks)
        
        # Create sample events
        events = [
            Event(
                title="Team Standup",
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                description="Daily team sync",
                user_id=test_user.id
            )
        ]
        db.add_all(events)
        
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close() 