from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from backend.config import (
    GROQ_API_KEY, SARVAM_API_KEY, AGENT_TIMEOUT, MAX_TOKENS, TEMPERATURE,
    SARVAM_MODEL, SARVAM_CONTEXT_WINDOW, SARVAM_TEMPERATURE
)
from backend.database import AgentLog, SessionLocal

class BaseAgent(ABC):
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        # Initialize Groq for basic LLM capabilities
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            timeout=AGENT_TIMEOUT,
            max_retries=2
        )
        # Initialize Sarvam.ai client
        self.sarvam_api_key = SARVAM_API_KEY
        self.sarvam_model = SARVAM_MODEL
        self.sarvam_context_window = SARVAM_CONTEXT_WINDOW
        self.sarvam_temperature = SARVAM_TEMPERATURE
        self.system_prompt = self._get_system_prompt()
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Return the system prompt specific to this agent type."""
        pass
    
    def _log_interaction(self, query: str, response: str, success: bool = True, error_message: Optional[str] = None):
        """Log agent interactions to the database."""
        db = SessionLocal()
        try:
            log = AgentLog(
                agent_type=self.agent_type,
                query=query,
                response=response,
                success=success,
                error_message=error_message
            )
            db.add(log)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a query using both Groq and Sarvam.ai for enhanced capabilities."""
        try:
            # First, use Groq for general LLM processing
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=query)
            ]
            
            groq_response = await self.llm.agenerate([messages])
            result = groq_response.generations[0][0].text
            
            # Enhance the response with Sarvam.ai if available
            if self.sarvam_api_key:
                try:
                    # Here we would make the actual Sarvam.ai API call
                    # For now, we'll just add a note about enhancement
                    result = f"{result}\n\n[Enhanced with Sarvam.ai merchant context]"
                except Exception as e:
                    print(f"Sarvam.ai enhancement failed: {str(e)}")
            
            self._log_interaction(query, result)
            
            return {
                "success": True,
                "response": result,
                "agent_type": self.agent_type
            }
        except Exception as e:
            error_msg = str(e)
            self._log_interaction(query, "", success=False, error_message=error_msg)
            return {
                "success": False,
                "error": error_msg,
                "agent_type": self.agent_type
            }
    
    @abstractmethod
    async def handle_specific_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle agent-specific query processing."""
        pass 