"""
Database models for the centralized memory system.
Defines SQLAlchemy models for agents, knowledge, conversations, actions, and learning patterns.
"""

from sqlalchemy import create_engine, Column, String, Text, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime

Base = declarative_base()

class Agent(Base):
    """Agent model for storing agent information."""
    __tablename__ = 'agents'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    department = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    knowledge_entries = relationship("KnowledgeEntry", back_populates="agent")
    conversations = relationship("Conversation", back_populates="agent")
    actions = relationship("Action", back_populates="agent")
    learning_patterns = relationship("LearningPattern", back_populates="agent")

class KnowledgeEntry(Base):
    """Knowledge storage model for structured and unstructured data."""
    __tablename__ = 'knowledge_entries'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('agents.id'), nullable=False)
    content_type = Column(String(50), nullable=False)  # 'structured', 'unstructured'
    content = Column(Text, nullable=False)
    entry_metadata = Column(JSONB)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    embedding = Column(Vector(1536))  # OpenAI embedding dimension
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agent = relationship("Agent", back_populates="knowledge_entries")

class Conversation(Base):
    """Conversation history model."""
    __tablename__ = 'conversations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('agents.id'), nullable=False)
    thread_id = Column(String(255))
    message = Column(Text, nullable=False)
    role = Column(String(50))  # 'user', 'assistant', 'system'
    conversation_metadata = Column(JSONB)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agent = relationship("Agent", back_populates="conversations")

class Action(Base):
    """Action history model."""
    __tablename__ = 'actions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('agents.id'), nullable=False)
    action_type = Column(String(100), nullable=False)
    input_data = Column(JSONB)
    output_data = Column(JSONB)
    success = Column(Boolean, default=True)
    execution_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agent = relationship("Agent", back_populates="actions")

class LearningPattern(Base):
    """Learning patterns model for tracking task outcomes."""
    __tablename__ = 'learning_patterns'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('agents.id'), nullable=False)
    task_type = Column(String(100), nullable=False)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    avg_execution_time_ms = Column(Integer)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agent = relationship("Agent", back_populates="learning_patterns")

# Database configuration class
class DatabaseConfig:
    """Database configuration and connection management."""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
    
    def initialize(self):
        """Initialize database connection and session factory."""
        self.engine = create_engine(
            self.database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=300
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all tables in the database."""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get a database session."""
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.SessionLocal()