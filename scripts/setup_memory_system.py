#!/usr/bin/env python3
"""
Setup script for the centralized memory system.
Handles environment configuration, database setup, and system validation.
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.memory_config import (
    MemoryConfig, 
    load_memory_config, 
    check_environment_file, 
    create_default_env_file,
    setup_logging
)
from database.setup import initialize_database

class MemorySystemSetup:
    """Handles complete memory system setup and validation."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def check_python_dependencies(self) -> bool:
        """Check if required Python packages are installed."""
        required_packages = [
            'sqlalchemy',
            'psycopg2-binary',
            'supabase',
            'python-dotenv',
            'openai'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self.errors.append(f"Missing required packages: {', '.join(missing_packages)}")
            self.logger.error(f"Install missing packages: pip install {' '.join(missing_packages)}")
            return False
        
        self.logger.info("✅ All required Python packages are installed")
        return True
    
    def setup_environment(self) -> bool:
        """Setup environment configuration."""
        try:
            # Create .env file if it doesn't exist
            if not Path('.env').exists():
                self.logger.info("Creating .env file from template...")
                create_default_env_file()
                self.warnings.append("Created .env file from template - please update with your credentials")
            
            # Check environment file
            if not check_environment_file():
                self.warnings.append("Environment file may have placeholder values - please update with real credentials")
                return False
            
            self.logger.info("✅ Environment configuration is ready")
            return True
            
        except Exception as e:
            self.errors.append(f"Failed to setup environment: {e}")
            return False
    
    def validate_configuration(self) -> Tuple[bool, MemoryConfig]:
        """Validate memory system configuration."""
        try:
            config = load_memory_config()
            self.logger.info("✅ Memory system configuration is valid")
            return True, config
            
        except Exception as e:
            self.errors.append(f"Configuration validation failed: {e}")
            return False, None
    
    def setup_database(self, config: MemoryConfig) -> bool:
        """Setup database with tables and indexes."""
        try:
            self.logger.info("Setting up database...")
            db_config = initialize_database()
            self.logger.info("✅ Database setup completed successfully")
            return True
            
        except Exception as e:
            self.errors.append(f"Database setup failed: {e}")
            self.logger.error(f"Database setup error: {e}")
            return False
    
    def test_database_connection(self, config: MemoryConfig) -> bool:
        """Test database connection and basic operations."""
        try:
            from sqlalchemy import create_engine, text
            
            # Create test connection
            engine = create_engine(
                config.get_database_url(),
                **config.get_connection_params()
            )
            
            # Test basic connection
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1 as test"))
                test_value = result.fetchone()[0]
                
                if test_value != 1:
                    raise ValueError("Database connection test failed")
            
            # Test pgvector extension
            with engine.connect() as conn:
                result = conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector'"))
                if not result.fetchone():
                    self.warnings.append("pgvector extension not found - vector operations may not work")
            
            self.logger.info("✅ Database connection test passed")
            return True
            
        except Exception as e:
            self.errors.append(f"Database connection test failed: {e}")
            return False
    
    def create_directories(self) -> bool:
        """Create necessary directories for the memory system."""
        directories = [
            'logs',
            'data',
            'scripts'
        ]
        
        try:
            for directory in directories:
                Path(directory).mkdir(exist_ok=True)
                self.logger.debug(f"Created/verified directory: {directory}")
            
            self.logger.info("✅ Required directories created")
            return True
            
        except Exception as e:
            self.errors.append(f"Failed to create directories: {e}")
            return False
    
    def run_setup(self) -> bool:
        """Run complete memory system setup."""
        self.logger.info("🚀 Starting Memory System Setup")
        self.logger.info("=" * 50)
        
        success = True
        
        # Step 1: Check dependencies
        if not self.check_python_dependencies():
            success = False
        
        # Step 2: Setup environment
        if not self.setup_environment():
            success = False
        
        # Step 3: Create directories
        if not self.create_directories():
            success = False
        
        # Step 4: Validate configuration
        config_valid, config = self.validate_configuration()
        if not config_valid:
            success = False
        
        # Step 5: Setup logging
        if config:
            try:
                setup_logging(config)
                self.logger.info("✅ Logging configuration setup")
            except Exception as e:
                self.errors.append(f"Failed to setup logging: {e}")
                success = False
        
        # Step 6: Setup database (only if config is valid)
        if config and not self.setup_database(config):
            success = False
        
        # Step 7: Test database connection (only if database setup succeeded)
        if config and success and not self.test_database_connection(config):
            success = False
        
        # Report results
        self.logger.info("=" * 50)
        
        if self.warnings:
            self.logger.warning("⚠️  Warnings:")
            for warning in self.warnings:
                self.logger.warning(f"  - {warning}")
        
        if self.errors:
            self.logger.error("❌ Errors:")
            for error in self.errors:
                self.logger.error(f"  - {error}")
        
        if success:
            self.logger.info("🎉 Memory System Setup Completed Successfully!")
            self.logger.info("\nNext steps:")
            self.logger.info("1. Update .env file with your actual Supabase credentials")
            self.logger.info("2. Test the system with: python demo_memory_manager_integration.py")
            self.logger.info("3. Run tests with: python -m pytest tests/test_memory_*")
        else:
            self.logger.error("❌ Memory System Setup Failed!")
            self.logger.error("Please fix the errors above and run setup again.")
        
        return success

def main():
    """Main setup function."""
    # Setup basic logging for setup process
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Change to project root directory
    os.chdir(project_root)
    
    # Run setup
    setup = MemorySystemSetup()
    success = setup.run_setup()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()