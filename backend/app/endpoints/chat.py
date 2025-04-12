from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, Dict
import uuid

from ..db.database import get_db
from ..models import User, ChatLog
from ..schemas import ChatMessageIn, ChatMessageOut
from ..utils.security import get_current_user
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

from ..config import settings

router = APIRouter()

@router.post("/message", response_model=ChatMessageOut)
async def chat_with_bot(
    message_in: ChatMessageIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Process a chat message from the user and generate a response.
    """
    try:
        # Initialize the LLM based on your API keys
        if settings.OPENAI_API_KEY:
            llm = ChatOpenAI(temperature=0.7, model_name="gpt-4", api_key=settings.OPENAI_API_KEY)
        elif settings.GEMINI_API_KEY:
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7, google_api_key=settings.GEMINI_API_KEY)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No LLM API key configured"
            )
        
        # Query the DB for project information related to this user
        projects = db.query(User).filter(User.user_id == current_user.user_id).first().projects
        project_info = "\n".join([
            f"Project {p.name} (ID: {p.project_id}): Status: {p.status}, " 
            f"Resource availability: {p.resource_availability}%, "
            f"Payment received: {'Yes' if p.customer_payment_received else 'No'}, "
            f"Schedule delay: {p.schedule_delay} days"
            for p in projects
        ])
        
        # Create the system prompt with project information
        system_template = f"""
        You are the Risk Management Assistant, an AI that helps project managers understand and manage project risks.
        You have access to the following project information:
        
        {project_info}
        
        Respond to the user's queries about project risks, status, and provide recommendations for risk mitigation.
        Always be concise and provide actionable insights.
        """
        
        # Set up the prompt template
        chat_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template("{message}")
        ])
        
        # Create and run the chain
        chain = LLMChain(llm=llm, prompt=chat_prompt)
        response = await chain.arun(message=message_in.message)
        
        # Log the chat interaction in the database
        chat_log = ChatLog(
            user_id=current_user.user_id,
            message=message_in.message,
            response=response
        )
        db.add(chat_log)
        db.commit()
        db.refresh(chat_log)
        
        return chat_log
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat message: {str(e)}"
        )