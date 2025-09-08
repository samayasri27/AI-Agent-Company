# agents/memory/memory_manager_agent.py

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from agents.agent_base import AgentBase
from .knowledge_agent import KnowledgeAgent
from .history_agent import HistoryAgent
from .learning_agent import LearningAgent
from .cache_manager import CacheManager, CacheKeyGenerator
from .connection_pool import ConnectionPoolManager, ConnectionPoolFactory
from .security_validator import SecurityValidator, AccessLevel
from .error_handler import ErrorHandler, with_error_handling, ValidationError, SecurityError
from config.memory_config import load_memory_config


class MemoryManagerAgent(AgentBase):
    """
    Central coordinator for all memory operations in the AI company simulation.
    Routes requests to appropriate specialized memory agents with error handling and fallback mechanisms.
    """
    
    def __init__(self, name="Memory Manager", department="memory", role="Memory Coordinator", memory=None):
        super().__init__(name, department, role, memory)
        
        # Load configuration
        self.config = load_memory_config()
        
        # Initialize error handling and security
        self.error_handler = ErrorHandler()
        self.security_validator = SecurityValidator()
        
        # Initialize caching system
        cache_config = {
            'knowledge_cache_size': self.config.cache_size // 2,
            'knowledge_cache_ttl': 3600,
            'history_cache_size': self.config.cache_size // 4,
            'history_cache_ttl': 1800,
            'learning_cache_size': self.config.cache_size // 4,
            'learning_cache_ttl': 7200,
            'similarity_cache_size': 100,
            'similarity_cache_ttl': 900
        }
        self.cache_manager = CacheManager(cache_config)
        
        # Initialize connection pool
        pool_config = {
            'pool_size': self.config.connection_pool_size,
            'max_overflow': self.config.connection_max_overflow,
            'pool_recycle': self.config.connection_pool_recycle,
            'pool_timeout': 30,
            'connect_timeout': 10,
            'echo_sql': self.config.debug_memory
        }
        self.connection_pool = ConnectionPoolFactory.get_pool(
            self.config.get_database_url(),
            pool_config
        )
        
        # Track agent health and availability (initialize before agents)
        self._agent_health = {
            "knowledge": True,
            "history": True,
            "learning": True
        }
        
        # Request routing statistics
        self._routing_stats = {
            "total_requests": 0,
            "successful_routes": 0,
            "failed_routes": 0,
            "fallback_used": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        # Performance metrics
        self._performance_metrics = {
            "avg_response_time": 0.0,
            "total_operations": 0,
            "total_response_time": 0.0
        }
        
        # Initialize specialized memory agents with error handling
        self._initialize_specialized_agents()
        
        self.log("Memory Manager initialized with caching, connection pooling, and specialized agents")
    
    def _initialize_specialized_agents(self):
        """Initialize specialized agents with error handling"""
        try:
            self.knowledge_agent = KnowledgeAgent()
            self.log("Knowledge Agent initialized successfully")
        except Exception as e:
            self.log(f"Failed to initialize Knowledge Agent: {str(e)}")
            self.knowledge_agent = None
            self._agent_health["knowledge"] = False
        
        try:
            self.history_agent = HistoryAgent()
            self.log("History Agent initialized successfully")
        except Exception as e:
            self.log(f"Failed to initialize History Agent: {str(e)}")
            self.history_agent = None
            self._agent_health["history"] = False
        
        try:
            self.learning_agent = LearningAgent()
            self.log("Learning Agent initialized successfully")
        except Exception as e:
            self.log(f"Failed to initialize Learning Agent: {str(e)}")
            self.learning_agent = None
            self._agent_health["learning"] = False
    
    async def execute_task(self, task: str):
        """
        Execute memory-related tasks by routing to appropriate specialized agents with error handling
        """
        self.log(f"Processing memory task: {task}")
        self._routing_stats["total_requests"] += 1
        
        try:
            # Enhanced task routing logic with error handling
            if "store" in task.lower() or "save" in task.lower():
                return await self._route_storage_request(task)
            elif "retrieve" in task.lower() or "search" in task.lower():
                return await self._route_retrieval_request(task)
            elif "history" in task.lower():
                return await self._route_history_request(task)
            elif "learn" in task.lower() or "pattern" in task.lower():
                return await self._route_learning_request(task)
            else:
                return await self._handle_general_request(task)
        except Exception as e:
            self.log(f"Error executing task: {str(e)}")
            self._routing_stats["failed_routes"] += 1
            return await self._handle_fallback(task, str(e))
    
    async def _route_storage_request(self, task: str):
        """Route storage requests to Knowledge Agent with error handling"""
        self.log("Routing storage request to Knowledge Agent")
        
        if not self._agent_health["knowledge"] or not self.knowledge_agent:
            return await self._handle_agent_unavailable("knowledge", task)
        
        try:
            result = await self.knowledge_agent.execute_task(task)
            self._routing_stats["successful_routes"] += 1
            return result
        except Exception as e:
            self.log(f"Knowledge Agent error: {str(e)}")
            self._agent_health["knowledge"] = False
            return await self._handle_agent_error("knowledge", task, str(e))
    
    async def _route_retrieval_request(self, task: str):
        """Route retrieval requests to Knowledge Agent with error handling"""
        self.log("Routing retrieval request to Knowledge Agent")
        
        if not self._agent_health["knowledge"] or not self.knowledge_agent:
            return await self._handle_agent_unavailable("knowledge", task)
        
        try:
            result = await self.knowledge_agent.execute_task(task)
            self._routing_stats["successful_routes"] += 1
            return result
        except Exception as e:
            self.log(f"Knowledge Agent error: {str(e)}")
            self._agent_health["knowledge"] = False
            return await self._handle_agent_error("knowledge", task, str(e))
    
    async def _route_history_request(self, task: str):
        """Route history requests to History Agent with error handling"""
        self.log("Routing history request to History Agent")
        
        if not self._agent_health["history"] or not self.history_agent:
            return await self._handle_agent_unavailable("history", task)
        
        try:
            result = await self.history_agent.execute_task(task)
            self._routing_stats["successful_routes"] += 1
            return result
        except Exception as e:
            self.log(f"History Agent error: {str(e)}")
            self._agent_health["history"] = False
            return await self._handle_agent_error("history", task, str(e))
    
    async def _route_learning_request(self, task: str):
        """Route learning requests to Learning Agent with error handling"""
        self.log("Routing learning request to Learning Agent")
        
        if not self._agent_health["learning"] or not self.learning_agent:
            return await self._handle_agent_unavailable("learning", task)
        
        try:
            result = await self.learning_agent.execute_task(task)
            self._routing_stats["successful_routes"] += 1
            return result
        except Exception as e:
            self.log(f"Learning Agent error: {str(e)}")
            self._agent_health["learning"] = False
            return await self._handle_agent_error("learning", task, str(e))
    
    async def _handle_general_request(self, task: str):
        """Handle general memory requests with intelligent routing"""
        self.log(f"Handling general memory request: {task}")
        
        # Try to intelligently route based on task content
        task_lower = task.lower()
        
        # Check for data-related keywords
        if any(keyword in task_lower for keyword in ["data", "information", "knowledge", "content"]):
            return await self._route_storage_request(task)
        
        # Check for conversation-related keywords
        if any(keyword in task_lower for keyword in ["conversation", "chat", "message", "action", "log"]):
            return await self._route_history_request(task)
        
        # Check for analysis-related keywords
        if any(keyword in task_lower for keyword in ["analyze", "pattern", "insight", "recommendation", "metric"]):
            return await self._route_learning_request(task)
        
        # Default fallback
        self._routing_stats["successful_routes"] += 1
        return {
            "status": "general_processed",
            "message": f"Memory Manager processed general request: {task}",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _handle_agent_unavailable(self, agent_type: str, task: str):
        """Handle requests when an agent is unavailable"""
        self.log(f"{agent_type.title()} Agent is unavailable for task: {task}")
        self._routing_stats["fallback_used"] += 1
        
        return {
            "status": "agent_unavailable",
            "agent_type": agent_type,
            "task": task,
            "message": f"{agent_type.title()} Agent is currently unavailable",
            "fallback_used": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _handle_agent_error(self, agent_type: str, task: str, error: str):
        """Handle errors from specialized agents"""
        self.log(f"{agent_type.title()} Agent error for task '{task}': {error}")
        self._routing_stats["failed_routes"] += 1
        
        # Attempt to recover the agent
        await self._attempt_agent_recovery(agent_type)
        
        return {
            "status": "agent_error",
            "agent_type": agent_type,
            "task": task,
            "error": error,
            "recovery_attempted": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _handle_fallback(self, task: str, error: str):
        """Handle fallback when all routing fails"""
        self.log(f"Using fallback for task '{task}' due to error: {error}")
        self._routing_stats["fallback_used"] += 1
        
        return {
            "status": "fallback_used",
            "task": task,
            "error": error,
            "message": "Task processed using fallback mechanism",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _attempt_agent_recovery(self, agent_type: str):
        """Attempt to recover a failed agent"""
        self.log(f"Attempting to recover {agent_type} agent")
        
        try:
            if agent_type == "knowledge" and not self._agent_health["knowledge"]:
                self.knowledge_agent = KnowledgeAgent()
                self._agent_health["knowledge"] = True
                self.log("Knowledge Agent recovered successfully")
            elif agent_type == "history" and not self._agent_health["history"]:
                self.history_agent = HistoryAgent()
                self._agent_health["history"] = True
                self.log("History Agent recovered successfully")
            elif agent_type == "learning" and not self._agent_health["learning"]:
                self.learning_agent = LearningAgent()
                self._agent_health["learning"] = True
                self.log("Learning Agent recovered successfully")
        except Exception as e:
            self.log(f"Failed to recover {agent_type} agent: {str(e)}")
            self._agent_health[agent_type] = False
    
    # Public API methods for other agents to use with error handling
    
    def store_data(self, agent_id: str, data_type: str, content: str, metadata: dict = None, 
                   requesting_agent_id: str = None, requesting_agent_department: str = None):
        """
        Store data through the appropriate specialized agent with caching and error handling
        """
        start_time = time.time()
        self.log(f"Storing {data_type} data for agent {agent_id}")
        
        try:
            # Security validation
            if requesting_agent_id and requesting_agent_department:
                is_allowed, reason = SecurityValidator.validate_agent_access(
                    requesting_agent_id, requesting_agent_department, "write", agent_id
                )
                if not is_allowed:
                    return self.error_handler.handle_security_error(
                        SecurityError(f"Access denied: {reason}"),
                        requesting_agent_id, "store_data"
                    )
            
            # Input validation
            if not SecurityValidator.validate_agent_id(agent_id):
                return self.error_handler.handle_validation_error(
                    ValidationError("Invalid agent ID format"), "agent_id", agent_id
                )
            
            if not data_type or not isinstance(data_type, str):
                return self.error_handler.handle_validation_error(
                    ValidationError("Data type must be a non-empty string"), "data_type", data_type
                )
            
            if not content or not isinstance(content, str):
                return self.error_handler.handle_validation_error(
                    ValidationError("Content must be a non-empty string"), "content", content
                )
            
            # Sanitize content
            try:
                sanitized_content = SecurityValidator.sanitize_content(content, data_type)
            except ValueError as e:
                return self.error_handler.handle_validation_error(e, "content", content)
            
            # Validate and sanitize metadata
            sanitized_metadata = None
            if metadata:
                try:
                    sanitized_metadata = SecurityValidator.validate_metadata(metadata)
                except ValueError as e:
                    return self.error_handler.handle_validation_error(e, "metadata", metadata)
            
            if not self._agent_health["knowledge"] or not self.knowledge_agent:
                self.log("Knowledge Agent unavailable for data storage")
                return {
                    "status": "error",
                    "message": "Knowledge Agent is currently unavailable",
                    "agent_id": agent_id,
                    "data_type": data_type
                }
            
            result = self.knowledge_agent.store_data(agent_id, data_type, sanitized_content, sanitized_metadata)
            
            # Invalidate related cache entries on successful storage
            if result.get("status") != "error":
                self._invalidate_related_cache(agent_id, data_type, "store")
            
            # Log the action for learning purposes
            if self._agent_health["learning"] and self.learning_agent:
                try:
                    success = result.get("status") not in ["error"]
                    self.learning_agent.record_task_outcome(
                        agent_id, 
                        f"store_{data_type}", 
                        success,
                        {"operation": "store_data"}
                    )
                except Exception as e:
                    self.log(f"Failed to log learning outcome: {str(e)}")
            
            # Update performance metrics
            self._update_performance_metrics(time.time() - start_time)
            
            return result
            
        except Exception as e:
            self.log(f"Error storing data: {str(e)}")
            self._update_performance_metrics(time.time() - start_time)
            return {"status": "error", "message": str(e), "agent_id": agent_id}
    
    def retrieve_data(self, agent_id: str, query: str, data_type: str = None, filters: dict = None,
                     requesting_agent_id: str = None, requesting_agent_department: str = None):
        """
        Retrieve data through the appropriate specialized agent with caching and error handling
        """
        start_time = time.time()
        self.log(f"Retrieving data for agent {agent_id} with query: {query}")
        
        try:
            # Security validation
            if requesting_agent_id and requesting_agent_department:
                is_allowed, reason = SecurityValidator.validate_agent_access(
                    requesting_agent_id, requesting_agent_department, "read", agent_id
                )
                if not is_allowed:
                    return self.error_handler.handle_security_error(
                        SecurityError(f"Access denied: {reason}"),
                        requesting_agent_id, "retrieve_data"
                    )
            
            # Input validation
            if not SecurityValidator.validate_agent_id(agent_id):
                return self.error_handler.handle_validation_error(
                    ValidationError("Invalid agent ID format"), "agent_id", agent_id
                )
            
            # Validate and sanitize query
            try:
                sanitized_query = SecurityValidator.validate_query(query)
            except ValueError as e:
                return self.error_handler.handle_validation_error(e, "query", query)
            
            # Validate and sanitize filters
            sanitized_filters = None
            if filters:
                try:
                    sanitized_filters = SecurityValidator.validate_filters(filters)
                except ValueError as e:
                    return self.error_handler.handle_validation_error(e, "filters", filters)
            
            # Generate cache key
            filters_hash = CacheKeyGenerator.hash_content(sanitized_filters or {})
            cache_key = f"retrieve:agent:{agent_id}:type:{data_type or 'any'}:query:{CacheKeyGenerator.hash_content(sanitized_query)}:filters:{filters_hash}"
            
            # Try cache first
            knowledge_cache = self.cache_manager.get_cache('knowledge')
            cached_result = knowledge_cache.get(cache_key)
            
            if cached_result is not None:
                self._routing_stats["cache_hits"] += 1
                self.log(f"Cache hit for data retrieval: {agent_id}")
                self._update_performance_metrics(time.time() - start_time)
                return cached_result
            
            self._routing_stats["cache_misses"] += 1
            
            if not self._agent_health["knowledge"] or not self.knowledge_agent:
                self.log("Knowledge Agent unavailable for data retrieval")
                return {
                    "status": "error",
                    "message": "Knowledge Agent is currently unavailable",
                    "agent_id": agent_id,
                    "query": query
                }
            
            result = self.knowledge_agent.retrieve_data(agent_id, sanitized_query, data_type, sanitized_filters)
            
            # Cache successful results
            if result.get("status") != "error":
                knowledge_cache.put(cache_key, result, ttl_seconds=3600)  # Cache for 1 hour
            
            # Log the action for learning purposes
            if self._agent_health["learning"] and self.learning_agent:
                try:
                    success = result.get("status") not in ["error"]
                    results_count = len(result.get("results", []))
                    self.learning_agent.record_task_outcome(
                        agent_id, 
                        f"retrieve_{data_type or 'any'}", 
                        success,
                        {"operation": "retrieve_data", "results_count": results_count}
                    )
                except Exception as e:
                    self.log(f"Failed to log learning outcome: {str(e)}")
            
            # Update performance metrics
            self._update_performance_metrics(time.time() - start_time)
            
            return result
            
        except Exception as e:
            self.log(f"Error retrieving data: {str(e)}")
            self._update_performance_metrics(time.time() - start_time)
            return {"status": "error", "message": str(e), "agent_id": agent_id}
    
    def get_agent_history(self, agent_id: str, limit: int = 10, filters: dict = None):
        """
        Get agent history through History Agent with error handling
        """
        self.log(f"Getting history for agent {agent_id}")
        
        try:
            if not self._agent_health["history"] or not self.history_agent:
                self.log("History Agent unavailable for history retrieval")
                return {
                    "status": "error",
                    "message": "History Agent is currently unavailable",
                    "agent_id": agent_id
                }
            
            result = self.history_agent.get_agent_history(agent_id, limit, filters)
            
            # Log the action for learning purposes
            if self._agent_health["learning"] and self.learning_agent:
                try:
                    success = result.get("status") not in ["error"]
                    self.learning_agent.record_task_outcome(
                        agent_id, 
                        "get_history", 
                        success,
                        {"operation": "get_agent_history", "limit": limit}
                    )
                except Exception as e:
                    self.log(f"Failed to log learning outcome: {str(e)}")
            
            return result
            
        except Exception as e:
            self.log(f"Error getting agent history: {str(e)}")
            return {"status": "error", "message": str(e), "agent_id": agent_id}
    
    def get_learning_insights(self, agent_id: str, task_type: str = None):
        """
        Get learning insights through Learning Agent with error handling
        """
        self.log(f"Getting learning insights for agent {agent_id}")
        
        try:
            if not self._agent_health["learning"] or not self.learning_agent:
                self.log("Learning Agent unavailable for insights")
                return {
                    "status": "error",
                    "message": "Learning Agent is currently unavailable",
                    "agent_id": agent_id
                }
            
            return self.learning_agent.get_learning_insights(agent_id, task_type)
            
        except Exception as e:
            self.log(f"Error getting learning insights: {str(e)}")
            return {"status": "error", "message": str(e), "agent_id": agent_id}
    
    # Additional coordination methods
    
    def log_conversation(self, agent_id: str, conversation_thread: list):
        """
        Log conversation through History Agent with error handling
        """
        self.log(f"Logging conversation for agent {agent_id}")
        
        try:
            if not self._agent_health["history"] or not self.history_agent:
                self.log("History Agent unavailable for conversation logging")
                return {
                    "status": "error",
                    "message": "History Agent is currently unavailable",
                    "agent_id": agent_id
                }
            
            result = self.history_agent.log_conversation(agent_id, conversation_thread)
            
            # Log the action for learning purposes
            if self._agent_health["learning"] and self.learning_agent:
                try:
                    success = result.get("status") not in ["error"]
                    message_count = len(conversation_thread)
                    self.learning_agent.record_task_outcome(
                        agent_id, 
                        "log_conversation", 
                        success,
                        {"operation": "log_conversation", "message_count": message_count}
                    )
                except Exception as e:
                    self.log(f"Failed to log learning outcome: {str(e)}")
            
            return result
            
        except Exception as e:
            self.log(f"Error logging conversation: {str(e)}")
            return {"status": "error", "message": str(e), "agent_id": agent_id}
    
    def log_action(self, agent_id: str, action: str, context: dict = None, result: str = None):
        """
        Log action through History Agent with error handling
        """
        self.log(f"Logging action '{action}' for agent {agent_id}")
        
        try:
            if not self._agent_health["history"] or not self.history_agent:
                self.log("History Agent unavailable for action logging")
                return {
                    "status": "error",
                    "message": "History Agent is currently unavailable",
                    "agent_id": agent_id,
                    "action": action
                }
            
            history_result = self.history_agent.log_action(agent_id, action, context, result)
            
            # Also record for learning analysis
            if self._agent_health["learning"] and self.learning_agent:
                try:
                    success = history_result.get("status") not in ["error"]
                    execution_time = None
                    if isinstance(result, dict) and "execution_time_ms" in result:
                        execution_time = result["execution_time_ms"]
                    
                    self.learning_agent.record_task_outcome(
                        agent_id, 
                        action, 
                        success,
                        {"operation": "action_execution", "execution_time_ms": execution_time}
                    )
                except Exception as e:
                    self.log(f"Failed to log learning outcome: {str(e)}")
            
            return history_result
            
        except Exception as e:
            self.log(f"Error logging action: {str(e)}")
            return {"status": "error", "message": str(e), "agent_id": agent_id}
    
    def search_similar(self, query: str, top_k: int = 5, filters: dict = None):
        """
        Perform similarity search through Knowledge Agent with caching and error handling
        """
        start_time = time.time()
        self.log(f"Performing similarity search for: {query}")
        
        try:
            # Generate cache key for similarity search
            query_hash = CacheKeyGenerator.hash_content(query)
            filters_hash = CacheKeyGenerator.hash_content(filters or {})
            cache_key = CacheKeyGenerator.similarity_key(query_hash, top_k, filters_hash)
            
            # Try cache first
            similarity_cache = self.cache_manager.get_cache('similarity')
            cached_result = similarity_cache.get(cache_key)
            
            if cached_result is not None:
                self._routing_stats["cache_hits"] += 1
                self.log(f"Cache hit for similarity search: {query[:50]}...")
                self._update_performance_metrics(time.time() - start_time)
                return cached_result
            
            self._routing_stats["cache_misses"] += 1
            
            if not self._agent_health["knowledge"] or not self.knowledge_agent:
                self.log("Knowledge Agent unavailable for similarity search")
                return {
                    "status": "error",
                    "message": "Knowledge Agent is currently unavailable",
                    "query": query
                }
            
            result = self.knowledge_agent.search_similar(query, top_k, filters)
            
            # Cache successful results
            if result.get("status") != "error":
                similarity_cache.put(cache_key, result, ttl_seconds=900)  # Cache for 15 minutes
            
            # Update performance metrics
            self._update_performance_metrics(time.time() - start_time)
            
            return result
            
        except Exception as e:
            self.log(f"Error performing similarity search: {str(e)}")
            self._update_performance_metrics(time.time() - start_time)
            return {"status": "error", "message": str(e), "query": query}
    
    # System health and monitoring methods
    
    def get_system_health(self):
        """
        Get health status of all specialized agents
        """
        return {
            "memory_manager": {
                "status": "healthy",
                "agent_health": self._agent_health.copy(),
                "routing_stats": self._routing_stats.copy(),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    def get_routing_statistics(self):
        """
        Get routing statistics for monitoring
        """
        return self._routing_stats.copy()
    
    def reset_routing_statistics(self):
        """
        Reset routing statistics
        """
        self._routing_stats = {
            "total_requests": 0,
            "successful_routes": 0,
            "failed_routes": 0,
            "fallback_used": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        self.log("Routing statistics reset")
    
    async def health_check(self):
        """
        Perform health check on all specialized agents, caching, and connection pool
        """
        self.log("Performing comprehensive health check")
        
        health_results = {}
        
        # Check Knowledge Agent
        if self.knowledge_agent:
            try:
                # Simple test operation
                test_result = self.knowledge_agent.get_cache_stats() if hasattr(self.knowledge_agent, 'get_cache_stats') else {"test": "passed"}
                health_results["knowledge"] = {"status": "healthy", "details": test_result}
                self._agent_health["knowledge"] = True
            except Exception as e:
                health_results["knowledge"] = {"status": "unhealthy", "error": str(e)}
                self._agent_health["knowledge"] = False
        else:
            health_results["knowledge"] = {"status": "unavailable", "error": "Agent not initialized"}
            self._agent_health["knowledge"] = False
        
        # Check History Agent
        if self.history_agent:
            try:
                # Simple test operation
                test_result = self.history_agent.get_cache_stats() if hasattr(self.history_agent, 'get_cache_stats') else {"test": "passed"}
                health_results["history"] = {"status": "healthy", "details": test_result}
                self._agent_health["history"] = True
            except Exception as e:
                health_results["history"] = {"status": "unhealthy", "error": str(e)}
                self._agent_health["history"] = False
        else:
            health_results["history"] = {"status": "unavailable", "error": "Agent not initialized"}
            self._agent_health["history"] = False
        
        # Check Learning Agent
        if self.learning_agent:
            try:
                # Simple test operation - get metrics for a test agent
                test_result = self.learning_agent.get_success_metrics("test-agent-id")
                health_results["learning"] = {"status": "healthy", "details": {"test_completed": True}}
                self._agent_health["learning"] = True
            except Exception as e:
                health_results["learning"] = {"status": "unhealthy", "error": str(e)}
                self._agent_health["learning"] = False
        else:
            health_results["learning"] = {"status": "unavailable", "error": "Agent not initialized"}
            self._agent_health["learning"] = False
        
        # Check connection pool
        try:
            pool_status = self.connection_pool.get_pool_status()
            connection_test = self.connection_pool.test_connection()
            health_results["connection_pool"] = {
                "status": "healthy" if connection_test else "unhealthy",
                "details": pool_status
            }
        except Exception as e:
            health_results["connection_pool"] = {"status": "unhealthy", "error": str(e)}
        
        # Check cache system
        try:
            cache_stats = self.cache_manager.get_all_stats()
            health_results["cache_system"] = {
                "status": "healthy",
                "details": cache_stats
            }
        except Exception as e:
            health_results["cache_system"] = {"status": "unhealthy", "error": str(e)}
        
        return {
            "status": "health_check_completed",
            "timestamp": datetime.utcnow().isoformat(),
            "agents": health_results,
            "overall_health": all(self._agent_health.values()),
            "performance_metrics": self._performance_metrics.copy()
        }
    
    # Cache management methods
    
    def _invalidate_related_cache(self, agent_id: str, data_type: str, operation: str):
        """Invalidate cache entries related to the operation."""
        try:
            if operation == "store":
                # Invalidate retrieval caches for this agent and data type
                self.cache_manager.invalidate_agent_data(agent_id)
                self.cache_manager.invalidate_data_type(data_type)
            elif operation == "update":
                # Invalidate specific caches
                self.cache_manager.invalidate_agent_data(agent_id)
            
            self.log(f"Cache invalidated for agent {agent_id}, type {data_type}, operation {operation}")
        except Exception as e:
            self.log(f"Error invalidating cache: {str(e)}")
    
    def _update_performance_metrics(self, response_time: float):
        """Update performance metrics with new response time."""
        self._performance_metrics["total_operations"] += 1
        self._performance_metrics["total_response_time"] += response_time
        self._performance_metrics["avg_response_time"] = (
            self._performance_metrics["total_response_time"] / 
            self._performance_metrics["total_operations"]
        )
    
    def get_cache_stats(self):
        """Get comprehensive cache statistics."""
        try:
            cache_stats = self.cache_manager.get_all_stats()
            cache_stats["routing_cache_stats"] = {
                "cache_hits": self._routing_stats["cache_hits"],
                "cache_misses": self._routing_stats["cache_misses"],
                "hit_rate": (
                    self._routing_stats["cache_hits"] / 
                    (self._routing_stats["cache_hits"] + self._routing_stats["cache_misses"])
                    if (self._routing_stats["cache_hits"] + self._routing_stats["cache_misses"]) > 0 
                    else 0
                )
            }
            return cache_stats
        except Exception as e:
            self.log(f"Error getting cache stats: {str(e)}")
            return {"error": str(e)}
    
    def get_connection_pool_stats(self):
        """Get connection pool statistics."""
        try:
            return self.connection_pool.get_pool_status()
        except Exception as e:
            self.log(f"Error getting connection pool stats: {str(e)}")
            return {"error": str(e)}
    
    def get_performance_metrics(self):
        """Get performance metrics."""
        return {
            "performance": self._performance_metrics.copy(),
            "routing": self._routing_stats.copy(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def clear_all_caches(self):
        """Clear all cache instances."""
        try:
            self.cache_manager.clear_all_caches()
            self.log("All caches cleared")
            return {"status": "success", "message": "All caches cleared"}
        except Exception as e:
            self.log(f"Error clearing caches: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def reset_performance_metrics(self):
        """Reset performance metrics."""
        self._performance_metrics = {
            "avg_response_time": 0.0,
            "total_operations": 0,
            "total_response_time": 0.0
        }
        self.reset_routing_statistics()
        self.connection_pool.reset_stats()
        self.log("Performance metrics reset")
    
    def shutdown(self):
        """Shutdown the memory manager and cleanup resources."""
        try:
            self.cache_manager.shutdown()
            self.connection_pool.close()
            self.log("Memory Manager shutdown completed")
        except Exception as e:
            self.log(f"Error during shutdown: {str(e)}")