"""
Database connection pool manager for the centralized memory system.
Provides efficient connection pooling, health monitoring, and connection lifecycle management.
"""

import time
import threading
import logging
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError
from datetime import datetime, timedelta


class ConnectionPoolStats:
    """Statistics tracking for connection pool."""
    
    def __init__(self):
        self.connections_created = 0
        self.connections_closed = 0
        self.connections_active = 0
        self.connections_checked_out = 0
        self.connection_errors = 0
        self.query_count = 0
        self.total_query_time = 0.0
        self.last_reset = datetime.utcnow()
        self._lock = threading.Lock()
    
    def record_connection_created(self):
        with self._lock:
            self.connections_created += 1
            self.connections_active += 1
    
    def record_connection_closed(self):
        with self._lock:
            self.connections_closed += 1
            self.connections_active = max(0, self.connections_active - 1)
    
    def record_connection_checkout(self):
        with self._lock:
            self.connections_checked_out += 1
    
    def record_connection_error(self):
        with self._lock:
            self.connection_errors += 1
    
    def record_query(self, execution_time: float):
        with self._lock:
            self.query_count += 1
            self.total_query_time += execution_time
    
    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            avg_query_time = (
                self.total_query_time / self.query_count 
                if self.query_count > 0 else 0
            )
            
            return {
                'connections_created': self.connections_created,
                'connections_closed': self.connections_closed,
                'connections_active': self.connections_active,
                'connections_checked_out': self.connections_checked_out,
                'connection_errors': self.connection_errors,
                'query_count': self.query_count,
                'total_query_time': self.total_query_time,
                'avg_query_time': avg_query_time,
                'last_reset': self.last_reset.isoformat()
            }
    
    def reset(self):
        with self._lock:
            self.connections_created = 0
            self.connections_closed = 0
            self.connection_errors = 0
            self.query_count = 0
            self.total_query_time = 0.0
            self.last_reset = datetime.utcnow()


