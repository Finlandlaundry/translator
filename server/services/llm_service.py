import os
from typing import List, Dict, AsyncGenerator
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv
from models.schemas import StyleType
from services.rag_service import rag_service
from utils.profanity_filter import profanity_filter

load_dotenv()

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            model=self.model_name,
            temperature=0.7,
            streaming=True
        )
    
    def get_refinement_prompt(self, original_text: str, examples: str, style: StyleType) -> str:
        """문장 교정을 위한 프롬프트 생성"""
        style_instruction = {
            StyleType.FORMAL: "존댓말과 정중한 표현을 사용하여",
            StyleType.CASUAL: "자연스럽고 친근한 말투로"
        }
        
        return f"""당신은 한국어 문장 교정 전문가입니다. 유학생이 작성한 한국어 문장을 자연스럽게 교정해주세요.

{examples}

교정 지침:
1. {style_instruction[style]} 교정해주세요
2. 맞춤법, 띄어쓰기, 문법을 정확하게 수정
3. 자연스러운 한국어 표현으로 개선
4. 원래 의미는 그대로 유지
5. 교정된 문장만 출력하세요 (설명 없이)

교정할 문장: {original_text}

교정된 문장:"""
    
    def get_reply_prompt(self, refined_text: str, style: StyleType, chat_history: List[Dict]) -> str:
        """응답 생성을 위한 프롬프트 생성"""
        style_instruction = {
            StyleType.FORMAL: "정중하고 도움이 되는 존댓말로",
            StyleType.CASUAL: "친근하고 자연스러운 말투로"
        }
        
        # 채팅 히스토리 컨텍스트 생성
        history_context = ""
        if chat_history:
            history_context = "이전 대화 내용:\n"
            for entry in chat_history[-5:]:  # 최근 5턴만 포함
                history_context += f"사용자: {entry['refined_text']}\n"
                history_context += f"봇: {entry['reply_text']}\n"
            history_context += "\n"
        
        return f"""당신은 유학생을 도와주는 친근한 한국어 대화 파트너입니다.

{history_context}사용자가 교정된 문장으로 대화를 시작했습니다. {style_instruction[style]} 자연스럽게 응답해주세요.

응답 지침:
1. 상황에 맞는 적절한 반응
2. 대화를 이어갈 수 있는 내용
3. 유학생에게 도움이 되는 방향
4. 너무 길지 않게 (2-3문장 정도)
5. 한국 문화나 언어에 대한 팁이 있다면 자연스럽게 포함

사용자 메시지: {refined_text}

응답:"""
    
    async def refine_text(self, original_text: str, style: StyleType) -> str:
        """문장 교정"""
        # 금칙어 체크
        if not profanity_filter.is_safe(original_text):
            return "죄송합니다. 부적절한 내용이 포함되어 있어 교정할 수 없습니다."
        
        # RAG로 유사한 예시 검색
        examples = rag_service.get_refinement_examples(original_text, k=3)
        
        # 프롬프트 생성
        prompt = self.get_refinement_prompt(original_text, examples, style)
        
        # LLM 호출
        messages = [SystemMessage(content=prompt)]
        response = await self.llm.ainvoke(messages)
        
        refined_text = response.content.strip()
        
        # 금칙어 필터링
        if not profanity_filter.is_safe(refined_text):
            refined_text = profanity_filter.filter_text(refined_text)
        
        return refined_text
    
    async def generate_reply(self, refined_text: str, style: StyleType, chat_history: List[Dict] = None) -> str:
        """응답 생성"""
        if chat_history is None:
            chat_history = []
        
        # 프롬프트 생성
        prompt = self.get_reply_prompt(refined_text, style, chat_history)
        
        # LLM 호출
        messages = [SystemMessage(content=prompt)]
        response = await self.llm.ainvoke(messages)
        
        reply_text = response.content.strip()
        
        # 금칙어 필터링
        if not profanity_filter.is_safe(reply_text):
            reply_text = profanity_filter.filter_text(reply_text)
        
        return reply_text
    
    async def stream_reply(self, refined_text: str, style: StyleType, chat_history: List[Dict] = None) -> AsyncGenerator[str, None]:
        """스트리밍 응답 생성"""
        if chat_history is None:
            chat_history = []
        
        # 프롬프트 생성
        prompt = self.get_reply_prompt(refined_text, style, chat_history)
        
        # 스트리밍 LLM 호출
        messages = [SystemMessage(content=prompt)]
        
        async for chunk in self.llm.astream(messages):
            if chunk.content:
                # 간단한 실시간 금칙어 필터링 (완벽하지 않음)
                filtered_content = profanity_filter.filter_text(chunk.content)
                yield filtered_content

# 전역 LLM 서비스 인스턴스
llm_service = LLMService()