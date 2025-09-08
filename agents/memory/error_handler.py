# agents/memory/error_handler.py

import logging
import traceback
import time
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime
from enum import Enum
from functools import wraps
from sqlalchemy.exc import (
    SQLAlchemyError, 
    IntegrityError, 
    OperationalError, 
    DatabaseError,
    DisconnectionError,
    TimeoutError as SQLTimeoutError
)
from psycopg2.errors import (
    UniqueViolation,
    ForeignKeyViolation,
    CheckViolation,
    NotNullViolation
)

class ErrorSeverity(Enum):
    """Error severity levels for categorization."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories for better handling."""
    DATABASE = "database"
    VALIDATION = "validation"
    SECURITY = "security"
    NETWORK = "network"
    SYSTEM = "system"
    USER_INPUT = "user_input"

class MemorySystemError(Exception):
    """Base exception for memory system errors."""
    
    def __init__(self, message: str, category: ErrorCategory = ErrorCategory.SYSTEM, 
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.timestamp = datetime.utcnow()

class DatabaseConnectionError(MemorySystemError):
    """Database connection related errors."""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, ErrorCategory.DATABASE, ErrorSeverity.HIGH, details)

class ValidationError(MemorySystemError):
    """Data validation related errors."""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, ErrorCategory.VALIDATION, ErrorSeverity.MEDIUM, details)

class SecurityError(MemorySystemError):
    """Security related errors."""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, ErrorCategory.SECURITY, ErrorSeverity.HIGH, details)

