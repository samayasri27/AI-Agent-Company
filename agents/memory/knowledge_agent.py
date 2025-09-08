# agents/memory/knowledge_agent.py

import json
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, text
from sqlalchemy.exc import SQLAlchemyError

from agents.agent_base import AgentBase
from database.models import DatabaseConfig, KnowledgeEntry, Agent
from config.memory_config import load_memory_config
from .security_validator import SecurityValidator
from .error_handler import ErrorHandler, with_error_handling, ValidationError, SecurityError


class KnowledgeAgent(AgentBase):
    """
    Specialized agent for managing structured and unstructured knowledge storage and retrieval.
    Handles data storage with vector embeddings for semantic search.
    """
    
    def __init__(self, name="Knowledge Agent", department="memory", role="Knowledge Manager", memory=None):
        super().__init__(name, department, role, memory)
        
        # Load configuration and initialize database
        self.config = load_memory_config()
        self.db_config = DatabaseConfig(self.config.get_database_url())
        self.db_config.initialize()
        
        # Initialize error handling
        self.error_handler = ErrorHandler()
        
        # Cache for frequently accessed data
        self._cache = {}
        self._cache_size = self.config.cache_size
        
        self.log("Knowledge Agent initialized with database connection")
    
    async def execute_task(self, task: str):
        """
        Execute knowledge-related tasks
        """
        self.log(f"Processing knowledge task: {task}")
        
        # Parse task and route to appropriate method
        if task.startswith("store_structured:"):
            data = json.loads(task.split(":", 1)[1])
            return self.store_structured(data["agent_id"], data["data"], data.get("schema"))
        elif task.startswith("store_unstructured:"):
            data = json.loads(task.split(":", 1)[1])
            return self.store_unstructured(data["agent_id"], data["content"], data.get("metadata"))
        elif task.startswith("search_similar:"):
            data = json.loads(task.split(":", 1)[1])
            return self.search_similar(data["query"], data.get("top_k", 5), data.get("filters"))
        else:
            return f"Knowledge Agent processed: {task}"
    
    @with_error_handling(ErrorHandler(), "store_data")
    def store_data(self, agent_id: str, data_type: str, content: str, metadata: dict = None):
        """
        Store data with appropriate processing based on type
        """
        self.log(f"Storing {data_type} data for agent {agent_id}")
        
        # Input validation
        if not SecurityValidator.validate_agent_id(agent_id):
            raise ValidationError("Invalid agent ID format", details={'field': 'agent_id'})
        
        if not data_type or data_type not in ["structured", "unstructured"]:
            raise ValidationError("Data type must be 'structured' or 'unstructured'", details={'field': 'data_type'})
        
        if not content or not isinstance(content, str):
            raise ValidationError("Content must be a non-empty string", details={'field': 'content'})
        
        # Sanitize content
        sanitized_content = SecurityValidator.sanitize_content(content, data_type)
        
        # Validate metadata if provided
        sanitized_metadata = None
        if metadata:
            sanitized_metadata = SecurityValidator.validate_metadata(metadata)
        
        if data_type == "structured":
            # Parse content as JSON for structured data
            try:
                data = json.loads(sanitized_content) if isinstance(sanitized_content, str) else sanitized_content
            except json.JSONDecodeError as e:
                raise ValidationError(f"Invalid JSON content: {str(e)}", details={'field': 'content'})
            return self.store_structured(agent_id, data, sanitized_metadata.get("schema") if sanitized_metadata else None)
        elif data_type == "unstructured":
            return self.store_unstructured(agent_id, sanitized_content, sanitized_metadata)
    
    def retrieve_data(self, agent_id: str, query: str, data_type: str = None, filters: dict = None):
        """
        Retrieve data based on query and filters
        """
        self.log(f"Retrieving data for agent {agent_id} with query: {query}")
        
        try:
            session = self.db_config.get_session()
            
            # Build base query
            query_obj = session.query(KnowledgeEntry).filter(
                KnowledgeEntry.agent_id == agent_id
            )
            
            # Apply data type filter if specified
            if data_type:
                query_obj = query_obj.filter(KnowledgeEntry.content_type == data_type)
            
            # Apply additional filters
            if filters:
                for key, value in filters.items():
                    if key == "created_after":
                        query_obj = query_obj.filter(KnowledgeEntry.created_at >= value)
                    elif key == "created_before":
                        query_obj = query_obj.filter(KnowledgeEntry.created_at <= value)
                    elif key == "metadata_contains":
                        # Search in JSONB metadata
                        query_obj = query_obj.filter(
                            KnowledgeEntry.entry_metadata.contains(value)
                        )
            
            # Execute query
            results = query_obj.all()
            
            # Convert to dictionary format
            formatted_results = []
            for entry in results:
                formatted_results.append({
                    "id": str(entry.id),
                    "agent_id": str(entry.agent_id),
                    "content_type": entry.content_type,
                    "content": entry.content,
                    "metadata": entry.entry_metadata,
                    "created_at": entry.created_at.isoformat()
                })
            
            session.close()
            return {"status": "retrieved", "agent_id": agent_id, "query": query, "results": formatted_results}
            
        except Exception as e:
            self.log(f"Error retrieving data: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    @with_error_handling(ErrorHandler(), "store_structured")
    def store_structured(self, agent_id: str, data: dict, schema: str = None):
        """
        Store structured data in relational format
        """
        self.log(f"Storing structured data for agent {agent_id}")
        
        # Validate data structure
        if not isinstance(data, dict):
            raise ValidationError("Structured data must be a dictionary")
        
        # Validate data size
        data_str = json.dumps(data)
        if len(data_str) > SecurityValidator.MAX_CONTENT_LENGTH:
            raise ValidationError(f"Data exceeds maximum size of {SecurityValidator.MAX_CONTENT_LENGTH} characters")
        
        session = self.db_config.get_session()
        
        try:
            # Create knowledge entry
            entry = KnowledgeEntry(
                agent_id=uuid.UUID(agent_id),
                content_type="structured",
                content=data_str,
                entry_metadata={"schema": schema} if schema else None,
                embedding=None  # No embedding for structured data
            )
            
            session.add(entry)
            session.commit()
            
            entry_id = str(entry.id)
            
            # Update cache
            self._update_cache(f"structured_{agent_id}_{entry_id}", data)
            
            self.log(f"Successfully stored structured data with ID: {entry_id}")
            return {
                "status": "structured_stored", 
                "agent_id": agent_id, 
                "entry_id": entry_id,
                "data_type": "structured"
            }
            
        finally:
            session.close()
    
    def store_unstructured(self, agent_id: str, content: str, metadata: dict = None):
        """
        Store unstructured data with vector embeddings
        """
        self.log(f"Storing unstructured data for agent {agent_id}")
        
        try:
            session = self.db_config.get_session()
            
            # Validate content
            if not isinstance(content, str) or not content.strip():
                raise ValueError("Content must be a non-empty string")
            
            # Generate embedding (placeholder - would use actual embedding service)
            embedding = self._generate_embedding(content)
            
            # Create knowledge entry
            entry = KnowledgeEntry(
                agent_id=uuid.UUID(agent_id),
                content_type="unstructured",
                content=content,
                entry_metadata=metadata or {},
                embedding=embedding
            )
            
            session.add(entry)
            session.commit()
            
            entry_id = str(entry.id)
            session.close()
            
            # Update cache
            self._update_cache(f"unstructured_{agent_id}_{entry_id}", content)
            
            self.log(f"Successfully stored unstructured data with ID: {entry_id}")
            return {
                "status": "unstructured_stored", 
                "agent_id": agent_id, 
                "entry_id": entry_id,
                "data_type": "unstructured"
            }
            
        except Exception as e:
            self.log(f"Error storing unstructured data: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def search_similar(self, query: str, top_k: int = 5, filters: dict = None):
        """
        Perform similarity search using vector embeddings
        """
        self.log(f"Performing similarity search for: {query}")
        
        try:
            session = self.db_config.get_session()
            
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            
            # Build similarity search query using pgvector
            similarity_query = session.query(
                KnowledgeEntry,
                KnowledgeEntry.embedding.cosine_distance(query_embedding).label('distance')
            ).filter(
                KnowledgeEntry.content_type == "unstructured",
                KnowledgeEntry.embedding.is_not(None)
            )
            
            # Apply filters if provided
            if filters:
                if "agent_id" in filters:
                    similarity_query = similarity_query.filter(
                        KnowledgeEntry.agent_id == uuid.UUID(filters["agent_id"])
                    )
                if "metadata_contains" in filters:
                    similarity_query = similarity_query.filter(
                        KnowledgeEntry.entry_metadata.contains(filters["metadata_contains"])
                    )
                if "created_after" in filters:
                    similarity_query = similarity_query.filter(
                        KnowledgeEntry.created_at >= filters["created_after"]
                    )
            
            # Order by similarity and limit results
            results = similarity_query.order_by('distance').limit(top_k).all()
            
            # Format results
            formatted_results = []
            for entry, distance in results:
                formatted_results.append({
                    "id": str(entry.id),
                    "agent_id": str(entry.agent_id),
                    "content": entry.content,
                    "metadata": entry.entry_metadata,
                    "similarity_score": 1.0 - float(distance),  # Convert distance to similarity
                    "created_at": entry.created_at.isoformat()
                })
            
            session.close()
            
            self.log(f"Found {len(formatted_results)} similar entries")
            return {
                "status": "searched", 
                "query": query, 
                "results": formatted_results,
                "total_results": len(formatted_results)
            }
            
        except Exception as e:
            self.log(f"Error performing similarity search: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_by_id(self, data_id: str):
        """
        Retrieve specific data by ID
        """
        self.log(f"Retrieving data by ID: {data_id}")
        
        try:
            # Check cache first
            cache_key = f"entry_{data_id}"
            if cache_key in self._cache:
                self.log("Retrieved from cache")
                return {"status": "retrieved_by_id", "data": self._cache[cache_key], "source": "cache"}
            
            session = self.db_config.get_session()
            
            # Query by ID
            entry = session.query(KnowledgeEntry).filter(
                KnowledgeEntry.id == uuid.UUID(data_id)
            ).first()
            
            if not entry:
                session.close()
                return {"status": "not_found", "data_id": data_id}
            
            # Format result
            result = {
                "id": str(entry.id),
                "agent_id": str(entry.agent_id),
                "content_type": entry.content_type,
                "content": entry.content,
                "metadata": entry.entry_metadata,
                "created_at": entry.created_at.isoformat()
            }
            
            session.close()
            
            # Update cache
            self._update_cache(cache_key, result)
            
            return {"status": "retrieved_by_id", "data": result, "source": "database"}
            
        except Exception as e:
            self.log(f"Error retrieving data by ID: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate vector embedding for text content.
        This is a placeholder implementation - in production, this would call
        an actual embedding service like OpenAI's text-embedding-ada-002.
        """
        # Placeholder: Generate a simple hash-based embedding for testing
        # In production, replace with actual embedding service call
        import hashlib
        
        # Create a deterministic "embedding" based on text hash
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hash to vector of specified dimension
        embedding = []
        for i in range(0, min(len(text_hash), self.config.vector_dimension // 4)):
            # Convert hex pairs to normalized floats
            hex_pair = text_hash[i*2:(i*2)+2] if i*2+1 < len(text_hash) else text_hash[i*2:] + "0"
            value = int(hex_pair, 16) / 255.0  # Normalize to 0-1
            embedding.extend([value, -value, value * 0.5, -value * 0.5])  # Expand to fill dimension
        
        # Pad or truncate to exact dimension
        while len(embedding) < self.config.vector_dimension:
            embedding.append(0.0)
        embedding = embedding[:self.config.vector_dimension]
        
        return embedding
    
    def _update_cache(self, key: str, value: Any):
        """
        Update the internal cache with size limit
        """
        if len(self._cache) >= self._cache_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        self._cache[key] = value
    
    def clear_cache(self):
        """
        Clear the internal cache
        """
        self._cache.clear()
        self.log("Cache cleared")
    
    def get_cache_stats(self):
        """
        Get cache statistics
        """
        return {
            "cache_size": len(self._cache),
            "max_cache_size": self._cache_size,
            "cache_keys": list(self._cache.keys())
        }