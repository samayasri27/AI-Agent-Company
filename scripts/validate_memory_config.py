#!/usr/bin/env python3
"""
Configuration validation script for the centralized memory system.
Validates environment variables, database connectivity, and system readiness.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.memory_config import MemoryConfig, load_memory_config, check_environment_file

class ConfigValidator:
    """Validates memory system configuration and environment."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.issues: List[Dict[str, Any]] = []
    
    def add_issue(self, level: str, category: str, message: str, fix: str = None):
        """Add a configuration issue."""
        self.issues.append({
            'level': level,
            'category': category,
            'message': message,
            'fix': fix
        })
    
    def validate_environment_file(self) -> bool:
        """Validate .env file exists and has required variables."""
        env_file = Path('.env')
        
        if not env_file.exists():
            self.add_issue(
                'ERROR',
                'Environment',
                '.env file not found',
                'Run: cp .env.example .env and update with your credentials'
            )
            return False
        
        # Check for required variables
        required_vars = [
            'SUPABASE_URL',
            'SUPABASE_ANON_KEY',
            'SUPABASE_SERVICE_KEY'
        ]
        
        env_content = env_file.read_text()
        missing_vars = []
        placeholder_vars = []
        
        for var in required_vars:
            if f"{var}=" not in env_content:
                missing_vars.append(var)
            elif any(placeholder in env_content for placeholder in ['your_', 'your-project']):
                if f"{var}=your_" in env_content or f"{var}=https://your-project" in env_content:
                    placeholder_vars.append(var)
        
        if missing_vars:
            self.add_issue(
                'ERROR',
                'Environment',
                f'Missing required environment variables: {", ".join(missing_vars)}',
                'Add the missing variables to your .env file'
            )
        
        if placeholder_vars:
            self.add_issue(
                'WARNING',
                'Environment',
                f'Placeholder values detected for: {", ".join(placeholder_vars)}',
                'Update .env file with your actual Supabase credentials'
            )
        
        return len(missing_vars) == 0
    
    def validate_configuration(self) -> tuple[bool, MemoryConfig]:
        """Validate memory system configuration."""
        try:
            config = load_memory_config()
            
            # Additional validation checks
            self.validate_supabase_config(config)
            self.validate_memory_settings(config)
            self.validate_database_settings(config)
            
            return True, config
            
        except Exception as e:
            self.add_issue(
                'ERROR',
                'Configuration',
                f'Configuration validation failed: {str(e)}',
                'Check your .env file and fix the configuration errors'
            )
            return False, None
    
    def validate_supabase_config(self, config: MemoryConfig):
        """Validate Supabase-specific configuration."""
        # Check URL format
        if not config.supabase_url.startswith('https://'):
            self.add_issue(
                'ERROR',
                'Supabase',
                'Supabase URL must start with https://',
                'Update SUPABASE_URL in .env file'
            )
        
        if not config.supabase_url.endswith('.supabase.co'):
            self.add_issue(
                'ERROR',
                'Supabase',
                'Supabase URL must end with .supabase.co',
                'Verify your Supabase project URL'
            )
        
        # Check key lengths (basic validation)
        if len(config.supabase_anon_key) < 100:
            self.add_issue(
                'WARNING',
                'Supabase',
                'Supabase anonymous key seems too short',
                'Verify your SUPABASE_ANON_KEY is correct'
            )
        
        if len(config.supabase_service_key) < 100:
            self.add_issue(
                'WARNING',
                'Supabase',
                'Supabase service key seems too short',
                'Verify your SUPABASE_SERVICE_KEY is correct'
            )
    
    def validate_memory_settings(self, config: MemoryConfig):
        """Validate memory system settings."""
        # Cache size validation
        if config.cache_size > 10000:
            self.add_issue(
                'WARNING',
                'Memory',
                f'Cache size ({config.cache_size}) is very large',
                'Consider reducing MEMORY_CACHE_SIZE for better memory usage'
            )
        
        # Vector dimension validation
        supported_dimensions = [1536, 3072, 512, 768]  # Common embedding dimensions
        if config.vector_dimension not in supported_dimensions:
            self.add_issue(
                'WARNING',
                'Memory',
                f'Vector dimension ({config.vector_dimension}) may not be supported',
                f'Consider using one of: {", ".join(map(str, supported_dimensions))}'
            )
        
        # Embedding model validation
        supported_models = [
            'text-embedding-ada-002',
            'text-embedding-3-small', 
            'text-embedding-3-large'
        ]
        if config.embedding_model not in supported_models:
            self.add_issue(
                'WARNING',
                'Memory',
                f'Embedding model ({config.embedding_model}) may not be supported',
                f'Consider using one of: {", ".join(supported_models)}'
            )
    
    def validate_database_settings(self, config: MemoryConfig):
        """Validate database connection settings."""
        # Connection pool validation
        if config.connection_pool_size > 50:
            self.add_issue(
                'WARNING',
                'Database',
                f'Connection pool size ({config.connection_pool_size}) is very large',
                'Consider reducing DB_POOL_SIZE for better resource usage'
            )
        
        if config.connection_max_overflow > config.connection_pool_size * 2:
            self.add_issue(
                'WARNING',
                'Database',
                'Max overflow is much larger than pool size',
                'Consider balancing DB_POOL_SIZE and DB_MAX_OVERFLOW'
            )
    
    def test_database_connectivity(self, config: MemoryConfig) -> bool:
        """Test database connectivity."""
        try:
            from sqlalchemy import create_engine, text
            
            # Create test engine with short timeout
            engine = create_engine(
                config.get_database_url(),
                pool_timeout=5,
                connect_args={'connect_timeout': 5}
            )
            
            # Test connection
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                if result.fetchone()[0] != 1:
                    raise ValueError("Connection test failed")
            
            # Test pgvector extension
            with engine.connect() as conn:
                result = conn.execute(text(
                    "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')"
                ))
                if not result.fetchone()[0]:
                    self.add_issue(
                        'WARNING',
                        'Database',
                        'pgvector extension not found',
                        'Enable pgvector extension in your Supabase database'
                    )
            
            return True
            
        except Exception as e:
            self.add_issue(
                'ERROR',
                'Database',
                f'Database connectivity test failed: {str(e)}',
                'Check your Supabase credentials and database status'
            )
            return False
    
    def run_validation(self) -> bool:
        """Run complete configuration validation."""
        self.logger.info("🔍 Validating Memory System Configuration")
        self.logger.info("=" * 50)
        
        success = True
        
        # Step 1: Validate environment file
        if not self.validate_environment_file():
            success = False
        
        # Step 2: Validate configuration
        config_valid, config = self.validate_configuration()
        if not config_valid:
            success = False
        
        # Step 3: Test database connectivity (only if config is valid)
        if config and not self.test_database_connectivity(config):
            success = False
        
        # Report results
        self.report_results()
        
        return success and len([i for i in self.issues if i['level'] == 'ERROR']) == 0
    
    def report_results(self):
        """Report validation results."""
        self.logger.info("=" * 50)
        
        # Group issues by level
        errors = [i for i in self.issues if i['level'] == 'ERROR']
        warnings = [i for i in self.issues if i['level'] == 'WARNING']
        
        if errors:
            self.logger.error(f"❌ Found {len(errors)} error(s):")
            for issue in errors:
                self.logger.error(f"  [{issue['category']}] {issue['message']}")
                if issue.get('fix'):
                    self.logger.error(f"    Fix: {issue['fix']}")
        
        if warnings:
            self.logger.warning(f"⚠️  Found {len(warnings)} warning(s):")
            for issue in warnings:
                self.logger.warning(f"  [{issue['category']}] {issue['message']}")
                if issue.get('fix'):
                    self.logger.warning(f"    Fix: {issue['fix']}")
        
        if not errors and not warnings:
            self.logger.info("✅ All configuration checks passed!")
        elif not errors:
            self.logger.info("✅ Configuration is valid (with warnings)")
        else:
            self.logger.error("❌ Configuration validation failed")

def main():
    """Main validation function."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Change to project root
    os.chdir(project_root)
    
    # Run validation
    validator = ConfigValidator()
    success = validator.run_validation()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()