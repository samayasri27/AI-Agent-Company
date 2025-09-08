# agents/memory/security_validator.py

import re
import json
import uuid
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from enum import Enum

class AccessLevel(Enum):
    """Access levels for role-based access control."""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"
    SYSTEM = "system"

class SecurityValidator:
    """
    Security validation utilities for the memory system.
    Provides input sanitization, access control, and data validation.
    """
    
    # Department-based access control mapping
    DEPARTMENT_ACCESS_LEVELS = {
        "executive": AccessLevel.ADMIN,
        "memory": AccessLevel.SYSTEM,
        "engineering": AccessLevel.READ_WRITE,
        "finance": AccessLevel.READ_WRITE,
        "marketing": AccessLevel.READ_WRITE,
        "hr": AccessLevel.READ_WRITE,
        "research": AccessLevel.READ_WRITE,
        "support": AccessLevel.READ_ONLY,
        "default": AccessLevel.READ_ONLY
    }
    
    # Maximum content lengths to prevent DoS attacks
    MAX_CONTENT_LENGTH = 100000  # 100KB
    MAX_METADATA_SIZE = 10000    # 10KB
    MAX_QUERY_LENGTH = 1000      # 1KB
    MAX_AGENT_NAME_LENGTH = 255
    MAX_TASK_TYPE_LENGTH = 100
    
    # Dangerous patterns to sanitize
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',                # JavaScript URLs
        r'on\w+\s*=[^>\s]*',          # Event handlers (improved pattern)
        r'<iframe[^>]*>.*?</iframe>',  # Iframes
        r'<object[^>]*>.*?</object>',  # Objects
        r'<embed[^>]*>.*?</embed>',    # Embeds
        r'<link[^>]*>',               # Link tags
        r'<meta[^>]*>',               # Meta tags
        r'<style[^>]*>.*?</style>',   # Style tags
    ]
    
    @classmethod
    def validate_agent_access(cls, agent_id: str, agent_department: str, 
                            operation: str, target_agent_id: str = None) -> Tuple[bool, str]:
        """
        Validate if an agent has permission to perform an operation.
        
        Args:
            agent_id: ID of the agent requesting access
            agent_department: Department of the requesting agent
            operation: Type of operation (read, write, delete, admin)
            target_agent_id: ID of the target agent (for cross-agent operations)
        
        Returns:
            Tuple of (is_allowed, reason)
        """
        try:
            # Get access level for the agent's department
            access_level = cls.DEPARTMENT_ACCESS_LEVELS.get(
                agent_department.lower(), 
                cls.DEPARTMENT_ACCESS_LEVELS["default"]
            )
            
            # System-level agents (memory department) have full access
            if access_level == AccessLevel.SYSTEM:
                return True, "System-level access granted"
            
            # Admin-level agents have broad access
            if access_level == AccessLevel.ADMIN:
                if operation in ["read", "write", "admin"]:
                    return True, "Admin-level access granted"
                elif operation == "delete":
                    # Admins can delete but with restrictions
                    if target_agent_id and target_agent_id != agent_id:
                        return True, "Admin delete access granted for other agents"
                    return True, "Admin delete access granted"
                
            # Read-write agents can read and write their own data
            if access_level == AccessLevel.READ_WRITE:
                if operation == "read":
                    return True, "Read access granted"
                elif operation == "write":
                    # Can write their own data or shared data
                    if not target_agent_id or target_agent_id == agent_id:
                        return True, "Write access granted for own data"
                    else:
                        return False, "Cannot write to other agents' data"
                elif operation in ["delete", "admin"]:
                    return False, f"Insufficient privileges for {operation} operation"
            
            # Read-only agents can only read
            if access_level == AccessLevel.READ_ONLY:
                if operation == "read":
                    return True, "Read-only access granted"
                else:
                    return False, f"Read-only access level cannot perform {operation}"
            
            return False, "Access denied - unknown access level"
            
        except Exception as e:
            logging.error(f"Error validating agent access: {str(e)}")
            return False, f"Access validation error: {str(e)}"
    
    @classmethod
    def sanitize_content(cls, content: str, content_type: str = "text") -> str:
        """
        Sanitize content to remove potentially dangerous patterns.
        
        Args:
            content: Content to sanitize
            content_type: Type of content (text, html, json)
        
        Returns:
            Sanitized content
        """
        if not isinstance(content, str):
            raise ValueError("Content must be a string")
        
        # Check content length
        if len(content) > cls.MAX_CONTENT_LENGTH:
            raise ValueError(f"Content exceeds maximum length of {cls.MAX_CONTENT_LENGTH} characters")
        
        sanitized = content
        
        # Remove dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        # Additional sanitization based on content type
        if content_type.lower() == "html":
            # More aggressive HTML sanitization
            sanitized = re.sub(r'<[^>]+>', '', sanitized)  # Remove all HTML tags
        elif content_type.lower() == "json":
            # Validate JSON structure
            try:
                json.loads(sanitized)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON content")
        
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)
        
        return sanitized.strip()
    
    @classmethod
    def validate_agent_id(cls, agent_id: str) -> bool:
        """
        Validate agent ID format.
        
        Args:
            agent_id: Agent ID to validate
        
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(agent_id, str):
            return False
        
        try:
            # Check if it's a valid UUID
            uuid.UUID(agent_id)
            return True
        except (ValueError, TypeError):
            return False
    
    @classmethod
    def validate_metadata(cls, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize metadata dictionary.
        
        Args:
            metadata: Metadata dictionary to validate
        
        Returns:
            Sanitized metadata dictionary
        """
        if not isinstance(metadata, dict):
            raise ValueError("Metadata must be a dictionary")
        
        # Check metadata size
        metadata_str = json.dumps(metadata)
        if len(metadata_str) > cls.MAX_METADATA_SIZE:
            raise ValueError(f"Metadata exceeds maximum size of {cls.MAX_METADATA_SIZE} characters")
        
        sanitized_metadata = {}
        
        for key, value in metadata.items():
            # Validate key
            if not isinstance(key, str):
                raise ValueError("Metadata keys must be strings")
            
            if len(key) > 100:  # Reasonable key length limit
                raise ValueError("Metadata key too long")
            
            # Sanitize key
            clean_key = cls.sanitize_content(key, "text")
            
            # Sanitize value based on type
            if isinstance(value, str):
                clean_value = cls.sanitize_content(value, "text")
            elif isinstance(value, (int, float, bool)):
                clean_value = value
            elif isinstance(value, (list, dict)):
                # Convert to JSON string and validate
                try:
                    json_str = json.dumps(value)
                    if len(json_str) > 1000:  # Limit nested structure size
                        raise ValueError("Nested metadata structure too large")
                    clean_value = value
                except (TypeError, ValueError) as e:
                    if "Nested metadata structure too large" in str(e):
                        raise e
                    raise ValueError("Invalid nested metadata structure")
            else:
                # Convert other types to string and sanitize
                clean_value = cls.sanitize_content(str(value), "text")
            
            sanitized_metadata[clean_key] = clean_value
        
        return sanitized_metadata
    
    @classmethod
    def validate_query(cls, query: str) -> str:
        """
        Validate and sanitize search queries.
        
        Args:
            query: Search query to validate
        
        Returns:
            Sanitized query
        """
        if not isinstance(query, str):
            raise ValueError("Query must be a string")
        
        if len(query) > cls.MAX_QUERY_LENGTH:
            raise ValueError(f"Query exceeds maximum length of {cls.MAX_QUERY_LENGTH} characters")
        
        if not query.strip():
            raise ValueError("Query cannot be empty")
        
        # Sanitize query
        sanitized = cls.sanitize_content(query, "text")
        
        # Remove potential SQL injection patterns
        sql_patterns = [
            r';\s*drop\s+table',
            r';\s*delete\s+from',
            r';\s*update\s+',
            r';\s*insert\s+into',
            r'union\s+select',
            r'--\s*',
            r'/\*.*?\*/',
        ]
        
        for pattern in sql_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
    
    @classmethod
    def validate_task_type(cls, task_type: str) -> str:
        """
        Validate task type string.
        
        Args:
            task_type: Task type to validate
        
        Returns:
            Sanitized task type
        """
        if not isinstance(task_type, str):
            raise ValueError("Task type must be a string")
        
        if len(task_type) > cls.MAX_TASK_TYPE_LENGTH:
            raise ValueError(f"Task type exceeds maximum length of {cls.MAX_TASK_TYPE_LENGTH} characters")
        
        if not task_type.strip():
            raise ValueError("Task type cannot be empty")
        
        # Allow only alphanumeric characters, underscores, hyphens, and spaces
        if not re.match(r'^[a-zA-Z0-9_\-\s]+$', task_type):
            raise ValueError("Task type contains invalid characters")
        
        return task_type.strip().lower()
    
    @classmethod
    def validate_filters(cls, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize filter parameters.
        
        Args:
            filters: Filter dictionary to validate
        
        Returns:
            Sanitized filters dictionary
        """
        if not isinstance(filters, dict):
            raise ValueError("Filters must be a dictionary")
        
        allowed_filter_keys = {
            'agent_id', 'created_after', 'created_before', 'content_type',
            'action_type', 'success', 'metadata_contains', 'date_range',
            'limit', 'offset', 'task_type'
        }
        
        sanitized_filters = {}
        
        for key, value in filters.items():
            if key not in allowed_filter_keys:
                logging.warning(f"Unknown filter key ignored: {key}")
                continue
            
            # Validate specific filter types
            if key == 'agent_id':
                if not cls.validate_agent_id(str(value)):
                    raise ValueError(f"Invalid agent ID in filters: {value}")
                sanitized_filters[key] = str(value)
            
            elif key in ['created_after', 'created_before']:
                # Validate datetime strings
                if isinstance(value, str):
                    try:
                        datetime.fromisoformat(value.replace('Z', '+00:00'))
                        sanitized_filters[key] = value
                    except ValueError:
                        raise ValueError(f"Invalid datetime format for {key}: {value}")
                elif isinstance(value, datetime):
                    sanitized_filters[key] = value.isoformat()
                else:
                    raise ValueError(f"Invalid datetime type for {key}")
            
            elif key in ['content_type', 'action_type', 'task_type']:
                sanitized_filters[key] = cls.sanitize_content(str(value), "text")
            
            elif key == 'success':
                if not isinstance(value, bool):
                    raise ValueError("Success filter must be boolean")
                sanitized_filters[key] = value
            
            elif key == 'metadata_contains':
                if isinstance(value, dict):
                    sanitized_filters[key] = cls.validate_metadata(value)
                else:
                    raise ValueError("metadata_contains filter must be a dictionary")
            
            elif key in ['limit', 'offset']:
                if not isinstance(value, int) or value < 0:
                    raise ValueError(f"{key} must be a non-negative integer")
                if key == 'limit' and value > 1000:  # Prevent excessive queries
                    raise ValueError("Limit cannot exceed 1000")
                sanitized_filters[key] = value
            
            elif key == 'date_range':
                if not isinstance(value, (list, tuple)) or len(value) != 2:
                    raise ValueError("date_range must be a tuple/list of two datetime values")
                start_date, end_date = value
                if start_date and end_date and start_date > end_date:
                    raise ValueError("Start date cannot be after end date")
                sanitized_filters[key] = value
            
            else:
                # Generic sanitization for other fields
                sanitized_filters[key] = cls.sanitize_content(str(value), "text")
        
        return sanitized_filters
    
    @classmethod
    def log_security_event(cls, event_type: str, agent_id: str, details: Dict[str, Any]):
        """
        Log security-related events for monitoring.
        
        Args:
            event_type: Type of security event
            agent_id: ID of the agent involved
            details: Additional event details
        """
        security_logger = logging.getLogger('security')
        
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'agent_id': agent_id,
            'details': details
        }
        
        if event_type in ['access_denied', 'validation_failed', 'suspicious_activity']:
            security_logger.warning(f"Security event: {json.dumps(log_entry)}")
        else:
            security_logger.info(f"Security event: {json.dumps(log_entry)}")