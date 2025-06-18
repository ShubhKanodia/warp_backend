from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
from .agents.orchestrator import AgentOrchestrator
from .database import init_db, get_db, SessionLocal
from sqlalchemy.orm import Session

# Initialize FastAPI app
app = FastAPI(title="AgentSwarm Backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = AgentOrchestrator()

# Initialize database
init_db()

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class TaskRequest(BaseModel):
    title: str
    description: str
    deadline: datetime
    priority: int
    user_id: int

class ScheduleRequest(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    description: str
    user_id: int

class MessageRequest(BaseModel):
    content: str
    priority: int
    user_id: int

# API endpoints
@app.post("/chat")
async def chat(request: ChatRequest):
    """Main chat endpoint that coordinates all agents."""
    try:
        response = await orchestrator.coordinate_agents(request.message, request.context)
        if not response["success"]:
            raise HTTPException(status_code=500, detail=response["error"])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/status")
async def get_agent_status():
    """Get the current status of all agents."""
    try:
        return await orchestrator.get_agent_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Test endpoints
@app.post("/test/task")
async def test_task(request: ChatRequest):
    """Test the task agent directly."""
    try:
        response = await orchestrator.task_agent.handle_specific_query(request.message, request.context)
        if not response["success"]:
            raise HTTPException(status_code=500, detail=response["error"])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test/schedule")
async def test_schedule(request: ChatRequest):
    """Test the schedule agent directly."""
    try:
        response = await orchestrator.schedule_agent.handle_specific_query(request.message, request.context)
        if not response["success"]:
            raise HTTPException(status_code=500, detail=response["error"])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test/communication")
async def test_communication(request: ChatRequest):
    """Test the communication agent directly."""
    try:
        response = await orchestrator.communication_agent.handle_specific_query(request.message, request.context)
        if not response["success"]:
            raise HTTPException(status_code=500, detail=response["error"])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Database operation endpoints
@app.post("/tasks")
async def create_task(request: TaskRequest, db: Session = Depends(get_db)):
    """Create a new task."""
    try:
        response = await orchestrator.task_agent.create_task(
            request.title,
            request.description,
            request.deadline,
            request.priority,
            request.user_id
        )
        if not response["success"]:
            raise HTTPException(status_code=500, detail=response["error"])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/events")
async def create_event(request: ScheduleRequest, db: Session = Depends(get_db)):
    """Create a new calendar event."""
    try:
        response = await orchestrator.schedule_agent.create_event(
            request.title,
            request.start_time,
            request.end_time,
            request.description,
            request.user_id
        )
        if not response["success"]:
            raise HTTPException(status_code=500, detail=response["error"])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/messages")
async def create_message(request: MessageRequest, db: Session = Depends(get_db)):
    """Create a new message."""
    try:
        response = await orchestrator.communication_agent.create_message(
            request.content,
            request.priority,
            request.user_id
        )
        if not response["success"]:
            raise HTTPException(status_code=500, detail=response["error"])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 