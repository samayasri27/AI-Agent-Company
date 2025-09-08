"""
Database setup and migration scripts for the centralized memory system.
Handles database initialization, table creation, and pgvector setup.
"""

import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from database.models import Base, DatabaseConfig

logger = logging.getLogger(__name__)

class DatabaseSetup:
    """Handles database setup and migrations."""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(database_url)
    
    def setup_pgvector_extension(self):
        """Enable pgvector extension in PostgreSQL."""
        try:
            with self.engine.connect() as conn:
                # Enable pgvector extension
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()
                logger.info("pgvector extension enabled successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to enable pgvector extension: {e}")
            raise
    
    def create_tables(self):
        """Create all database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def create_indexes(self):
        """Create database indexes for performance optimization."""
        try:
            with self.engine.connect() as conn:
                # Create pgvector index for similarity search
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS knowledge_embedding_idx 
                    ON knowledge_entries 
                    USING ivfflat (embedding vector_cosine_ops) 
                    WITH (lists = 100);
                """))
                
                # Create indexes for common queries
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_knowledge_agent_id 
                    ON knowledge_entries(agent_id);
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_conversations_agent_id 
                    ON conversations(agent_id);
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_conversations_thread_id 
                    ON conversations(thread_id);
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_actions_agent_id 
                    ON actions(agent_id);
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_actions_type 
                    ON actions(action_type);
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_learning_agent_task 
                    ON learning_patterns(agent_id, task_type);
                """))
                
                conn.commit()
                logger.info("Database indexes created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to create database indexes: {e}")
            raise
    
    def run_full_setup(self):
        """Run complete database setup including extensions, tables, and indexes."""
        logger.info("Starting database setup...")
        
        try:
            # Enable pgvector extension
            self.setup_pgvector_extension()
            
            # Create tables
            self.create_tables()
            
            # Create indexes
            self.create_indexes()
            
            logger.info("Database setup completed successfully")
            
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            raise

def get_database_url():
    """Get database URL from environment variables."""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables are required")
    
    # Extract database connection details from Supabase URL
    # Supabase URL format: https://xxx.supabase.co
    # Database URL format: postgresql://postgres:[password]@db.xxx.supabase.co:5432/postgres
    project_id = supabase_url.replace('https://', '').replace('.supabase.co', '')
    database_url = f"postgresql://postgres:{supabase_key}@db.{project_id}.supabase.co:5432/postgres"
    
    return database_url

def initialize_database():
    """Initialize database with full setup."""
    try:
        database_url = get_database_url()
        setup = DatabaseSetup(database_url)
        setup.run_full_setup()
        
        # Return configured database instance
        db_config = DatabaseConfig(database_url)
        db_config.initialize()
        return db_config
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Run database setup
    initialize_database()
    print("Database setup completed successfully!")