class ErrorHandler:
    """
    Comprehensive error handling utilities for the memory system.
    Provides error categorization, logging, recovery strategies, and monitoring.
    """
    
    def __init__(self):
        self.error_counts = {}
        self.error_history = []
        self.max_history_size = 1000
        self.logger = logging.getLogger('memory_error_handler')
    
    def handle_database_error(self, error: Exception, operation: str, 
                            context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle database-related errors with appropriate recovery strategies.
        
        Args:
            error: The database error that occurred
            operation: The operation that failed
            context: Additional context about the operation
        
        Returns:
            Error response dictionary
        """
        context = context or {}
        error_details = {
            'operation': operation,
            'error_type': type(error).__name__,
            'context': context,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Categorize database errors
        if isinstance(error, DisconnectionError):
            return self._handle_connection_error(error, error_details)
        elif isinstance(error, SQLTimeoutError):
            return self._handle_timeout_error(error, error_details)
        elif isinstance(error, IntegrityError):
            return self._handle_integrity_error(error, error_details)
        elif isinstance(error, OperationalError):
            return self._handle_operational_error(error, error_details)
        elif isinstance(error, DatabaseError):
            return self._handle_general_database_error(error, error_details)
        else:
            return self._handle_unknown_database_error(error, error_details)
    
    def _handle_connection_error(self, error: Exception, details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle database connection errors."""
        self.logger.error(f"Database connection error: {str(error)}")
        
        self._record_error(ErrorCategory.DATABASE, ErrorSeverity.HIGH, str(error), details)
        
        return {
            'status': 'error',
            'error_type': 'database_connection',
            'message': 'Database connection failed. Please try again later.',
            'details': {
                'category': 'database',
                'severity': 'high',
                'retry_recommended': True,
                'retry_delay_seconds': 5
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _handle_timeout_error(self, error: Exception, details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle database timeout errors."""
        self.logger.warning(f"Database timeout error: {str(error)}")
        
        self._record_error(ErrorCategory.DATABASE, ErrorSeverity.MEDIUM, str(error), details)
        
        return {
            'status': 'error',
            'error_type': 'database_timeout',
            'message': 'Database operation timed out. Please try again with a simpler query.',
            'details': {
                'category': 'database',
                'severity': 'medium',
                'retry_recommended': True,
                'retry_delay_seconds': 2
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _handle_integrity_error(self, error: Exception, details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle database integrity constraint errors."""
        error_message = str(error)
        
        # Specific handling for different integrity violations
        if isinstance(error.orig, UniqueViolation):
            user_message = "A record with this information already exists."
        elif isinstance(error.orig, ForeignKeyViolation):
            user_message = "Referenced record does not exist."
        elif isinstance(error.orig, NotNullViolation):
            user_message = "Required information is missing."
        elif isinstance(error.orig, CheckViolation):
            user_message = "Data does not meet validation requirements."
        else:
            user_message = "Data integrity constraint violated."
        
        self.logger.warning(f"Database integrity error: {error_message}")
        self._record_error(ErrorCategory.DATABASE, ErrorSeverity.MEDIUM, error_message, details)
        
        return {
            'status': 'error',
            'error_type': 'data_integrity',
            'message': user_message,
            'details': {
                'category': 'database',
                'severity': 'medium',
                'retry_recommended': False
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _handle_operational_error(self, error: Exception, details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle database operational errors."""
        error_message = str(error)
        self.logger.error(f"Database operational error: {error_message}")
        
        self._record_error(ErrorCategory.DATABASE, ErrorSeverity.HIGH, error_message, details)
        
        return {
            'status': 'error',
            'error_type': 'database_operational',
            'message': 'Database operation failed. Please contact support if this persists.',
            'details': {
                'category': 'database',
                'severity': 'high',
                'retry_recommended': True,
                'retry_delay_seconds': 10
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _handle_general_database_error(self, error: Exception, details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general database errors."""
        error_message = str(error)
        self.logger.error(f"General database error: {error_message}")
        
        self._record_error(ErrorCategory.DATABASE, ErrorSeverity.HIGH, error_message, details)
        
        return {
            'status': 'error',
            'error_type': 'database_general',
            'message': 'Database error occurred. Please try again later.',
            'details': {
                'category': 'database',
                'severity': 'high',
                'retry_recommended': True,
                'retry_delay_seconds': 5
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _handle_unknown_database_error(self, error: Exception, details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unknown database errors."""
        error_message = str(error)
        self.logger.error(f"Unknown database error: {error_message}")
        
        self._record_error(ErrorCategory.DATABASE, ErrorSeverity.HIGH, error_message, details)
        
        return {
            'status': 'error',
            'error_type': 'database_unknown',
            'message': 'An unexpected database error occurred.',
            'details': {
                'category': 'database',
                'severity': 'high',
                'retry_recommended': False
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def handle_validation_error(self, error: Exception, field: str = None, 
                              value: Any = None) -> Dict[str, Any]:
        """
        Handle validation errors with user-friendly messages.
        
        Args:
            error: The validation error
            field: The field that failed validation
            value: The value that failed validation
        
        Returns:
            Error response dictionary
        """
        error_message = str(error)
        self.logger.warning(f"Validation error for field '{field}': {error_message}")
        
        details = {
            'field': field,
            'value_type': type(value).__name__ if value is not None else None,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self._record_error(ErrorCategory.VALIDATION, ErrorSeverity.MEDIUM, error_message, details)
        
        return {
            'status': 'error',
            'error_type': 'validation',
            'message': f"Validation failed: {error_message}",
            'details': {
                'category': 'validation',
                'severity': 'medium',
                'field': field,
                'retry_recommended': False
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def handle_security_error(self, error: Exception, agent_id: str = None, 
                            operation: str = None) -> Dict[str, Any]:
        """
        Handle security-related errors.
        
        Args:
            error: The security error
            agent_id: ID of the agent involved
            operation: The operation that was attempted
        
        Returns:
            Error response dictionary
        """
        error_message = str(error)
        self.logger.error(f"Security error for agent '{agent_id}' operation '{operation}': {error_message}")
        
        details = {
            'agent_id': agent_id,
            'operation': operation,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self._record_error(ErrorCategory.SECURITY, ErrorSeverity.HIGH, error_message, details)
        
        # Log security event
        from .security_validator import SecurityValidator
        SecurityValidator.log_security_event('security_error', agent_id or 'unknown', {
            'error': error_message,
            'operation': operation
        })
        
        return {
            'status': 'error',
            'error_type': 'security',
            'message': 'Access denied or security violation.',
            'details': {
                'category': 'security',
                'severity': 'high',
                'retry_recommended': False
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def handle_system_error(self, error: Exception, component: str = None) -> Dict[str, Any]:
        """
        Handle general system errors.
        
        Args:
            error: The system error
            component: The component where the error occurred
        
        Returns:
            Error response dictionary
        """
        error_message = str(error)
        self.logger.error(f"System error in component '{component}': {error_message}")
        
        details = {
            'component': component,
            'traceback': traceback.format_exc(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self._record_error(ErrorCategory.SYSTEM, ErrorSeverity.HIGH, error_message, details)
        
        return {
            'status': 'error',
            'error_type': 'system',
            'message': 'A system error occurred. Please try again later.',
            'details': {
                'category': 'system',
                'severity': 'high',
                'component': component,
                'retry_recommended': True,
                'retry_delay_seconds': 5
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _record_error(self, category: ErrorCategory, severity: ErrorSeverity, 
                     message: str, details: Dict[str, Any]):
        """Record error for monitoring and analysis."""
        error_key = f"{category.value}_{severity.value}"
        
        # Update error counts
        if error_key not in self.error_counts:
            self.error_counts[error_key] = 0
        self.error_counts[error_key] += 1
        
        # Add to error history
        error_record = {
            'category': category.value,
            'severity': severity.value,
            'message': message,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.error_history.append(error_record)
        
        # Maintain history size limit
        if len(self.error_history) > self.max_history_size:
            self.error_history = self.error_history[-self.max_history_size:]
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring."""
        return {
            'error_counts': self.error_counts.copy(),
            'total_errors': sum(self.error_counts.values()),
            'recent_errors': len([
                e for e in self.error_history 
                if datetime.fromisoformat(e['timestamp']) > 
                   datetime.utcnow().replace(hour=datetime.utcnow().hour-1)
            ]),
            'error_categories': list(set(e['category'] for e in self.error_history)),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent errors for debugging."""
        return self.error_history[-limit:] if self.error_history else []
    
    def clear_error_history(self):
        """Clear error history and reset counts."""
        self.error_history.clear()
        self.error_counts.clear()
        self.logger.info("Error history and counts cleared")

def with_error_handling(error_handler: ErrorHandler, operation_name: str = None):
    """
    Decorator for automatic error handling in memory system methods.
    
    Args:
        error_handler: ErrorHandler instance to use
        operation_name: Name of the operation for logging
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # Log successful operation
                execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                error_handler.logger.debug(f"Operation '{op_name}' completed successfully in {execution_time:.2f}ms")
                
                return result
                
            except ValidationError as e:
                return error_handler.handle_validation_error(e, e.details.get('field'))
            
            except SecurityError as e:
                return error_handler.handle_security_error(
                    e, 
                    e.details.get('agent_id'), 
                    e.details.get('operation')
                )
            
            except SQLAlchemyError as e:
                context = {
                    'function': func.__name__,
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys())
                }
                return error_handler.handle_database_error(e, op_name, context)
            
            except Exception as e:
                return error_handler.handle_system_error(e, func.__name__)
        
        return wrapper
    return decorator

# Global error handler instance
global_error_handler = ErrorHandler()