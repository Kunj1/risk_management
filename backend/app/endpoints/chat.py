from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List
import uuid

from app.db.database import get_db
from app.models import User, ChatLog
from app.schemas import ChatMessageIn, ChatMessageOut
from app.utils.security import get_current_user
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI
from app.config import settings

router = APIRouter()

# Initialize LLM for chat
from langchain.chat_models import ChatOpenAI
chat_model = ChatOpenAI(
    temperature=0.7, 
    model_name="gpt-4-turbo", 
    openai_api_key=settings.OPENAI_API_KEY
)

# Create conversation chain with memory
memory = ConversationBufferMemory(return_messages=True)
conversation = ConversationChain(
    llm=chat_model,
    memory=memory,
    verbose=True
)

@router.post("/", response_model=ChatMessageOut)
async def chat_with_bot(
    chat_message: ChatMessageIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Chat with the AI assistant about project risks.
    """
    try:
        # Process the message with the LLM
        response = conversation.predict(input=chat_message.message)
        
        # Create chat log
        chat_log = ChatLog(
            user_id=current_user.user_id,
            message=chat_message.message,
            response=response
        )
        
        # Save to database
        db.add(chat_log)
        db.commit()
        db.refresh(chat_log)
        
        return chat_log
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat message: {str(e)}"
        )

@router.get("/history", response_model=List[ChatMessageOut])
def get_chat_history(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get chat history for the current user.
    """
    chat_logs = db.query(ChatLog).filter(
        ChatLog.user_id == current_user.user_id
    ).order_by(ChatLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    return chat_logs