"""
Skill Dispatcher Service
"""
from typing import Dict, Any
from src.agents import TaskAgent, ReminderAgent
from src.utils.logging import get_logger

logger = get_logger(__name__)


class SkillDispatcher:
    """Dispatch requests to appropriate skill agents and execute operations"""
    
    def __init__(self):
        self.task_agent = TaskAgent()
        self.reminder_agent = ReminderAgent()
    
    async def dispatch(
        self,
        agent_name: str,
        intent_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Dispatch request to appropriate agent and execute
        
        Args:
            agent_name: Name of the agent to use
            intent_data: Extracted intent and data
            context: Additional context (user_id, db_session, etc.)
        
        Returns:
            Agent execution result
        """
        logger.info(
            "dispatching_skill",
            agent=agent_name,
            intent=intent_data.get("intent"),
        )
        
        # Get agent
        agent = self._get_agent(agent_name)
        if not agent:
            logger.warning("agent_not_found", agent=agent_name)
            return {
                "success": False,
                "message": f"Agent '{agent_name}' not found",
            }
        
        # Execute using agent
        try:
            result = agent.execute(intent_data, context)
            logger.info(
                "skill_executed",
                agent=agent_name,
                success=True,
            )
            return result
        except Exception as e:
            logger.error(
                "skill_execution_failed",
                agent=agent_name,
                error=str(e),
            )
            return {
                "success": False,
                "message": f"Execution failed: {str(e)}",
            }
    
    def _get_agent(self, agent_name: str):
        """Get agent by name"""
        agents = {
            "task": self.task_agent,
            "reminder": self.reminder_agent,
        }
        return agents.get(agent_name)
