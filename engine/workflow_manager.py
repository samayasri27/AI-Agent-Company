# engine/workflow_manager.py

import asyncio
from enum import Enum
from typing import Dict, List, Any
from dataclasses import dataclass

class ExecutionPhase(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"

@dataclass
class Task:
    id: str
    description: str
    department: str
    dependencies: List[str] = None
    phase: ExecutionPhase = ExecutionPhase.PARALLEL
    priority: int = 1
    status: str = "pending"
    result: Any = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class WorkflowManager:
    """Manages task execution flow with sequential and parallel phases"""
    
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.tasks: Dict[str, Task] = {}
        self.execution_order = []
        self.completed_tasks = set()
        
    def add_task(self, task: Task):
        """Add a task to the workflow"""
        self.tasks[task.id] = task
        print(f"[WorkflowManager] ✅ Added task: {task.id} ({task.phase.value})")
        
    def plan_execution(self):
        """Plan the execution order based on dependencies and phases"""
        # Separate sequential and parallel tasks
        sequential_tasks = [t for t in self.tasks.values() if t.phase == ExecutionPhase.SEQUENTIAL]
        parallel_tasks = [t for t in self.tasks.values() if t.phase == ExecutionPhase.PARALLEL]
        
        # Sort sequential tasks by priority and dependencies
        sequential_tasks.sort(key=lambda x: (x.priority, len(x.dependencies)))
        
        # Build execution plan
        self.execution_order = []
        
        # Phase 1: Sequential execution
        if sequential_tasks:
            self.execution_order.append({
                "phase": ExecutionPhase.SEQUENTIAL,
                "tasks": sequential_tasks
            })
        
        # Phase 2: Parallel execution
        if parallel_tasks:
            self.execution_order.append({
                "phase": ExecutionPhase.PARALLEL,
                "tasks": parallel_tasks
            })
            
        print(f"[WorkflowManager] 📋 Planned execution: {len(sequential_tasks)} sequential, {len(parallel_tasks)} parallel")
        
    async def execute_workflow(self):
        """Execute the planned workflow"""
        print(f"[WorkflowManager] 🚀 Starting workflow execution...")
        
        for phase_info in self.execution_order:
            phase = phase_info["phase"]
            tasks = phase_info["tasks"]
            
            print(f"\n[WorkflowManager] 📍 Executing {phase.value.upper()} phase with {len(tasks)} tasks")
            
            if phase == ExecutionPhase.SEQUENTIAL:
                await self._execute_sequential(tasks)
            else:
                await self._execute_parallel(tasks)
                
        print(f"[WorkflowManager] ✅ Workflow completed. {len(self.completed_tasks)} tasks finished.")
        
    async def _execute_sequential(self, tasks: List[Task]):
        """Execute tasks sequentially"""
        for task in tasks:
            if self._can_execute(task):
                print(f"[WorkflowManager] ⏳ Executing sequential task: {task.id}")
                result = await self.scheduler.assign_task(task.department, task.description)
                task.result = result
                task.status = "completed"
                self.completed_tasks.add(task.id)
                print(f"[WorkflowManager] ✅ Completed: {task.id}")
                
                # Add delay between sequential tasks for better coordination
                await asyncio.sleep(1)
            else:
                print(f"[WorkflowManager] ⚠️ Skipping task {task.id} - dependencies not met")
                
    async def _execute_parallel(self, tasks: List[Task]):
        """Execute tasks in parallel"""
        executable_tasks = [task for task in tasks if self._can_execute(task)]
        
        if not executable_tasks:
            print("[WorkflowManager] ⚠️ No executable parallel tasks found")
            return
            
        print(f"[WorkflowManager] 🔄 Running {len(executable_tasks)} tasks in parallel")
        
        # Create coroutines for parallel execution
        coroutines = []
        for task in executable_tasks:
            coroutines.append(self._execute_single_task(task))
            
        # Execute all tasks concurrently
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        # Process results
        for task, result in zip(executable_tasks, results):
            if isinstance(result, Exception):
                print(f"[WorkflowManager] ❌ Task {task.id} failed: {result}")
                task.status = "failed"
            else:
                task.result = result
                task.status = "completed"
                self.completed_tasks.add(task.id)
                print(f"[WorkflowManager] ✅ Parallel task completed: {task.id}")
                
    async def _execute_single_task(self, task: Task):
        """Execute a single task"""
        print(f"[WorkflowManager] ⏳ Executing parallel task: {task.id}")
        return await self.scheduler.assign_task(task.department, task.description)
        
    def _can_execute(self, task: Task) -> bool:
        """Check if a task can be executed based on dependencies"""
        if not task.dependencies:
            return True
            
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return False
                
        return True
        
    def get_task_status(self, task_id: str) -> str:
        """Get the status of a specific task"""
        if task_id in self.tasks:
            return self.tasks[task_id].status
        return "not_found"
        
    def get_completed_tasks(self) -> List[Task]:
        """Get all completed tasks"""
        return [task for task in self.tasks.values() if task.status == "completed"]