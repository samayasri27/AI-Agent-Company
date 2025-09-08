#!/usr/bin/env python3
"""
Database initialization script for the centralized memory system.
Run this script to set up the database with all required tables and indexes.
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.setup import initialize_database
from config.memory_config import load_memory_config

def main():
    """Initialize the database for the centralized memory system."""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting database initialization...")
        
        # Load configuration
        config = load_memory_config()
        logger.info(f"Loaded configuration for Supabase project: {config.supabase_url}")
        
        # Initialize database
        db_config = initialize_database()
        logger.info("Database initialization completed successfully!")
        
        # Test connection
        with db_config.get_session() as session:
            result = session.execute("SELECT 1 as test")
            test_value = result.scalar()
            if test_value == 1:
                logger.info("Database connection test passed!")
            else:
                logger.error("Database connection test failed!")
                return 1
        
        logger.info("All database setup tasks completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)