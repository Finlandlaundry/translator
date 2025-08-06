import uuid
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from models.database import ChatHistoryDB, get_db
from models.schemas import ChatHistory
import os
from dotenv import load_dotenv

load_dotenv()

class ChatService:
    def __init__(self):
        self.max_history = int(os.getenv("MAX_CHAT_HISTORY", "10"))
    
    def create_session_id(self) -> str:
        """새로운 세션 ID 생성"""
        return str(uuid.uuid4())
    
    def save_chat_history(self, db: Session, session_id: str, original_text: str, 
                         refined_text: str, reply_text: str) -> ChatHistoryDB:
        """채팅 히스토리 저장"""
        chat_entry = ChatHistoryDB(
            session_id=session_id,
            original_text=original_text,
            refined_text=refined_text,
            reply_text=reply_text
        )
        
        db.add(chat_entry)
        db.commit()
        db.refresh(chat_entry)
        
        # 최대 히스토리 수 제한
        self._cleanup_old_history(db, session_id)
        
        return chat_entry
    
    def get_chat_history(self, db: Session, session_id: str, limit: Optional[int] = None) -> List[Dict]:
        """채팅 히스토리 조회"""
        if limit is None:
            limit = self.max_history
        
        histories = db.query(ChatHistoryDB)\
                     .filter(ChatHistoryDB.session_id == session_id)\
                     .order_by(ChatHistoryDB.created_at.desc())\
                     .limit(limit)\
                     .all()
        
        # 최신순으로 정렬된 것을 다시 시간순으로 뒤집음
        histories.reverse()
        
        return [
            {
                "id": h.id,
                "session_id": h.session_id,
                "original_text": h.original_text,
                "refined_text": h.refined_text,
                "reply_text": h.reply_text,
                "created_at": h.created_at.isoformat() if h.created_at else None
            }
            for h in histories
        ]
    
    def _cleanup_old_history(self, db: Session, session_id: str):
        """오래된 히스토리 정리"""
        # 최신 N개만 유지하고 나머지는 삭제
        histories = db.query(ChatHistoryDB)\
                     .filter(ChatHistoryDB.session_id == session_id)\
                     .order_by(ChatHistoryDB.created_at.desc())\
                     .all()
        
        if len(histories) > self.max_history:
            old_histories = histories[self.max_history:]
            for old_history in old_histories:
                db.delete(old_history)
            db.commit()
    
    def get_recent_history_for_context(self, db: Session, session_id: str, limit: int = 5) -> List[Dict]:
        """컨텍스트용 최근 히스토리 조회 (간소화된 형태)"""
        histories = db.query(ChatHistoryDB)\
                     .filter(ChatHistoryDB.session_id == session_id)\
                     .order_by(ChatHistoryDB.created_at.desc())\
                     .limit(limit)\
                     .all()
        
        histories.reverse()  # 시간순 정렬
        
        return [
            {
                "refined_text": h.refined_text,
                "reply_text": h.reply_text
            }
            for h in histories
        ]

# 전역 채팅 서비스 인스턴스
chat_service = ChatService()