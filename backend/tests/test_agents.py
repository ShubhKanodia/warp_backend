import pytest
from datetime import datetime, timedelta
from ..agents.orchestrator import AgentOrchestrator
from ..agents.task_agent import TaskAgent
from ..agents.schedule_agent import ScheduleAgent
from ..agents.communication_agent import CommunicationAgent
from ..database import init_db, SessionLocal, User, Task, Event, Message

# Initialize test database
@pytest.fixture(scope="session")
def db():
    init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create test user
@pytest.fixture
def test_user(db):
    user = User(email="test@example.com")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Test TaskAgent
@pytest.mark.asyncio
async def test_task_agent():
    agent = TaskAgent()
    
    # Test task creation
    response = await agent.create_task(
        title="Test Task",
        description="This is a test task",
        deadline=datetime.utcnow() + timedelta(days=1),
        priority=1,
        user_id=1
    )
    assert response["success"] is True
    assert "task_id" in response
    
    # Test task query
    response = await agent.handle_specific_query(
        "I need to complete the project proposal by Friday"
    )
    assert response["success"] is True
    assert "response" in response

# Test ScheduleAgent
@pytest.mark.asyncio
async def test_schedule_agent():
    agent = ScheduleAgent()
    
    # Test event creation
    response = await agent.create_event(
        title="Test Meeting",
        start_time=datetime.utcnow() + timedelta(hours=1),
        end_time=datetime.utcnow() + timedelta(hours=2),
        description="This is a test meeting",
        user_id=1
    )
    assert response["success"] is True
    assert "event_id" in response
    
    # Test schedule query
    response = await agent.handle_specific_query(
        "When can I schedule a 1-hour meeting this week?"
    )
    assert response["success"] is True
    assert "response" in response

# Test CommunicationAgent
@pytest.mark.asyncio
async def test_communication_agent():
    agent = CommunicationAgent()
    
    # Test message creation
    response = await agent.create_message(
        content="This is a test message",
        priority=1,
        user_id=1
    )
    assert response["success"] is True
    assert "message_id" in response
    
    # Test communication query
    response = await agent.handle_specific_query(
        "Summarize my urgent emails from today"
    )
    assert response["success"] is True
    assert "response" in response

# Test AgentOrchestrator
@pytest.mark.asyncio
async def test_orchestrator():
    orchestrator = AgentOrchestrator()
    
    # Test query classification
    agents = await orchestrator.classify_query(
        "I need to schedule a meeting to discuss the project proposal"
    )
    assert len(agents) > 0
    assert "schedule" in agents
    
    # Test agent coordination
    response = await orchestrator.coordinate_agents(
        "I have a presentation due Friday, when should I work on it?"
    )
    assert response["success"] is True
    assert "response" in response
    
    # Test agent status
    status = await orchestrator.get_agent_status()
    assert status["success"] is True
    assert "agents" in status

# Test complex scenarios
@pytest.mark.asyncio
async def test_complex_scenarios():
    orchestrator = AgentOrchestrator()
    
    # Test multi-agent coordination
    response = await orchestrator.coordinate_agents(
        "I have an urgent email about the project deadline, and I need to schedule a meeting to discuss it"
    )
    assert response["success"] is True
    assert "response" in response
    assert "agent_responses" in response
    
    # Test task scheduling coordination
    response = await orchestrator.coordinate_agents(
        "Schedule my workout for tomorrow morning and create a task to prepare my presentation"
    )
    assert response["success"] is True
    assert "response" in response

if __name__ == "__main__":
    pytest.main([__file__]) 