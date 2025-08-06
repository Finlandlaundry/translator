# 한국어 교정 챗봇 🇰🇷💬

유학생을 위한 실시간 한국어 문장 교정 및 대화 서비스입니다. RAG 기반으로 자연스러운 교정 예시를 제공하고, AI가 친근한 응답으로 대화를 이어갑니다.

## 🌟 주요 기능

- **🔧 실시간 문장 교정**: 입력한 한국어 문장을 자연스럽게 교정
- **💭 AI 응답 생성**: 교정된 문장에 대해 친근한 응답 제공
- **🎯 RAG 기반 검색**: 유사한 예시를 찾아 더 정확한 교정 제공
- **🎨 스타일 선택**: 정중한 말투 vs 친근한 말투 선택 가능
- **⚡ 실시간 스트리밍**: WebSocket으로 토큰 단위 실시간 응답
- **💾 대화 기록**: 최근 10턴 대화 히스토리 관리
- **🛡️ 금칙어 필터**: 부적절한 내용 자동 필터링
- **📱 모바일 반응형**: 모든 디바이스에서 최적화된 UI

## 🏗️ 기술 스택

### 백엔드
- **FastAPI**: 고성능 웹 API 프레임워크
- **LangChain**: LLM 체이닝 및 프롬프트 관리
- **OpenAI API**: GPT 모델을 통한 텍스트 생성
- **sentence-transformers**: 다국어 임베딩 모델
- **FAISS**: 고속 벡터 유사도 검색
- **SQLite**: 채팅 히스토리 저장
- **WebSocket**: 실시간 스트리밍 통신

### 프론트엔드
- **Next.js 14**: React 기반 풀스택 프레임워크 (App Router)
- **TypeScript**: 타입 안전성 보장
- **Tailwind CSS**: 유틸리티 기반 스타일링
- **Heroicons**: 아이콘 라이브러리

## 📁 프로젝트 구조

```
.
├── server/                 # 백엔드 (FastAPI)
│   ├── models/            # 데이터 모델 및 스키마
│   │   ├── database.py    # SQLAlchemy 모델
│   │   └── schemas.py     # Pydantic 스키마
│   ├── services/          # 비즈니스 로직
│   │   ├── rag_service.py # RAG 검색 서비스
│   │   ├── llm_service.py # LLM 처리 서비스
│   │   └── chat_service.py # 채팅 관리 서비스
│   ├── routes/            # API 라우터
│   │   ├── chat.py        # REST API
│   │   └── websocket.py   # WebSocket API
│   ├── utils/             # 유틸리티
│   │   └── profanity_filter.py # 금칙어 필터
│   ├── main.py            # FastAPI 앱 진입점
│   ├── rag_build.py       # RAG 인덱스 빌드 스크립트
│   └── requirements.txt   # Python 의존성
├── web/                   # 프론트엔드 (Next.js)
│   ├── src/
│   │   ├── app/           # App Router 페이지
│   │   ├── components/    # React 컴포넌트
│   │   ├── lib/           # 라이브러리 (API, WebSocket)
│   │   └── types/         # TypeScript 타입 정의
│   ├── package.json       # Node.js 의존성
│   └── tailwind.config.js # Tailwind 설정
├── data/                  # 데이터 파일
│   └── fortraining.csv    # RAG 훈련 데이터
├── .env.example           # 백엔드 환경변수 예시
└── README.md              # 프로젝트 문서
```

## 🚀 빠른 시작

### 1. 저장소 클론

```bash
git clone <repository-url>
cd korean-correction-chatbot
```

### 2. 백엔드 설정

```bash
# 백엔드 디렉토리로 이동
cd server

# Python 가상환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp ../.env.example .env
# .env 파일에서 OPENAI_API_KEY 설정 필수!
```

### 3. RAG 인덱스 생성

```bash
# 백엔드 디렉토리에서 실행
python rag_build.py
```

### 4. 백엔드 서버 실행

```bash
# 백엔드 디렉토리에서 실행
python main.py
# 또는
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 프론트엔드 설정

```bash
# 새 터미널에서 프론트엔드 디렉토리로 이동
cd web

# Node.js 의존성 설치
npm install

