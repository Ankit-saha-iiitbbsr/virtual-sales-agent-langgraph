from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class MessageRequest(BaseModel):
    customer_id: str = Field(..., description="Customer identifier")
    message: str = Field(..., description="Message content")

class MessageResponse(BaseModel):
    message_id: str
    customer_id: str
    response: str
    timestamp: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "message_id": "123e4567-e89b-12d3-a456-426614174000",
                "customer_id": "123456789",
                "response": "Hello! How can I help you today?",
                "timestamp": "2024-02-07T12:00:00"
            }
        }

class ChatHistory(BaseModel):
    message_id: str
    customer_id: str
    message: str
    response: str
    timestamp: datetime

class ChatHistoryResponse(BaseModel):
    customer_id: str
    history: List[ChatHistory]