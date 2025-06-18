from typing import Dict, Any, Optional, List
from datetime import datetime
from backend.agents.base_agent import BaseAgent
from backend.database import Message, SessionLocal

class CommunicationAgent(BaseAgent):
    def __init__(self):
        super().__init__("communication_agent")
    
    def _get_system_prompt(self) -> str:
        return """You are a Communication Management Agent responsible for handling messages and communications.
        Your capabilities include:
        1. Processing and summarizing messages
        2. Drafting responses
        3. Prioritizing communications
        4. Managing message threads
        
        Always maintain a professional tone and consider context when processing communications."""
    
    async def handle_specific_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle communication-specific queries."""
        base_response = await self.process(query, context)
        
        if not base_response["success"]:
            return base_response
        
        try:
            # Here you would implement specific communication logic
            return base_response
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_type": self.agent_type
            }
    
    async def create_message(self, content: str, priority: int, user_id: int) -> Dict[str, Any]:
        """Create a new message."""
        db = SessionLocal()
        try:
            message = Message(
                content=content,
                priority=priority,
                status="new",
                user_id=user_id
            )
            db.add(message)
            db.commit()
            db.refresh(message)
            
            return {
                "success": True,
                "message_id": message.id,
                "message": "Message created successfully"
            }
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close()
    
    async def get_messages(self, user_id: int, priority: Optional[int] = None, 
                          status: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve messages, optionally filtered by priority and status."""
        db = SessionLocal()
        try:
            query = db.query(Message).filter(Message.user_id == user_id)
            
            if priority is not None:
                query = query.filter(Message.priority == priority)
            if status:
                query = query.filter(Message.status == status)
            
            messages = query.order_by(Message.created_at.desc()).all()
            
            return {
                "success": True,
                "messages": [
                    {
                        "id": message.id,
                        "content": message.content,
                        "priority": message.priority,
                        "status": message.status,
                        "created_at": message.created_at.isoformat()
                    }
                    for message in messages
                ]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close()
    
    async def update_message_status(self, message_id: int, new_status: str) -> Dict[str, Any]:
        """Update the status of a message."""
        db = SessionLocal()
        try:
            message = db.query(Message).filter(Message.id == message_id).first()
            if not message:
                return {
                    "success": False,
                    "error": f"Message with ID {message_id} not found"
                }
            
            message.status = new_status
            db.commit()
            
            return {
                "success": True,
                "message": f"Message status updated to {new_status}"
            }
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close()
    
    async def summarize_messages(self, message_ids: List[int]) -> Dict[str, Any]:
        """Generate a summary of multiple messages."""
        db = SessionLocal()
        try:
            messages = db.query(Message).filter(Message.id.in_(message_ids)).all()
            
            if not messages:
                return {
                    "success": False,
                    "error": "No messages found"
                }
            
            # Combine message contents for summarization
            combined_content = "\n\n".join([
                f"Message {msg.id} (Priority: {msg.priority}):\n{msg.content}"
                for msg in messages
            ])
            
            # Use the LLM to generate a summary
            summary_response = await self.process(
                f"Please provide a concise summary of the following messages:\n\n{combined_content}"
            )
            
            return {
                "success": True,
                "summary": summary_response["response"],
                "message_count": len(messages)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close() 