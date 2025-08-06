from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class StyleType(str, Enum):
    FORMAL = "formal"  # 존댓말
    CASUAL = "casual"  # 캐주얼

class ChatRequest(BaseModel):
    message: str
    style: StyleType = StyleType.FORMAL
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    refined_text: str
    reply_text: str
    session_id: str

class StreamingResponse(BaseModel):
    type: str  # "refined" | "reply" | "done"
    content: str
    session_id: str

class ChatHistory(BaseModel):
    id: Optional[int] = None
    session_id: str
    original_text: str
    refined_text: str
    reply_text: str
    created_at: Optional[str] = None