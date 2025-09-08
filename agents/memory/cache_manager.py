"""
Cache manager for the centralized memory system.
Provides in-memory caching with TTL, LRU eviction, and cache invalidation strategies.
"""

import time
import threading
from typing import Any, Dict, Optional, Set, Tuple
from collections import OrderedDict
from datetime import datetime, timedelta
import hashlib
import json


class CacheEntry:
    """Represents a single cache entry with metadata."""
    
    def __init__(self, value: Any, ttl_seconds: Optional[int] = None):
        self.value = value
        self.created_at = time.time()
        self.last_accessed = self.created_at
        self.access_count = 1
        self.ttl_seconds = ttl_seconds
        self.expires_at = self.created_at + ttl_seconds if ttl_seconds else None
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
    
    def touch(self):
        """Update last accessed time and increment access count."""
        self.last_accessed = time.time()
        self.access_count += 1


class LRUCache:
    """Thread-safe LRU cache with TTL support."""
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[int] = None):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expired': 0,
            'invalidations': 0
        }
    
    def _generate_key(self, key_parts: Tuple) -> str:
        """Generate a cache key from multiple parts."""
        key_str = json.dumps(key_parts, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            if key not in self._cache:
                self._stats['misses'] += 1
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if entry.is_expired():
                del self._cache[key]
                self._stats['expired'] += 1
                self._stats['misses'] += 1
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            entry.touch()
            self._stats['hits'] += 1
            return entry.value
    
    def put(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Put value in cache."""
        with self._lock:
            ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
            entry = CacheEntry(value, ttl)
            
            if key in self._cache:
                # Update existing entry
                self._cache[key] = entry
                self._cache.move_to_end(key)
            else:
                # Add new entry
                self._cache[key] = entry
                
                # Evict if over capacity
                while len(self._cache) > self.max_size:
                    oldest_key = next(iter(self._cache))
                    del self._cache[oldest_key]
                    self._stats['evictions'] += 1
    
    def invalidate(self, key: str) -> bool:
        """Remove specific key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats['invalidations'] += 1
                return True
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Remove all keys matching a pattern."""
        with self._lock:
            keys_to_remove = [key for key in self._cache.keys() if pattern in key]
            for key in keys_to_remove:
                del self._cache[key]
                self._stats['invalidations'] += 1
            return len(keys_to_remove)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            cleared_count = len(self._cache)
            self._cache.clear()
            self._stats['invalidations'] += cleared_count
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count removed."""
        with self._lock:
            current_time = time.time()
            expired_keys = []
            
            for key, entry in self._cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
                self._stats['expired'] += 1
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = self._stats['hits'] / total_requests if total_requests > 0 else 0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hit_rate': hit_rate,
                'stats': self._stats.copy(),
                'memory_usage_estimate': len(self._cache) * 1024  # Rough estimate
            }


class CacheManager:
    """Manages multiple cache instances for different data types."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.caches: Dict[str, LRUCache] = {}
        self._lock = threading.RLock()
        
        # Initialize default caches
        self._initialize_caches()
        
        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self._cleanup_running = True
        self._cleanup_thread.start()
    
    def _initialize_caches(self):
        """Initialize cache instances for different data types."""
        cache_configs = {
            'knowledge': {
                'max_size': self.config.get('knowledge_cache_size', 500),
                'default_ttl': self.config.get('knowledge_cache_ttl', 3600)  # 1 hour
            },
            'history': {
                'max_size': self.config.get('history_cache_size', 300),
                'default_ttl': self.config.get('history_cache_ttl', 1800)  # 30 minutes
            },
            'learning': {
                'max_size': self.config.get('learning_cache_size', 200),
                'default_ttl': self.config.get('learning_cache_ttl', 7200)  # 2 hours
            },
            'similarity': {
                'max_size': self.config.get('similarity_cache_size', 100),
                'default_ttl': self.config.get('similarity_cache_ttl', 900)  # 15 minutes
            }
        }
        
        for cache_name, cache_config in cache_configs.items():
            self.caches[cache_name] = LRUCache(
                max_size=cache_config['max_size'],
                default_ttl=cache_config['default_ttl']
            )
    
    def get_cache(self, cache_name: str) -> LRUCache:
        """Get a specific cache instance."""
        with self._lock:
            if cache_name not in self.caches:
                # Create cache on demand
                self.caches[cache_name] = LRUCache(
                    max_size=self.config.get(f'{cache_name}_cache_size', 100),
                    default_ttl=self.config.get(f'{cache_name}_cache_ttl', 3600)
                )
            return self.caches[cache_name]
    
    def invalidate_agent_data(self, agent_id: str) -> int:
        """Invalidate all cached data for a specific agent."""
        total_invalidated = 0
        with self._lock:
            for cache in self.caches.values():
                total_invalidated += cache.invalidate_pattern(f"agent:{agent_id}")
        return total_invalidated
    
    def invalidate_data_type(self, data_type: str) -> int:
        """Invalidate all cached data of a specific type."""
        total_invalidated = 0
        with self._lock:
            for cache in self.caches.values():
                total_invalidated += cache.invalidate_pattern(f"type:{data_type}")
        return total_invalidated
    
    def clear_all_caches(self) -> None:
        """Clear all cache instances."""
        with self._lock:
            for cache in self.caches.values():
                cache.clear()
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all caches."""
        with self._lock:
            stats = {}
            total_size = 0
            total_hit_rate = 0
            cache_count = len(self.caches)
            
            for cache_name, cache in self.caches.items():
                cache_stats = cache.get_stats()
                stats[cache_name] = cache_stats
                total_size += cache_stats['size']
                total_hit_rate += cache_stats['hit_rate']
            
            avg_hit_rate = total_hit_rate / cache_count if cache_count > 0 else 0
            
            return {
                'caches': stats,
                'summary': {
                    'total_entries': total_size,
                    'cache_count': cache_count,
                    'average_hit_rate': avg_hit_rate
                }
            }
    
    def _cleanup_worker(self):
        """Background worker to clean up expired entries."""
        while self._cleanup_running:
            try:
                with self._lock:
                    for cache in self.caches.values():
                        cache.cleanup_expired()
                
                # Sleep for 5 minutes between cleanups
                time.sleep(300)
            except Exception as e:
                # Log error but continue running
                print(f"Cache cleanup error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def shutdown(self):
        """Shutdown the cache manager."""
        self._cleanup_running = False
        if self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5)


# Cache key generators
class CacheKeyGenerator:
    """Utility class for generating consistent cache keys."""
    
    @staticmethod
    def knowledge_key(agent_id: str, content_type: str, content_hash: str) -> str:
        """Generate cache key for knowledge entries."""
        return f"knowledge:agent:{agent_id}:type:{content_type}:hash:{content_hash}"
    
    @staticmethod
    def history_key(agent_id: str, history_type: str, filters_hash: str) -> str:
        """Generate cache key for history queries."""
        return f"history:agent:{agent_id}:type:{history_type}:filters:{filters_hash}"
    
    @staticmethod
    def learning_key(agent_id: str, task_type: str) -> str:
        """Generate cache key for learning insights."""
        return f"learning:agent:{agent_id}:task:{task_type}"
    
    @staticmethod
    def similarity_key(query_hash: str, top_k: int, filters_hash: str) -> str:
        """Generate cache key for similarity searches."""
        return f"similarity:query:{query_hash}:k:{top_k}:filters:{filters_hash}"
    
    @staticmethod
    def hash_content(content: Any) -> str:
        """Generate hash for content to use in cache keys."""
        if isinstance(content, str):
            return hashlib.md5(content.encode()).hexdigest()[:16]
        else:
            content_str = json.dumps(content, sort_keys=True, default=str)
            return hashlib.md5(content_str.encode()).hexdigest()[:16]