class HealthMonitor:
    """Monitors database connection health."""
    
    def __init__(self, pool_manager):
        self.pool_manager = pool_manager
        self.is_healthy = True
        self.last_check = None
        self.consecutive_failures = 0
        self.max_failures = 3
        self._lock = threading.Lock()
    
    def check_health(self) -> bool:
        """Perform health check on database connection."""
        with self._lock:
            try:
                with self.pool_manager.get_session() as session:
                    # Simple query to test connection
                    result = session.execute(text("SELECT 1"))
                    result.fetchone()
                
                self.is_healthy = True
                self.consecutive_failures = 0
                self.last_check = datetime.utcnow()
                return True
                
            except Exception as e:
                self.consecutive_failures += 1
                self.last_check = datetime.utcnow()
                
                if self.consecutive_failures >= self.max_failures:
                    self.is_healthy = False
                
                logging.warning(f"Database health check failed: {e}")
                return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get health status information."""
        with self._lock:
            return {
                'is_healthy': self.is_healthy,
                'last_check': self.last_check.isoformat() if self.last_check else None,
                'consecutive_failures': self.consecutive_failures,
                'max_failures': self.max_failures
            }


class ConnectionPoolManager:
    """Manages database connection pool with monitoring and health checks."""
    
    def __init__(self, database_url: str, config: Dict[str, Any]):
        self.database_url = database_url
        self.config = config
        self.engine = None
        self.SessionLocal = None
        self.stats = ConnectionPoolStats()
        self.health_monitor = HealthMonitor(self)
        self._lock = threading.RLock()
        self._initialized = False
        
        # Health check thread
        self._health_check_thread = None
        self._health_check_running = False
        
        # Initialize connection pool
        self.initialize()
    
    def initialize(self):
        """Initialize the database connection pool."""
        with self._lock:
            if self._initialized:
                return
            
            try:
                # Create engine with connection pooling
                self.engine = create_engine(
                    self.database_url,
                    poolclass=QueuePool,
                    pool_size=self.config.get('pool_size', 10),
                    max_overflow=self.config.get('max_overflow', 20),
                    pool_pre_ping=True,
                    pool_recycle=self.config.get('pool_recycle', 3600),
                    pool_timeout=self.config.get('pool_timeout', 30),
                    echo=self.config.get('echo_sql', False),
                    connect_args={
                        'connect_timeout': self.config.get('connect_timeout', 10),
                        'application_name': 'memory_system'
                    }
                )
                
                # Create session factory
                self.SessionLocal = sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=self.engine
                )
                
                # Test initial connection
                with self.get_session() as session:
                    session.execute(text("SELECT 1"))
                
                self._initialized = True
                
                # Start health monitoring
                self._start_health_monitoring()
                
                logging.info("Database connection pool initialized successfully")
                
            except Exception as e:
                logging.error(f"Failed to initialize database connection pool: {e}")
                raise
    
    def _start_health_monitoring(self):
        """Start background health monitoring."""
        if self._health_check_running:
            return
        
        self._health_check_running = True
        self._health_check_thread = threading.Thread(
            target=self._health_check_worker,
            daemon=True
        )
        self._health_check_thread.start()
    
    def _health_check_worker(self):
        """Background worker for health checks."""
        while self._health_check_running:
            try:
                self.health_monitor.check_health()
                # Check every 5 minutes
                time.sleep(300)
            except Exception as e:
                logging.error(f"Health check worker error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    @contextmanager
    def get_session(self):
        """Get a database session with automatic cleanup."""
        if not self._initialized:
            raise RuntimeError("Connection pool not initialized")
        
        session = None
        start_time = time.time()
        
        try:
            session = self.SessionLocal()
            self.stats.record_connection_checkout()
            yield session
            session.commit()
            
        except Exception as e:
            if session:
                session.rollback()
            self.stats.record_connection_error()
            raise
        
        finally:
            if session:
                session.close()
            
            execution_time = time.time() - start_time
            self.stats.record_query(execution_time)
    
    @contextmanager
    def get_connection(self):
        """Get a raw database connection."""
        if not self._initialized:
            raise RuntimeError("Connection pool not initialized")
        
        connection = None
        start_time = time.time()
        
        try:
            connection = self.engine.connect()
            self.stats.record_connection_checkout()
            yield connection
            
        except Exception as e:
            self.stats.record_connection_error()
            raise
        
        finally:
            if connection:
                connection.close()
            
            execution_time = time.time() - start_time
            self.stats.record_query(execution_time)
    
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> Any:
        """Execute a query with connection pooling."""
        with self.get_session() as session:
            if params:
                return session.execute(text(query), params)
            else:
                return session.execute(text(query))
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_session() as session:
                result = session.execute(text("SELECT 1 as test"))
                return result.fetchone()[0] == 1
        except Exception as e:
            logging.error(f"Connection test failed: {e}")
            return False
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Get connection pool status information."""
        if not self.engine:
            return {'status': 'not_initialized'}
        
        pool = self.engine.pool
        
        return {
            'status': 'initialized' if self._initialized else 'not_initialized',
            'pool_size': pool.size(),
            'checked_in': pool.checkedin(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'invalid': pool.invalid(),
            'health': self.health_monitor.get_status(),
            'stats': self.stats.get_stats()
        }
    
    def reset_stats(self):
        """Reset connection pool statistics."""
        self.stats.reset()
    
    def close(self):
        """Close the connection pool and cleanup resources."""
        with self._lock:
            # Stop health monitoring
            self._health_check_running = False
            if self._health_check_thread and self._health_check_thread.is_alive():
                self._health_check_thread.join(timeout=5)
            
            # Close engine
            if self.engine:
                self.engine.dispose()
                self.engine = None
            
            self.SessionLocal = None
            self._initialized = False
            
            logging.info("Database connection pool closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class ConnectionPoolFactory:
    """Factory for creating and managing connection pool instances."""
    
    _instances: Dict[str, ConnectionPoolManager] = {}
    _lock = threading.Lock()
    
    @classmethod
    def get_pool(cls, database_url: str, config: Dict[str, Any]) -> ConnectionPoolManager:
        """Get or create a connection pool instance."""
        pool_key = f"{database_url}:{hash(frozenset(config.items()))}"
        
        with cls._lock:
            if pool_key not in cls._instances:
                cls._instances[pool_key] = ConnectionPoolManager(database_url, config)
            
            return cls._instances[pool_key]
    
    @classmethod
    def close_all_pools(cls):
        """Close all connection pool instances."""
        with cls._lock:
            for pool in cls._instances.values():
                pool.close()
            cls._instances.clear()
    
    @classmethod
    def get_all_pool_stats(cls) -> Dict[str, Any]:
        """Get statistics for all connection pools."""
        with cls._lock:
            return {
                pool_key: pool.get_pool_status()
                for pool_key, pool in cls._instances.items()
            }


# Utility functions for connection management
def create_connection_pool(database_url: str, config: Dict[str, Any]) -> ConnectionPoolManager:
    """Create a new connection pool with the given configuration."""
    return ConnectionPoolManager(database_url, config)


def get_default_pool_config() -> Dict[str, Any]:
    """Get default connection pool configuration."""
    return {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_recycle': 3600,
        'pool_timeout': 30,
        'connect_timeout': 10,
        'echo_sql': False
    }