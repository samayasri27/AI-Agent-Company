# agents/memory/learning_agent.py

import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.exc import SQLAlchemyError

from agents.agent_base import AgentBase
from database.models import DatabaseConfig, LearningPattern, Agent, Action
from config.memory_config import load_memory_config


class LearningAgent(AgentBase):
    """
    Specialized agent for pattern analysis and learning insights.
    Tracks task outcomes and provides basic recommendations for improvement.
    """
    
    def __init__(self, name="Learning Agent", department="memory", role="Learning Manager", memory=None):
        super().__init__(name, department, role, memory)
        
        # Load configuration and initialize database
        self.config = load_memory_config()
        self.db_config = DatabaseConfig(self.config.get_database_url())
        self.db_config.initialize()
        
        # Cache for frequently accessed patterns
        self._pattern_cache = {}
        self._cache_size = self.config.cache_size
        
        self.log("Learning Agent initialized with database connection")
    
    async def execute_task(self, task: str):
        """
        Execute learning-related tasks
        """
        self.log(f"Processing learning task: {task}")
        
        # Parse task and route to appropriate method
        if task.startswith("record_outcome:"):
            data = json.loads(task.split(":", 1)[1])
            return self.record_task_outcome(
                data["agent_id"], 
                data["task_type"], 
                data["success"], 
                data.get("metrics")
            )
        elif task.startswith("get_recommendations:"):
            data = json.loads(task.split(":", 1)[1])
            return self.get_recommendations(data["agent_id"], data["task_type"])
        elif task.startswith("analyze_patterns:"):
            data = json.loads(task.split(":", 1)[1])
            return self.analyze_patterns(data["agent_id"], data.get("time_period"))
        elif task.startswith("get_metrics:"):
            data = json.loads(task.split(":", 1)[1])
            return self.get_success_metrics(data["agent_id"], data.get("task_type"))
        else:
            return f"Learning Agent processed: {task}"
    
    def record_task_outcome(self, agent_id: str, task_type: str, success: bool, metrics: dict = None):
        """
        Record task completion results for learning analysis
        """
        self.log(f"Recording task outcome for agent {agent_id}: {task_type} ({'success' if success else 'failure'})")
        
        try:
            session = self.db_config.get_session()
            
            # Find or create learning pattern entry
            pattern = session.query(LearningPattern).filter(
                and_(
                    LearningPattern.agent_id == uuid.UUID(agent_id),
                    LearningPattern.task_type == task_type
                )
            ).first()
            
            if not pattern:
                # Create new pattern entry
                pattern = LearningPattern(
                    agent_id=uuid.UUID(agent_id),
                    task_type=task_type,
                    success_count=0,
                    failure_count=0,
                    avg_execution_time_ms=0
                )
                session.add(pattern)
            
            # Update counts
            if success:
                pattern.success_count += 1
            else:
                pattern.failure_count += 1
            
            # Update execution time if provided
            if metrics and "execution_time_ms" in metrics:
                execution_time = metrics["execution_time_ms"]
                total_tasks = pattern.success_count + pattern.failure_count
                
                if pattern.avg_execution_time_ms is None:
                    pattern.avg_execution_time_ms = execution_time
                else:
                    # Calculate running average
                    pattern.avg_execution_time_ms = int(
                        (pattern.avg_execution_time_ms * (total_tasks - 1) + execution_time) / total_tasks
                    )
            
            pattern.last_updated = datetime.utcnow()
            
            session.commit()
            session.close()
            
            # Clear cache for this agent/task combination
            cache_key = f"pattern_{agent_id}_{task_type}"
            if cache_key in self._pattern_cache:
                del self._pattern_cache[cache_key]
            
            self.log(f"Successfully recorded task outcome for {agent_id}")
            return {
                "status": "outcome_recorded", 
                "agent_id": agent_id, 
                "task_type": task_type, 
                "success": success,
                "total_success": pattern.success_count,
                "total_failure": pattern.failure_count
            }
            
        except Exception as e:
            self.log(f"Error recording task outcome: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_recommendations(self, agent_id: str, task_type: str):
        """
        Provide simple recommendations based on historical patterns
        """
        self.log(f"Getting recommendations for agent {agent_id} on task type: {task_type}")
        
        try:
            session = self.db_config.get_session()
            
            # Get pattern for this specific agent and task type
            pattern = session.query(LearningPattern).filter(
                and_(
                    LearningPattern.agent_id == uuid.UUID(agent_id),
                    LearningPattern.task_type == task_type
                )
            ).first()
            
            recommendations = []
            
            if pattern:
                total_tasks = pattern.success_count + pattern.failure_count
                success_rate = pattern.success_count / total_tasks if total_tasks > 0 else 0
                
                # Generate recommendations based on success rate
                if success_rate < 0.5 and total_tasks >= 3:
                    recommendations.append({
                        "type": "improvement_needed",
                        "message": f"Success rate for {task_type} is {success_rate:.1%}. Consider reviewing approach.",
                        "priority": "high"
                    })
                elif success_rate < 0.7 and total_tasks >= 5:
                    recommendations.append({
                        "type": "optimization_opportunity",
                        "message": f"Success rate for {task_type} is {success_rate:.1%}. Room for improvement.",
                        "priority": "medium"
                    })
                elif success_rate >= 0.9 and total_tasks >= 5:
                    recommendations.append({
                        "type": "best_practice",
                        "message": f"Excellent success rate for {task_type} ({success_rate:.1%}). Consider sharing approach.",
                        "priority": "low"
                    })
                
                # Execution time recommendations
                if pattern.avg_execution_time_ms and pattern.avg_execution_time_ms > 5000:  # 5 seconds
                    recommendations.append({
                        "type": "performance_optimization",
                        "message": f"Average execution time is {pattern.avg_execution_time_ms}ms. Consider optimization.",
                        "priority": "medium"
                    })
                
                # Get comparative data from other agents for the same task type
                other_patterns = session.query(LearningPattern).filter(
                    and_(
                        LearningPattern.task_type == task_type,
                        LearningPattern.agent_id != uuid.UUID(agent_id)
                    )
                ).all()
                
                if other_patterns:
                    # Calculate average success rate across other agents
                    other_success_rates = []
                    for other_pattern in other_patterns:
                        other_total = other_pattern.success_count + other_pattern.failure_count
                        if other_total > 0:
                            other_success_rates.append(other_pattern.success_count / other_total)
                    
                    if other_success_rates:
                        avg_other_success = sum(other_success_rates) / len(other_success_rates)
                        
                        if success_rate < avg_other_success - 0.2:  # 20% below average
                            recommendations.append({
                                "type": "benchmark_comparison",
                                "message": f"Success rate ({success_rate:.1%}) is below average for this task type ({avg_other_success:.1%}).",
                                "priority": "high"
                            })
                        elif success_rate > avg_other_success + 0.2:  # 20% above average
                            recommendations.append({
                                "type": "benchmark_comparison",
                                "message": f"Success rate ({success_rate:.1%}) is above average for this task type ({avg_other_success:.1%}).",
                                "priority": "low"
                            })
            else:
                recommendations.append({
                    "type": "insufficient_data",
                    "message": f"No historical data available for {task_type}. Continue executing tasks to build patterns.",
                    "priority": "info"
                })
            
            session.close()
            
            return {
                "status": "recommendations_generated", 
                "agent_id": agent_id, 
                "task_type": task_type,
                "recommendations": recommendations,
                "total_recommendations": len(recommendations)
            }
            
        except Exception as e:
            self.log(f"Error generating recommendations: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def analyze_patterns(self, agent_id: str, time_period: str = None):
        """
        Perform basic pattern analysis on agent behavior
        """
        self.log(f"Analyzing patterns for agent {agent_id}")
        
        try:
            session = self.db_config.get_session()
            
            # Build base query
            query = session.query(LearningPattern).filter(
                LearningPattern.agent_id == uuid.UUID(agent_id)
            )
            
            # Apply time period filter if specified
            if time_period:
                if time_period == "last_week":
                    cutoff_date = datetime.utcnow() - timedelta(weeks=1)
                elif time_period == "last_month":
                    cutoff_date = datetime.utcnow() - timedelta(days=30)
                elif time_period == "last_quarter":
                    cutoff_date = datetime.utcnow() - timedelta(days=90)
                else:
                    cutoff_date = None
                
                if cutoff_date:
                    query = query.filter(LearningPattern.last_updated >= cutoff_date)
            
            patterns = query.all()
            
            # Analyze patterns
            analysis = {
                "total_task_types": len(patterns),
                "task_types": [],
                "overall_success_rate": 0.0,
                "best_performing_tasks": [],
                "worst_performing_tasks": [],
                "trends": []
            }
            
            if patterns:
                total_success = 0
                total_tasks = 0
                task_performance = []
                
                for pattern in patterns:
                    task_total = pattern.success_count + pattern.failure_count
                    task_success_rate = pattern.success_count / task_total if task_total > 0 else 0
                    
                    task_info = {
                        "task_type": pattern.task_type,
                        "success_count": pattern.success_count,
                        "failure_count": pattern.failure_count,
                        "total_attempts": task_total,
                        "success_rate": task_success_rate,
                        "avg_execution_time_ms": pattern.avg_execution_time_ms,
                        "last_updated": pattern.last_updated.isoformat()
                    }
                    
                    analysis["task_types"].append(task_info)
                    task_performance.append((pattern.task_type, task_success_rate, task_total))
                    
                    total_success += pattern.success_count
                    total_tasks += task_total
                
                # Calculate overall success rate
                analysis["overall_success_rate"] = total_success / total_tasks if total_tasks > 0 else 0
                
                # Sort by success rate for best/worst performing
                task_performance.sort(key=lambda x: x[1], reverse=True)
                
                # Best performing tasks (top 3 with at least 3 attempts)
                analysis["best_performing_tasks"] = [
                    {"task_type": task, "success_rate": rate, "total_attempts": total}
                    for task, rate, total in task_performance[:3]
                    if total >= 3
                ]
                
                # Worst performing tasks (bottom 3 with at least 3 attempts)
                analysis["worst_performing_tasks"] = [
                    {"task_type": task, "success_rate": rate, "total_attempts": total}
                    for task, rate, total in task_performance[-3:]
                    if total >= 3 and rate < 0.8
                ]
                
                # Simple trend analysis
                if len(patterns) > 1:
                    recent_patterns = [p for p in patterns if p.last_updated >= datetime.utcnow() - timedelta(days=7)]
                    if recent_patterns:
                        recent_success = sum(p.success_count for p in recent_patterns)
                        recent_total = sum(p.success_count + p.failure_count for p in recent_patterns)
                        recent_rate = recent_success / recent_total if recent_total > 0 else 0
                        
                        if recent_rate > analysis["overall_success_rate"] + 0.1:
                            analysis["trends"].append("improving_performance")
                        elif recent_rate < analysis["overall_success_rate"] - 0.1:
                            analysis["trends"].append("declining_performance")
                        else:
                            analysis["trends"].append("stable_performance")
            
            session.close()
            
            return {
                "status": "patterns_analyzed", 
                "agent_id": agent_id, 
                "time_period": time_period or "all_time",
                "analysis": analysis
            }
            
        except Exception as e:
            self.log(f"Error analyzing patterns: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_success_metrics(self, agent_id: str, task_type: str = None):
        """
        Return success/failure statistics for tasks
        """
        self.log(f"Getting success metrics for agent {agent_id}")
        
        try:
            session = self.db_config.get_session()
            
            # Build query
            query = session.query(LearningPattern).filter(
                LearningPattern.agent_id == uuid.UUID(agent_id)
            )
            
            if task_type:
                query = query.filter(LearningPattern.task_type == task_type)
            
            patterns = query.all()
            
            # Calculate metrics
            metrics = {
                "total_success": 0,
                "total_failure": 0,
                "total_tasks": 0,
                "success_rate": 0.0,
                "task_types_count": len(patterns),
                "avg_execution_time_ms": None,
                "task_breakdown": []
            }
            
            if patterns:
                total_execution_times = []
                
                for pattern in patterns:
                    task_total = pattern.success_count + pattern.failure_count
                    
                    metrics["total_success"] += pattern.success_count
                    metrics["total_failure"] += pattern.failure_count
                    metrics["total_tasks"] += task_total
                    
                    if pattern.avg_execution_time_ms:
                        total_execution_times.extend([pattern.avg_execution_time_ms] * task_total)
                    
                    metrics["task_breakdown"].append({
                        "task_type": pattern.task_type,
                        "success_count": pattern.success_count,
                        "failure_count": pattern.failure_count,
                        "success_rate": pattern.success_count / task_total if task_total > 0 else 0,
                        "avg_execution_time_ms": pattern.avg_execution_time_ms
                    })
                
                # Calculate overall success rate
                if metrics["total_tasks"] > 0:
                    metrics["success_rate"] = metrics["total_success"] / metrics["total_tasks"]
                
                # Calculate average execution time
                if total_execution_times:
                    metrics["avg_execution_time_ms"] = int(sum(total_execution_times) / len(total_execution_times))
            
            session.close()
            
            return {
                "status": "metrics_retrieved", 
                "agent_id": agent_id, 
                "task_type": task_type,
                "metrics": metrics
            }
            
        except Exception as e:
            self.log(f"Error retrieving success metrics: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_learning_insights(self, agent_id: str, task_type: str = None):
        """
        Get comprehensive learning insights and recommendations for an agent
        """
        self.log(f"Getting learning insights for agent {agent_id}")
        
        try:
            # Get metrics and recommendations
            metrics_result = self.get_success_metrics(agent_id, task_type)
            
            if task_type:
                recommendations_result = self.get_recommendations(agent_id, task_type)
            else:
                # Get recommendations for all task types
                recommendations_result = {"recommendations": []}
                session = self.db_config.get_session()
                patterns = session.query(LearningPattern).filter(
                    LearningPattern.agent_id == uuid.UUID(agent_id)
                ).all()
                session.close()
                
                for pattern in patterns:
                    task_recs = self.get_recommendations(agent_id, pattern.task_type)
                    if task_recs.get("recommendations"):
                        recommendations_result["recommendations"].extend(task_recs["recommendations"])
            
            # Get pattern analysis
            patterns_result = self.analyze_patterns(agent_id)
            
            # Combine insights
            insights = {
                "agent_id": agent_id,
                "task_type": task_type,
                "metrics": metrics_result.get("metrics", {}),
                "recommendations": recommendations_result.get("recommendations", []),
                "patterns": patterns_result.get("analysis", {}),
                "summary": self._generate_insights_summary(
                    metrics_result.get("metrics", {}),
                    recommendations_result.get("recommendations", []),
                    patterns_result.get("analysis", {})
                )
            }
            
            return {"status": "insights_retrieved", "agent_id": agent_id, "insights": insights}
            
        except Exception as e:
            self.log(f"Error getting learning insights: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _generate_insights_summary(self, metrics: dict, recommendations: list, patterns: dict):
        """
        Generate a summary of key insights
        """
        summary = []
        
        # Performance summary
        if metrics.get("total_tasks", 0) > 0:
            success_rate = metrics.get("success_rate", 0)
            if success_rate >= 0.9:
                summary.append(f"Excellent performance with {success_rate:.1%} success rate")
            elif success_rate >= 0.7:
                summary.append(f"Good performance with {success_rate:.1%} success rate")
            elif success_rate >= 0.5:
                summary.append(f"Moderate performance with {success_rate:.1%} success rate")
            else:
                summary.append(f"Performance needs improvement with {success_rate:.1%} success rate")
        
        # Task diversity
        task_count = metrics.get("task_types_count", 0)
        if task_count > 5:
            summary.append(f"High task diversity with {task_count} different task types")
        elif task_count > 2:
            summary.append(f"Moderate task diversity with {task_count} task types")
        elif task_count > 0:
            summary.append(f"Limited task diversity with {task_count} task types")
        
        # Recommendations summary
        high_priority_recs = [r for r in recommendations if r.get("priority") == "high"]
        if high_priority_recs:
            summary.append(f"{len(high_priority_recs)} high-priority recommendations available")
        
        # Trends
        trends = patterns.get("trends", [])
        if "improving_performance" in trends:
            summary.append("Recent performance shows improvement")
        elif "declining_performance" in trends:
            summary.append("Recent performance shows decline")
        
        return summary