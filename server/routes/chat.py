from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db
from models.schemas import ChatRequest, ChatResponse
from services.llm_service import llm_service
from services.chat_service import chat_service

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    채팅 엔드포인트 - 문장 교정 및 응답 생성
    """
    try:
        # 세션 ID 처리
        session_id = request.session_id or chat_service.create_session_id()
        
        # 채팅 히스토리 조회 (컨텍스트용)
        chat_history = chat_service.get_recent_history_for_context(db, session_id, limit=5)
        
        # 1단계: 문장 교정
        refined_text = await llm_service.refine_text(request.message, request.style)
        
        # 2단계: 응답 생성
        reply_text = await llm_service.generate_reply(refined_text, request.style, chat_history)
        
        # 히스토리 저장
        chat_service.save_chat_history(
            db=db,
            session_id=session_id,
            original_text=request.message,
            refined_text=refined_text,
            reply_text=reply_text
        )
        
        return ChatResponse(
            refined_text=refined_text,
            reply_text=reply_text,
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채팅 처리 중 오류가 발생했습니다: {str(e)}")

@router.get("/chat/history/{session_id}")
async def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    채팅 히스토리 조회
    """
    try:
        history = chat_service.get_chat_history(db, session_id)
        return {"session_id": session_id, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"히스토리 조회 중 오류가 발생했습니다: {str(e)}")