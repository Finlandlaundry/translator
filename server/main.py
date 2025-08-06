import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from models.database import create_tables
from routes import chat, websocket

# 환경변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(
    title="한국어 교정 챗봇 API",
    description="유학생을 위한 한국어 문장 교정 및 대화 서비스",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 구체적인 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(websocket.router, prefix="/api", tags=["websocket"])

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    print("🚀 한국어 교정 챗봇 서버 시작 중...")
    
    # 데이터베이스 테이블 생성
    create_tables()
    print("✅ 데이터베이스 테이블 생성 완료")
    
    # RAG 인덱스 존재 확인
    rag_index_dir = os.getenv("RAG_INDEX_DIR", "./data/faiss_index")
    index_path = os.path.join(rag_index_dir, "faiss.index")
    
    if not os.path.exists(index_path):
        print("⚠️  RAG 인덱스가 없습니다. 'python server/rag_build.py'를 실행하여 인덱스를 생성하세요.")
    else:
        print("✅ RAG 인덱스 확인 완료")
    
    print("🎉 서버 시작 완료!")

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "한국어 교정 챗봇 API 서버",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat",
            "websocket": "/api/ws/chat",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8000"))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,  # 개발 모드
        log_level="info"
    )