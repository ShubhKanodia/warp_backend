from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from backend.agents.base_agent import BaseAgent
from backend.database import Event, SessionLocal

class ScheduleAgent(BaseAgent):
    def __init__(self):
        super().__init__("schedule_agent")
    
    def _get_system_prompt(self) -> str:
        return """You are a Schedule Management Agent responsible for handling calendar events and time management.
        Your capabilities include:
        1. Scheduling and managing events
        2. Finding available time slots
        3. Coordinating meeting times
        4. Managing calendar conflicts
        
        Always consider time zones, existing commitments, and user preferences when making scheduling decisions."""
    
    async def handle_specific_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle schedule-specific queries."""
        base_response = await self.process(query, context)
        
        if not base_response["success"]:
            return base_response
        
        try:
            # Here you would implement specific scheduling logic
            return base_response
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_type": self.agent_type
            }
    
    async def create_event(self, title: str, start_time: datetime, end_time: datetime, 
                          description: str, user_id: int) -> Dict[str, Any]:
        """Create a new calendar event."""
        db = SessionLocal()
        try:
            # Check for scheduling conflicts
            conflicts = db.query(Event).filter(
                Event.user_id == user_id,
                Event.start_time < end_time,
                Event.end_time > start_time
            ).all()
            
            if conflicts:
                return {
                    "success": False,
                    "error": "Scheduling conflict detected",
                    "conflicts": [
                        {
                            "title": event.title,
                            "start_time": event.start_time.isoformat(),
                            "end_time": event.end_time.isoformat()
                        }
                        for event in conflicts
                    ]
                }
            
            event = Event(
                title=title,
                start_time=start_time,
                end_time=end_time,
                description=description,
                user_id=user_id
            )
            db.add(event)
            db.commit()
            db.refresh(event)
            
            return {
                "success": True,
                "event_id": event.id,
                "message": f"Event '{title}' scheduled successfully"
            }
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close()
    
    async def get_events(self, user_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Retrieve events within a date range."""
        db = SessionLocal()
        try:
            events = db.query(Event).filter(
                Event.user_id == user_id,
                Event.start_time >= start_date,
                Event.end_time <= end_date
            ).all()
            
            return {
                "success": True,
                "events": [
                    {
                        "id": event.id,
                        "title": event.title,
                        "start_time": event.start_time.isoformat(),
                        "end_time": event.end_time.isoformat(),
                        "description": event.description
                    }
                    for event in events
                ]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close()
    
    async def find_available_slots(self, user_id: int, duration_minutes: int, 
                                 start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Find available time slots for scheduling."""
        db = SessionLocal()
        try:
            # Get all events in the date range
            events = db.query(Event).filter(
                Event.user_id == user_id,
                Event.start_time >= start_date,
                Event.end_time <= end_date
            ).order_by(Event.start_time).all()
            
            # Find gaps between events
            available_slots = []
            current_time = start_date
            
            for event in events:
                if event.start_time - current_time >= timedelta(minutes=duration_minutes):
                    available_slots.append({
                        "start_time": current_time.isoformat(),
                        "end_time": event.start_time.isoformat()
                    })
                current_time = event.end_time
            
            # Check for slot after last event
            if end_date - current_time >= timedelta(minutes=duration_minutes):
                available_slots.append({
                    "start_time": current_time.isoformat(),
                    "end_time": end_date.isoformat()
                })
            
            return {
                "success": True,
                "available_slots": available_slots
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close() 