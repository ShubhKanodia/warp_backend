from typing import Dict, Any, Optional
from datetime import datetime
from backend.agents.base_agent import BaseAgent
from backend.database import Task, SessionLocal

class TaskAgent(BaseAgent):
    def __init__(self):
        super().__init__("task_agent")
    
    def _get_system_prompt(self) -> str:
        return """You are a Task Management Agent responsible for handling tasks, deadlines, and priorities.
        Your capabilities include:
        1. Creating and managing tasks
        2. Setting and updating priorities
        3. Tracking deadlines
        4. Providing task status updates
        
        Always respond in a clear, actionable format and consider task dependencies and deadlines."""
    
    async def handle_specific_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle task-specific queries."""
        # First, get the general response from the LLM
        base_response = await self.process(query, context)
        
        if not base_response["success"]:
            return base_response
        
        # Extract task-related information from the response
        try:
            # Here you would implement specific task management logic
            # For now, we'll just return the LLM response
            return base_response
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_type": self.agent_type
            }
    
    async def create_task(self, title: str, description: str, deadline: datetime, priority: int, user_id: int) -> Dict[str, Any]:
        """Create a new task in the database."""
        db = SessionLocal()
        try:
            task = Task(
                title=title,
                description=description,
                deadline=deadline,
                priority=priority,
                status="pending",
                user_id=user_id
            )
            db.add(task)
            db.commit()
            db.refresh(task)
            
            return {
                "success": True,
                "task_id": task.id,
                "message": f"Task '{title}' created successfully"
            }
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close()
    
    async def get_tasks(self, user_id: int, status: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve tasks for a user, optionally filtered by status."""
        db = SessionLocal()
        try:
            query = db.query(Task).filter(Task.user_id == user_id)
            if status:
                query = query.filter(Task.status == status)
            
            tasks = query.all()
            return {
                "success": True,
                "tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "deadline": task.deadline.isoformat(),
                        "priority": task.priority,
                        "status": task.status
                    }
                    for task in tasks
                ]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close()
    
    async def update_task_status(self, task_id: int, new_status: str) -> Dict[str, Any]:
        """Update the status of a task."""
        db = SessionLocal()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return {
                    "success": False,
                    "error": f"Task with ID {task_id} not found"
                }
            
            task.status = new_status
            db.commit()
            
            return {
                "success": True,
                "message": f"Task status updated to {new_status}"
            }
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close() 