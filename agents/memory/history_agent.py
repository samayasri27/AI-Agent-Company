# agents/memory/history_agent.py

import json
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.exc import SQLAlchemyError

from agents.agent_base import AgentBase
from database.models import DatabaseConfig, Conversation, Action, Agent
from config.memory_config import load_memory_config


class HistoryAgent(AgentBase):
    """
    Specialized agent for managing conversation history and action logging.
    Maintains comprehensive logs of agent interactions and activities.
    """
    
    def __init__(self, name="History Agent", department="memory", role="History Manager", memory=None):
        super().__init__(name, department, role, memory)
        
        # Load configuration and initialize database
        self.config = load_memory_config()
        self.db_config = DatabaseConfig(self.config.get_database_url())
        self.db_config.initialize()
        
        # Cache for frequently accessed data
        self._cache = {}
        self._cache_size = self.config.cache_size
        
        self.log("History Agent initialized with database connection")
    
    async def execute_task(self, task: str):
        """
        Execute history-related tasks
        """
        self.log(f"Processing history task: {task}")
        
        # Parse task and route to appropriate method
        try:
            if task.startswith("log_conversation:"):
                data = json.loads(task.split(":", 1)[1])
                return self.log_conversation(data["agent_id"], data["conversation_thread"])
            elif task.startswith("log_action:"):
                data = json.loads(task.split(":", 1)[1])
                return self.log_action(
                    data["agent_id"], 
                    data["action"], 
                    data.get("context"), 
                    data.get("result")
                )
            elif task.startswith("get_conversation_history:"):
                data = json.loads(task.split(":", 1)[1])
                return self.get_conversation_history(
                    data["agent_id"], 
                    data.get("limit", 10), 
                    data.get("date_range")
                )
            elif task.startswith("get_action_history:"):
                data = json.loads(task.split(":", 1)[1])
                return self.get_action_history(
                    data["agent_id"], 
                    data.get("action_type"), 
                    data.get("limit", 10)
                )
            else:
                return f"History Agent processed: {task}"
        except Exception as e:
            self.log(f"Error processing task: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def log_conversation(self, agent_id: str, conversation_thread: list):
        """
        Store conversation data with context
        
        Args:
            agent_id: UUID of the agent
            conversation_thread: List of conversation messages with format:
                [{"role": "user|assistant|system", "message": "text", "metadata": {...}}]
        """
        self.log(f"Logging conversation for agent {agent_id}")
        
        try:
            session = self.db_config.get_session()
            
            # Validate input
            if not isinstance(conversation_thread, list):
                raise ValueError("Conversation thread must be a list")
            
            if not conversation_thread:
                raise ValueError("Conversation thread cannot be empty")
            
            # Generate thread ID for grouping related messages
            thread_id = str(uuid.uuid4())
            
            # Store each message in the conversation
            stored_messages = []
            for message_data in conversation_thread:
                if not isinstance(message_data, dict):
                    raise ValueError("Each message must be a dictionary")
                
                if "message" not in message_data:
                    raise ValueError("Each message must have a 'message' field")
                
                conversation = Conversation(
                    agent_id=uuid.UUID(agent_id),
                    thread_id=thread_id,
                    message=message_data["message"],
                    role=message_data.get("role", "user"),
                    conversation_metadata=message_data.get("metadata", {})
                )
                
                session.add(conversation)
                stored_messages.append({
                    "role": conversation.role,
                    "message": conversation.message,
                    "metadata": conversation.conversation_metadata
                })
            
            session.commit()
            session.close()
            
            # Update cache
            cache_key = f"conversation_{agent_id}_{thread_id}"
            self._update_cache(cache_key, stored_messages)
            
            self.log(f"Successfully logged {len(stored_messages)} messages with thread ID: {thread_id}")
            return {
                "status": "conversation_logged", 
                "agent_id": agent_id, 
                "thread_id": thread_id,
                "message_count": len(stored_messages)
            }
            
        except Exception as e:
            self.log(f"Error logging conversation: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def log_action(self, agent_id: str, action: str, context: dict = None, result: str = None):
        """
        Record agent actions with input/output tracking
        
        Args:
            agent_id: UUID of the agent
            action: Type/name of the action performed
            context: Input data and context for the action
            result: Output/result of the action
        """
        self.log(f"Logging action '{action}' for agent {agent_id}")
        
        try:
            session = self.db_config.get_session()
            
            # Validate input
            if not action or not isinstance(action, str):
                raise ValueError("Action must be a non-empty string")
            
            # Determine success based on result
            success = True
            execution_time_ms = None
            
            # Parse result if it contains execution info
            output_data = {"result": result} if result else {}
            if isinstance(result, dict):
                output_data = result
                success = result.get("success", True)
                execution_time_ms = result.get("execution_time_ms")
            
            # Create action record
            action_record = Action(
                agent_id=uuid.UUID(agent_id),
                action_type=action,
                input_data=context or {},
                output_data=output_data,
                success=success,
                execution_time_ms=execution_time_ms
            )
            
            session.add(action_record)
            session.commit()
            
            action_id = str(action_record.id)
            session.close()
            
            # Update cache
            cache_key = f"action_{agent_id}_{action_id}"
            self._update_cache(cache_key, {
                "action_type": action,
                "input_data": context,
                "output_data": output_data,
                "success": success,
                "execution_time_ms": execution_time_ms
            })
            
            self.log(f"Successfully logged action with ID: {action_id}")
            return {
                "status": "action_logged", 
                "agent_id": agent_id, 
                "action_id": action_id,
                "action": action,
                "success": success
            }
            
        except Exception as e:
            self.log(f"Error logging action: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_conversation_history(self, agent_id: str, limit: int = 10, date_range: tuple = None):
        """
        Retrieve conversation history with filtering
        
        Args:
            agent_id: UUID of the agent
            limit: Maximum number of conversations to return
            date_range: Tuple of (start_date, end_date) for filtering
        """
        self.log(f"Getting conversation history for agent {agent_id}")
        
        try:
            session = self.db_config.get_session()
            
            # Build base query
            query = session.query(Conversation).filter(
                Conversation.agent_id == uuid.UUID(agent_id)
            )
            
            # Apply date range filter if provided
            if date_range:
                start_date, end_date = date_range
                if start_date:
                    query = query.filter(Conversation.created_at >= start_date)
                if end_date:
                    query = query.filter(Conversation.created_at <= end_date)
            
            # Order by creation time (newest first) and limit
            conversations = query.order_by(desc(Conversation.created_at)).limit(limit).all()
            
            # Group conversations by thread_id
            threads = {}
            for conv in conversations:
                thread_id = conv.thread_id or "single_message"
                if thread_id not in threads:
                    threads[thread_id] = []
                
                threads[thread_id].append({
                    "id": str(conv.id),
                    "role": conv.role,
                    "message": conv.message,
                    "metadata": conv.conversation_metadata,
                    "created_at": conv.created_at.isoformat()
                })
            
            # Sort messages within each thread by creation time
            for thread_id in threads:
                threads[thread_id].sort(key=lambda x: x["created_at"])
            
            session.close()
            
            # Format results
            formatted_threads = []
            for thread_id, messages in threads.items():
                formatted_threads.append({
                    "thread_id": thread_id,
                    "message_count": len(messages),
                    "messages": messages,
                    "first_message_at": messages[0]["created_at"] if messages else None,
                    "last_message_at": messages[-1]["created_at"] if messages else None
                })
            
            # Sort threads by last message time (newest first)
            formatted_threads.sort(key=lambda x: x["last_message_at"] or "", reverse=True)
            
            self.log(f"Retrieved {len(formatted_threads)} conversation threads")
            return {
                "status": "conversations_retrieved", 
                "agent_id": agent_id, 
                "conversations": formatted_threads,
                "total_threads": len(formatted_threads)
            }
            
        except Exception as e:
            self.log(f"Error retrieving conversation history: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_action_history(self, agent_id: str, action_type: str = None, limit: int = 10):
        """
        Retrieve action history with optional filtering by action type
        
        Args:
            agent_id: UUID of the agent
            action_type: Optional filter for specific action types
            limit: Maximum number of actions to return
        """
        self.log(f"Getting action history for agent {agent_id}")
        
        try:
            session = self.db_config.get_session()
            
            # Build base query
            query = session.query(Action).filter(
                Action.agent_id == uuid.UUID(agent_id)
            )
            
            # Apply action type filter if provided
            if action_type:
                query = query.filter(Action.action_type == action_type)
            
            # Order by creation time (newest first) and limit
            actions = query.order_by(desc(Action.created_at)).limit(limit).all()
            
            # Format results
            formatted_actions = []
            for action in actions:
                formatted_actions.append({
                    "id": str(action.id),
                    "action_type": action.action_type,
                    "input_data": action.input_data,
                    "output_data": action.output_data,
                    "success": action.success,
                    "execution_time_ms": action.execution_time_ms,
                    "created_at": action.created_at.isoformat()
                })
            
            session.close()
            
            self.log(f"Retrieved {len(formatted_actions)} actions")
            return {
                "status": "actions_retrieved", 
                "agent_id": agent_id, 
                "actions": formatted_actions,
                "total_actions": len(formatted_actions),
                "action_type_filter": action_type
            }
            
        except Exception as e:
            self.log(f"Error retrieving action history: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_agent_history(self, agent_id: str, limit: int = 10, filters: dict = None):
        """
        Get comprehensive history for an agent (both conversations and actions)
        
        Args:
            agent_id: UUID of the agent
            limit: Maximum number of items to return per category
            filters: Optional filters for date range, action types, etc.
        """
        self.log(f"Getting comprehensive history for agent {agent_id} (limit: {limit})")
        
        try:
            # Get conversation history
            date_range = None
            if filters and "date_range" in filters:
                date_range = filters["date_range"]
            
            conversations = self.get_conversation_history(agent_id, limit, date_range)
            
            # Get action history
            action_type = None
            if filters and "action_type" in filters:
                action_type = filters["action_type"]
            
            actions = self.get_action_history(agent_id, action_type, limit)
            
            # Combine and return results
            return {
                "status": "history_retrieved", 
                "agent_id": agent_id, 
                "limit": limit,
                "filters": filters or {},
                "conversations": conversations.get("conversations", []),
                "actions": actions.get("actions", []),
                "summary": {
                    "total_conversation_threads": conversations.get("total_threads", 0),
                    "total_actions": actions.get("total_actions", 0)
                }
            }
            
        except Exception as e:
            self.log(f"Error retrieving comprehensive history: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_recent_activity(self, agent_id: str, hours: int = 24):
        """
        Get recent activity for an agent within specified hours
        
        Args:
            agent_id: UUID of the agent
            hours: Number of hours to look back
        """
        self.log(f"Getting recent activity for agent {agent_id} (last {hours} hours)")
        
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Get recent conversations and actions
            date_range = (cutoff_time, None)
            recent_history = self.get_agent_history(
                agent_id, 
                limit=50,  # Higher limit for recent activity
                filters={"date_range": date_range}
            )
            
            if recent_history["status"] == "error":
                return recent_history
            
            # Add activity summary
            recent_history["activity_period_hours"] = hours
            recent_history["cutoff_time"] = cutoff_time.isoformat()
            
            return recent_history
            
        except Exception as e:
            self.log(f"Error retrieving recent activity: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_action_statistics(self, agent_id: str, days: int = 7):
        """
        Get action statistics for an agent over specified days
        
        Args:
            agent_id: UUID of the agent
            days: Number of days to analyze
        """
        self.log(f"Getting action statistics for agent {agent_id} (last {days} days)")
        
        try:
            session = self.db_config.get_session()
            
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            # Query actions within time period
            actions = session.query(Action).filter(
                Action.agent_id == uuid.UUID(agent_id),
                Action.created_at >= cutoff_time
            ).all()
            
            session.close()
            
            # Calculate statistics
            total_actions = len(actions)
            successful_actions = sum(1 for action in actions if action.success)
            failed_actions = total_actions - successful_actions
            
            # Group by action type
            action_types = {}
            execution_times = []
            
            for action in actions:
                action_type = action.action_type
                if action_type not in action_types:
                    action_types[action_type] = {"count": 0, "success": 0, "failure": 0}
                
                action_types[action_type]["count"] += 1
                if action.success:
                    action_types[action_type]["success"] += 1
                else:
                    action_types[action_type]["failure"] += 1
                
                if action.execution_time_ms:
                    execution_times.append(action.execution_time_ms)
            
            # Calculate average execution time
            avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
            
            return {
                "status": "statistics_retrieved",
                "agent_id": agent_id,
                "period_days": days,
                "total_actions": total_actions,
                "successful_actions": successful_actions,
                "failed_actions": failed_actions,
                "success_rate": successful_actions / total_actions if total_actions > 0 else 0,
                "avg_execution_time_ms": avg_execution_time,
                "action_types": action_types
            }
            
        except Exception as e:
            self.log(f"Error retrieving action statistics: {str(e)}")
            return {"status": "error", "message": str(e)}
    
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