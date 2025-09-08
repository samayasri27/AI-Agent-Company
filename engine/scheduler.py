import asyncio

class Scheduler:
    def __init__(self):
        self.agent_tasks = {}
        self.queues = {}
        self.agents = {}

    def register_agent(self, name, agent):
        """Register an agent with the scheduler"""
        queue = asyncio.Queue()
        self.queues[name] = queue
        self.agents[name] = agent
        self.agent_tasks[name] = asyncio.create_task(self._agent_runner(agent, queue))
        print(f"[Scheduler] ✅ Registered agent: {name}")

    async def _agent_runner(self, agent, queue):
        """Run agent tasks from queue"""
        while True:
            task_data = await queue.get()
            if task_data is None:
                break
            task, result_future = task_data
            try:
                result = await agent.execute_task(task)
                if result_future:
                    result_future.set_result(result)
            except Exception as e:
                print(f"[Scheduler] ❌ Error in agent {agent.name}: {e}")
                if result_future:
                    result_future.set_exception(e)

    async def assign_task(self, agent_name, task):
        """Assign task to specific agent"""
        if agent_name not in self.queues:
            raise ValueError(f"Agent '{agent_name}' not registered with scheduler")
            
        print(f"[Scheduler] 📋 Assigning task to {agent_name}: {task}")
        result_future = asyncio.get_event_loop().create_future()
        await self.queues[agent_name].put((task, result_future))
        return await result_future  # Wait for the agent to complete and return result

    def get_registered_agents(self):
        """Get list of registered agents"""
        return list(self.agents.keys())

    def get_agent(self, agent_name):
        """Get agent instance by name"""
        return self.agents.get(agent_name)

    async def shutdown(self):
        """Shutdown all agent tasks"""
        print("[Scheduler] 🔄 Shutting down all agents...")
        for name in self.queues:
            await self.queues[name].put(None)
        
        # Wait for all tasks to complete
        if self.agent_tasks:
            await asyncio.gather(*self.agent_tasks.values(), return_exceptions=True)
        
        print("[Scheduler] ✅ All agents shut down successfully")