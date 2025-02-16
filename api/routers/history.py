from fastapi import APIRouter, HTTPException
from ..models.schemas import ChatHistoryResponse, ChatHistory
from database.db_manager import DatabaseManager
from datetime import datetime

router = APIRouter()
db_manager = DatabaseManager()

@router.get("/history/{customer_id}", response_model=ChatHistoryResponse)
async def get_chat_history(customer_id: str):
    try:
        customer_id_int = int(customer_id)
        history = db_manager.get_customer_chat_history(customer_id_int)
        
        if not history:
            raise HTTPException(
                status_code=404,
                detail=f"No chat history found for customer {customer_id}"
            )
            
        return ChatHistoryResponse(
            customer_id=customer_id,
            history=[
                ChatHistory(
                    message_id=row["message_id"],
                    customer_id=str(row["customer_id"]),
                    message=row["message"],
                    response=row["response"],
                    timestamp=datetime.fromisoformat(row["timestamp"])
                ) for row in history
            ]
        )
        
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid customer ID format: {customer_id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving chat history: {str(e)}"
        )