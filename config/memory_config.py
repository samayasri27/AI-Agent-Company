"""
Configuration module for the centralized memory system.
Handles environment variables, database settings, and system configuration.
"""

import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class MemoryConfig:
    """Configuration class for memory system settings."""
    
    # Supabase Configuration
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    
    # Memory System Configuration
    cache_size: int = 1000
    embedding_model: str = "text-embedding-ada-002"
    vector_dimension: int = 1536
    
    # Database Configuration
    connection_pool_size: int = 10
    connection_max_overflow: int = 20
    connection_pool_recycle: int = 300
    
    # Development Settings
    debug_memory: bool = False
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> 'MemoryConfig':
        """Create configuration from environment variables."""
        
        # Required environment variables
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
        supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not supabase_url:
            raise ValueError("SUPABASE_URL environment variable is required")
        if not supabase_anon_key:
            raise ValueError("SUPABASE_ANON_KEY environment variable is required")
        if not supabase_service_key:
            raise ValueError("SUPABASE_SERVICE_KEY environment variable is required")
        
        return cls(
            supabase_url=supabase_url,
            supabase_anon_key=supabase_anon_key,
            supabase_service_key=supabase_service_key,
            cache_size=int(os.getenv('MEMORY_CACHE_SIZE', '1000')),
            embedding_model=os.getenv('MEMORY_EMBEDDING_MODEL', 'text-embedding-ada-002'),
            vector_dimension=int(os.getenv('MEMORY_VECTOR_DIMENSION', '1536')),
            connection_pool_size=int(os.getenv('DB_POOL_SIZE', '10')),
            connection_max_overflow=int(os.getenv('DB_MAX_OVERFLOW', '20')),
            connection_pool_recycle=int(os.getenv('DB_POOL_RECYCLE', '300')),
            debug_memory=os.getenv('DEBUG_MEMORY', 'false').lower() == 'true',
            log_level=os.getenv('LOG_LEVEL', 'INFO')
        )
    
    def get_database_url(self) -> str:
        """Get PostgreSQL database URL for Supabase."""
        # Extract project ID from Supabase URL
        project_id = self.supabase_url.replace('https://', '').replace('.supabase.co', '')
        
        # Construct PostgreSQL connection URL
        return f"postgresql://postgres:{self.supabase_service_key}@db.{project_id}.supabase.co:5432/postgres"
    
    def validate(self) -> None:
        """Validate configuration settings."""
        errors = []
        
        # Validate numeric values
        if self.cache_size <= 0:
            errors.append("Cache size must be positive")
        
        if self.vector_dimension <= 0:
            errors.append("Vector dimension must be positive")
        
        if self.connection_pool_size <= 0:
            errors.append("Connection pool size must be positive")
        
        if self.connection_max_overflow < 0:
            errors.append("Connection max overflow must be non-negative")
        
        if self.connection_pool_recycle <= 0:
            errors.append("Connection pool recycle time must be positive")
        
        # Validate Supabase URL format
        if not self.supabase_url.startswith('https://'):
            errors.append("Supabase URL must start with https://")
        
        if not self.supabase_url.endswith('.supabase.co'):
            errors.append("Invalid Supabase URL format - must end with .supabase.co")
        
        # Validate keys are not placeholder values
        placeholder_values = [
            'your_supabase_url',
            'your_supabase_anon_key_here',
            'your_supabase_service_key_here',
            'your-project.supabase.co'
        ]
        
        if any(placeholder in self.supabase_url for placeholder in placeholder_values):
            errors.append("Supabase URL appears to be a placeholder value")
        
        if any(placeholder in self.supabase_anon_key for placeholder in placeholder_values):
            errors.append("Supabase anonymous key appears to be a placeholder value")
        
        if any(placeholder in self.supabase_service_key for placeholder in placeholder_values):
            errors.append("Supabase service key appears to be a placeholder value")
        
        # Validate log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level.upper() not in valid_log_levels:
            errors.append(f"Invalid log level '{self.log_level}'. Must be one of: {', '.join(valid_log_levels)}")
        
        # Validate embedding model
        supported_models = [
            'text-embedding-ada-002',
            'text-embedding-3-small',
            'text-embedding-3-large'
        ]
        if self.embedding_model not in supported_models:
            logging.warning(f"Embedding model '{self.embedding_model}' may not be supported. Supported models: {', '.join(supported_models)}")
        
        if errors:
            raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)
    
    def get_connection_params(self) -> Dict[str, Any]:
        """Get database connection parameters."""
        return {
            'pool_size': self.connection_pool_size,
            'max_overflow': self.connection_max_overflow,
            'pool_recycle': self.connection_pool_recycle,
            'pool_pre_ping': True,  # Validate connections before use
            'echo': self.debug_memory  # Log SQL queries in debug mode
        }

def load_memory_config() -> MemoryConfig:
    """Load and validate memory system configuration."""
    try:
        config = MemoryConfig.from_env()
        config.validate()
        return config
    except Exception as e:
        logging.error(f"Failed to load memory configuration: {e}")
        raise

def check_environment_file() -> bool:
    """Check if .env file exists and has required variables."""
    env_file = Path('.env')
    if not env_file.exists():
        return False
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY', 
        'SUPABASE_SERVICE_KEY'
    ]
    
    # Read .env file and check for required variables
    env_content = env_file.read_text()
    missing_vars = []
    
    for var in required_vars:
        if f"{var}=" not in env_content or f"{var}=your_" in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        logging.warning(f"Missing or placeholder values for: {', '.join(missing_vars)}")
        return False
    
    return True

def create_default_env_file() -> None:
    """Create a default .env file from .env.example if it doesn't exist."""
    env_file = Path('.env')
    example_file = Path('.env.example')
    
    if env_file.exists():
        logging.info(".env file already exists")
        return
    
    if not example_file.exists():
        logging.error(".env.example file not found")
        raise FileNotFoundError(".env.example file is required to create default .env")
    
    # Copy example to .env
    env_content = example_file.read_text()
    env_file.write_text(env_content)
    logging.info("Created .env file from .env.example template")

def setup_logging(config: MemoryConfig) -> None:
    """Setup logging configuration for memory system."""
    log_level = getattr(logging, config.log_level.upper())
    
    # Create logs directory if it doesn't exist
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / 'memory_system.log'),
            logging.StreamHandler()
        ]
    )
    
    # Set specific logger levels
    if config.debug_memory:
        logging.getLogger('agents.memory').setLevel(logging.DEBUG)
        logging.getLogger('database').setLevel(logging.DEBUG)
    else:
        logging.getLogger('agents.memory').setLevel(log_level)
        logging.getLogger('database').setLevel(log_level)