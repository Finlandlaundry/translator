import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from models.database import get_db, SessionLocal
from models.schemas import ChatRequest, StreamingResponse, StyleType
from services.llm_service import llm_service
from services.chat_service import chat_service

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_message(self, websocket: WebSocket, message: dict):
        await websocket.send_text(json.dumps(message, ensure_ascii=False))

manager = ConnectionManager()

@router.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    """
    WebSocket 스트리밍 채팅 엔드포인트
    """
    await manager.connect(websocket)
    db = SessionLocal()
    
    try:
        while True:
            # 클라이언트로부터 메시지 수신
            data = await websocket.receive_text()
            
            try:
                request_data = json.loads(data)
                
                # 요청 검증
                message = request_data.get("message", "").strip()
                style = request_data.get("style", "formal")
                session_id = request_data.get("session_id") or chat_service.create_session_id()
                
                if not message:
                    await manager.send_message(websocket, {
                        "type": "error",
                        "content": "메시지가 비어있습니다.",
                        "session_id": session_id
                    })
                    continue
                
                # StyleType 변환
                try:
                    style_type = StyleType(style)
                except ValueError:
                    style_type = StyleType.FORMAL
                
                # 채팅 히스토리 조회
                chat_history = chat_service.get_recent_history_for_context(db, session_id, limit=5)
                
                # 1단계: 문장 교정 (즉시 전송)
                refined_text = await llm_service.refine_text(message, style_type)
                
                await manager.send_message(websocket, {
                    "type": "refined",
                    "content": refined_text,
                    "session_id": session_id
                })
                
                # 2단계: 응답 스트리밍
                await manager.send_message(websocket, {
                    "type": "reply_start",
                    "content": "",
                    "session_id": session_id
                })
                
                reply_chunks = []
                async for chunk in llm_service.stream_reply(refined_text, style_type, chat_history):
                    reply_chunks.append(chunk)
                    await manager.send_message(websocket, {
                        "type": "reply_chunk",
                        "content": chunk,
                        "session_id": session_id
                    })
                
                # 전체 응답 텍스트 조합
                reply_text = "".join(reply_chunks)
                
                await manager.send_message(websocket, {
                    "type": "reply_complete",
                    "content": reply_text,
                    "session_id": session_id
                })
                
                # 히스토리 저장
                chat_service.save_chat_history(
                    db=db,
                    session_id=session_id,
                    original_text=message,
                    refined_text=refined_text,
                    reply_text=reply_text
                )
                
                await manager.send_message(websocket, {
                    "type": "done",
                    "content": "완료",
                    "session_id": session_id
                })
                
            except json.JSONDecodeError:
                await manager.send_message(websocket, {
                    "type": "error",
                    "content": "잘못된 JSON 형식입니다.",
                    "session_id": ""
                })
                
            except Exception as e:
                await manager.send_message(websocket, {
                    "type": "error",
                    "content": f"처리 중 오류가 발생했습니다: {str(e)}",
                    "session_id": session_id if 'session_id' in locals() else ""
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    finally:
        db.close()