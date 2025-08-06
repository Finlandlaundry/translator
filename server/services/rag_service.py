import os
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
from typing import List, Tuple
from dotenv import load_dotenv

load_dotenv()

class RAGService:
    def __init__(self):
        self.embed_model_name = os.getenv("EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        self.index_dir = os.getenv("RAG_INDEX_DIR", "./data/faiss_index")
        self.model = None
        self.index = None
        self.texts = None
        
    def load_model(self):
        """임베딩 모델 로드"""
        if self.model is None:
            print(f"임베딩 모델 로드 중: {self.embed_model_name}")
            self.model = SentenceTransformer(self.embed_model_name)
        return self.model
    
    def load_index(self):
        """FAISS 인덱스 로드"""
        if self.index is None:
            index_path = os.path.join(self.index_dir, "faiss.index")
            texts_path = os.path.join(self.index_dir, "texts.pkl")
            
            if not os.path.exists(index_path) or not os.path.exists(texts_path):
                raise FileNotFoundError(f"인덱스 파일을 찾을 수 없습니다. {index_path} 또는 {texts_path}")
            
            self.index = faiss.read_index(index_path)
            
            with open(texts_path, 'rb') as f:
                self.texts = pickle.load(f)
                
        return self.index, self.texts
    
    def search_similar_examples(self, query: str, k: int = 3) -> List[Tuple[str, str, float]]:
        """유사한 예시 검색"""
        model = self.load_model()
        index, texts = self.load_index()
        
        # 쿼리 임베딩
        query_embedding = model.encode([query])
        
        # FAISS 검색
        scores, indices = index.search(query_embedding.astype('float32'), k)
        
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(texts):
                original, refined = texts[idx]
                results.append((original, refined, float(score)))
        
        return results
    
    def get_refinement_examples(self, query: str, k: int = 3) -> str:
        """교정 예시를 위한 컨텍스트 생성"""
        similar_examples = self.search_similar_examples(query, k)
        
        if not similar_examples:
            return ""
        
        examples_text = "다음은 한국어 문장 교정 예시들입니다:\n\n"
        for i, (original, refined, score) in enumerate(similar_examples, 1):
            examples_text += f"예시 {i}:\n"
            examples_text += f"원문: {original}\n"
            examples_text += f"교정: {refined}\n\n"
        
        return examples_text

# 전역 RAG 서비스 인스턴스
rag_service = RAGService()