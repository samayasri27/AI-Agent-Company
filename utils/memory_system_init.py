# utils/memory_system_init.py

"""
Utility module for initializing the centralized memory system.
Provides functions to create and configure the memory manager for use by all agents.
"""

import os
import logging
from typing import Optional

from agents.memory.memory_manager_agent import MemoryManagerAgent
from config.memory_config import load_memory_config, check_environment_file, create_default_env_file, setup_logging


def initialize_memory_system(fallback_mode: bool = False) -> Optional[MemoryManagerAgent]:
    """
    Initialize the centralized memory system with proper configuration.
    
    Args:
        fallback_mode: If True, returns None when memory system cannot be initialized
                      instead of raising an exception
    
    Returns:
        MemoryManagerAgent instance or None if fallback_mode is True and initialization fails
    
    Raises:
        Exception: If memory system cannot be initialized and fallback_mode is False
    """
    try:
        # Check if environment file exists and has required variables
        if not check_environment_file():
            if fallback_mode:
                logging.warning("Memory system environment not configured, running without centralized memory")
                return None
            else:
                # Try to create default .env file
                try:
                    create_default_env_file()
                    logging.info("Created default .env file. Please configure Supabase credentials.")
                except Exception as e:
                    logging.error(f"Failed to create default .env file: {e}")
                
                raise ValueError(
                    "Memory system environment not configured. "
                    "Please set SUPABASE_URL, SUPABASE_ANON_KEY, and SUPABASE_SERVICE_KEY in .env file"
                )
        
        # Load and validate configuration
        config = load_memory_config()
        
        # Setup logging
        setup_logging(config)
        
        # Initialize memory manager
        memory_manager = MemoryManagerAgent()
        
        logging.info("Centralized memory system initialized successfully")
        return memory_manager
        
    except Exception as e:
        error_msg = f"Failed to initialize memory system: {e}"
        
        if fallback_mode:
            logging.warning(f"{error_msg}, running without centralized memory")
            return None
        else:
            logging.error(error_msg)
            raise


def get_memory_manager_for_agent(agent_name: str = None, fallback_mode: bool = True) -> Optional[MemoryManagerAgent]:
    """
    Get a memory manager instance for an agent.
    
    Args:
        agent_name: Name of the agent requesting memory manager (for logging)
        fallback_mode: If True, returns None when memory system is unavailable
    
    Returns:
        MemoryManagerAgent instance or None if unavailable and fallback_mode is True
    """
    try:
        memory_manager = initialize_memory_system(fallback_mode=fallback_mode)
        
        if memory_manager and agent_name:
            logging.info(f"Memory manager provided to agent: {agent_name}")
        
        return memory_manager
        
    except Exception as e:
        if fallback_mode:
            logging.warning(f"Memory manager unavailable for agent {agent_name}: {e}")
            return None
        else:
            raise


def check_memory_system_health() -> dict:
    """
    Check the health of the memory system components.
    
    Returns:
        Dictionary with health status information
    """
    try:
        memory_manager = initialize_memory_system(fallback_mode=True)
        
        if not memory_manager:
            return {
                "status": "unavailable",
                "message": "Memory system not configured or unavailable",
                "components": {
                    "memory_manager": False,
                    "knowledge_agent": False,
                    "history_agent": False,
                    "learning_agent": False
                }
            }
        
        # Get system health from memory manager
        health_status = memory_manager.get_system_health()
        
        return {
            "status": "healthy",
            "message": "Memory system is operational",
            "components": health_status["memory_manager"]["agent_health"],
            "routing_stats": health_status["memory_manager"]["routing_stats"]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error checking memory system health: {e}",
            "components": {
                "memory_manager": False,
                "knowledge_agent": False,
                "history_agent": False,
                "learning_agent": False
            }
        }


def create_memory_enabled_agent_kwargs(base_kwargs: dict, agent_name: str = None) -> dict:
    """
    Create agent initialization kwargs with memory manager if available.
    
    Args:
        base_kwargs: Base keyword arguments for agent initialization
        agent_name: Name of the agent being created (for logging)
    
    Returns:
        Updated kwargs with memory_manager parameter if available
    """
    # Get memory manager
    memory_manager = get_memory_manager_for_agent(agent_name, fallback_mode=True)
    
    # Create updated kwargs
    updated_kwargs = base_kwargs.copy()
    
    if memory_manager:
        # Use new memory system
        updated_kwargs['memory_manager'] = memory_manager
        # Remove old memory parameter if present
        updated_kwargs.pop('memory', None)
    else:
        # Keep existing memory parameter or set to None
        if 'memory' not in updated_kwargs:
            updated_kwargs['memory'] = None
    
    return updated_kwargs


def migrate_agent_to_memory_system(agent_class, *args, **kwargs):
    """
    Helper function to create an agent with centralized memory system.
    
    Args:
        agent_class: The agent class to instantiate
        *args: Positional arguments for agent initialization
        **kwargs: Keyword arguments for agent initialization
    
    Returns:
        Agent instance with memory manager if available, otherwise with legacy memory
    """
    # Extract agent name for logging
    agent_name = kwargs.get('name', agent_class.__name__)
    
    # Update kwargs with memory manager
    updated_kwargs = create_memory_enabled_agent_kwargs(kwargs, agent_name)
    
    # Create and return agent instance
    return agent_class(*args, **updated_kwargs)