# 환경변수 설정
cp .env.local.example .env.local

# 개발 서버 실행
npm run dev
```

### 6. 접속

- **프론트엔드**: http://localhost:3000
- **백엔드 API 문서**: http://localhost:8000/docs

## ⚙️ 환경변수 설정

### 백엔드 (.env)

```bash
# OpenAI API 설정 (필수)
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4o-mini

# 임베딩 모델
EMBED_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

# RAG 인덱스 경로
RAG_INDEX_DIR=./data/faiss_index

# 서버 설정
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# 데이터베이스
DATABASE_URL=sqlite:///./data/chat_history.db

# 기타 설정
MAX_CHAT_HISTORY=10
PROFANITY_FILTER_ENABLED=true
```

### 프론트엔드 (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## 🔧 API 사용법

### REST API 예시

```bash
# 채팅 요청
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "안녕하세요 저는 한국에 유학하는 학생이에요",
    "style": "formal"
  }'

# 응답 예시
{
  "refined_text": "안녕하세요, 저는 한국에 유학하고 있는 학생입니다.",
  "reply_text": "안녕하세요! 한국에서 유학 생활을 하고 계시는군요. 어떤 전공을 공부하고 계신가요?",
  "session_id": "abc123def456"
}

# 히스토리 조회
curl "http://localhost:8000/api/chat/history/abc123def456"
```

### WebSocket 사용법

```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/chat');

// 메시지 전송
ws.send(JSON.stringify({
  message: "한국어 공부가 어려워요",
  style: "casual",
  session_id: "abc123def456"
}));

// 응답 수신
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.type, data.content);
  // refined, reply_start, reply_chunk, reply_complete, done
};
```

## 🐳 Docker 배포

### Docker Compose 사용

```bash
# Docker Compose 파일 생성 (docker-compose.yml)
version: '3.8'
services:
  backend:
    build: ./server
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
  
  frontend:
    build: ./web
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend

# 실행
docker-compose up --build
```

## 🧪 테스트

### 백엔드 테스트

```bash
cd server

# 헬스 체크
curl http://localhost:8000/health

# RAG 인덱스 테스트
python rag_build.py
```

### 프론트엔드 테스트

```bash
cd web

# 빌드 테스트
npm run build

# 린트 체크
npm run lint
```

## 📊 성능 최적화

- **RAG 검색**: FAISS 인덱스로 고속 벡터 검색
- **스트리밍**: WebSocket으로 실시간 토큰 단위 응답
- **캐싱**: 임베딩 모델 및 LLM 인스턴스 재사용
- **메모리 관리**: 최신 10턴 대화만 유지
- **모바일 최적화**: 반응형 UI 및 터치 최적화

## 🔒 보안 고려사항

- **API 키 관리**: 환경변수로 안전하게 저장
- **금칙어 필터**: 부적절한 내용 자동 필터링
- **CORS 설정**: 프로덕션에서 적절한 도메인 제한
- **입력 검증**: Pydantic으로 엄격한 타입 체크
- **에러 처리**: 사용자에게 민감한 정보 노출 방지

## 🛠️ 개발 및 확장

### 새로운 교정 데이터 추가

1. `data/fortraining.csv`에 원문,교정문 형태로 데이터 추가
2. `python server/rag_build.py` 실행하여 인덱스 재구축

### 새로운 언어 모델 추가

1. `server/services/llm_service.py`에서 모델 설정 변경
2. 환경변수 `OPENAI_MODEL` 업데이트

### UI 커스터마이징

1. `web/src/components/` 컴포넌트 수정
2. `web/tailwind.config.js`에서 테마 색상 변경

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ 지원 및 문의

- **Issues**: GitHub Issues를 통해 버그 리포트 및 기능 요청
- **Discussions**: GitHub Discussions에서 질문 및 아이디어 공유

## 🔄 버전 히스토리

- **v1.0.0**: 초기 릴리스
  - 기본 문장 교정 및 응답 기능
  - RAG 기반 예시 검색
  - 실시간 스트리밍 지원
  - 모바일 반응형 UI

---

⭐ 이 프로젝트가 도움이 되셨다면 Star를 눌러주세요!