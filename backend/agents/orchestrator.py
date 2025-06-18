from typing import Dict, Any, List, Optional
from backend.agents.task_agent import TaskAgent
from backend.agents.schedule_agent import ScheduleAgent
from backend.agents.communication_agent import CommunicationAgent
from backend.database import AgentLog, SessionLocal
import re

class AgentOrchestrator:
    def __init__(self):
        self.task_agent = TaskAgent()
        self.schedule_agent = ScheduleAgent()
        self.communication_agent = CommunicationAgent()
        self.agents = {
            "task": self.task_agent,
            "schedule": self.schedule_agent,
            "communication": self.communication_agent
        }
    
    async def classify_query(self, query: str) -> List[str]:
        """Determine which agents should handle the query."""
        # Use the task agent's LLM to classify the query
        classification_prompt = f"""Analyze the following query and determine which agents should handle it.
        Available agents: task, schedule, communication
        Return a comma-separated list of relevant agents.
        
        Query: {query}
        
        Example responses:
        - "task,schedule" (for queries about scheduling tasks)
        - "communication" (for message-related queries)
        - "task,schedule,communication" (for complex queries requiring all agents)
        """
        
        response = await self.task_agent.process(classification_prompt)
        print("[DEBUG] LLM classification response:", response)  # Debug print
        if not response["success"]:
            return ["task"]  # Default to task agent if classification fails
        
        # Extract agent list using regex: look for a line that ends with a comma-separated list of agents
        agent_list_match = re.search(r'([a-z]+(?:,\s*[a-z]+)*)(?:\s*$|\n)', response["response"], re.IGNORECASE)
        if agent_list_match:
            agent_list = [agent.strip().lower() for agent in agent_list_match.group(1).split(",")]
        else:
            agent_list = []
        return [agent for agent in agent_list if agent in self.agents]
    
    async def coordinate_agents(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Coordinate multiple agents to handle a query."""
        # Determine which agents to involve
        relevant_agents = await self.classify_query(query)
        print("[DEBUG] Relevant agents:", relevant_agents)  # Debug print
        
        if not relevant_agents:
            return {
                "success": True,
                "response": "No suitable agents found for the query",
                "agent_responses": {}
            }
        
        # Get responses from each relevant agent
        agent_responses = {}
        for agent_name in relevant_agents:
            agent = self.agents[agent_name]
            response = await agent.handle_specific_query(query, context)
            agent_responses[agent_name] = response
        print("[DEBUG] Agent responses:", agent_responses)  # Debug print
        
        # Merge responses
        merged_response = await self.merge_responses(agent_responses)
        print("[DEBUG] Merged response:", merged_response)  # Debug print
        
        # Log the coordination
        self._log_coordination(query, relevant_agents, merged_response)
        
        return merged_response
    
    async def merge_responses(self, agent_responses: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Merge responses from multiple agents into a unified response."""
        # If only one agent responded, return its response with agent_responses included
        if len(agent_responses) == 1:
            single_response = list(agent_responses.values())[0]
            return {
                "success": True,
                "response": single_response["response"],
                "agent_responses": agent_responses
            }
        
        # Combine responses for multiple agents
        combined_content = "\n\n".join([
            f"{agent_name.capitalize()} Agent:\n{response['response']}"
            for agent_name, response in agent_responses.items()
            if response["success"]
        ])
        
        # Use the task agent's LLM to merge the responses
        merge_prompt = f"""Please merge the following agent responses into a coherent, unified response:
        
        {combined_content}
        
        Provide a clear, concise summary that combines all relevant information."""
        
        merged = await self.task_agent.process(merge_prompt)
        
        return {
            "success": True,
            "response": merged["response"],
            "agent_responses": agent_responses
        }
    
    def _log_coordination(self, query: str, agents: List[str], response: Dict[str, Any]):
        """Log agent coordination details."""
        db = SessionLocal()
        try:
            log = AgentLog(
                agent_type="orchestrator",
                query=query,
                response=str(response),
                success=response["success"],
                error_message=response.get("error")
            )
            db.add(log)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error logging coordination: {str(e)}")
        finally:
            db.close()
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get the current status of all agents."""
        return {
            "success": True,
            "agents": {
                name: {
                    "status": "active",
                    "type": agent.agent_type
                }
                for name, agent in self.agents.items()
            }
        } 