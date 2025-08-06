#!/usr/bin/env python3
"""
RAG 인덱스 빌드 스크립트
CSV 파일에서 데이터를 읽어 FAISS 인덱스를 생성합니다.
"""

import os
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
from dotenv import load_dotenv

def build_rag_index():
    """RAG 인덱스 빌드"""
    load_dotenv()
    
    # 설정
    csv_path = "./data/fortraining.csv"
    embed_model_name = os.getenv("EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    index_dir = os.getenv("RAG_INDEX_DIR", "./data/faiss_index")
    
    print("=== RAG 인덱스 빌드 시작 ===")
    
    # 디렉토리 생성
    os.makedirs(index_dir, exist_ok=True)
    
    # CSV 파일 읽기
    print(f"CSV 파일 읽는 중: {csv_path}")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {csv_path}")
    
    df = pd.read_csv(csv_path)
    print(f"데이터 개수: {len(df)}개")
    
    # 임베딩 모델 로드
    print(f"임베딩 모델 로드 중: {embed_model_name}")
    model = SentenceTransformer(embed_model_name)
    
    # 텍스트 데이터 준비
    texts = []
    for _, row in df.iterrows():
        texts.append((row['original_text'], row['refined_text']))
    
    # 원문 텍스트들에 대해 임베딩 생성
    print("임베딩 생성 중...")
    original_texts = [text[0] for text in texts]
    embeddings = model.encode(original_texts, show_progress_bar=True)
    
    # FAISS 인덱스 생성
    print("FAISS 인덱스 생성 중...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner Product (cosine similarity와 유사)
    
    # 임베딩 정규화 (코사인 유사도를 위해)
    normalized_embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    index.add(normalized_embeddings.astype('float32'))
    
    # 인덱스 저장
    index_path = os.path.join(index_dir, "faiss.index")
    texts_path = os.path.join(index_dir, "texts.pkl")
    
    print(f"인덱스 저장 중: {index_path}")
    faiss.write_index(index, index_path)
    
    print(f"텍스트 데이터 저장 중: {texts_path}")
    with open(texts_path, 'wb') as f:
        pickle.dump(texts, f)
    
    print(f"=== RAG 인덱스 빌드 완료 ===")
    print(f"인덱스 크기: {index.ntotal}개")
    print(f"임베딩 차원: {dimension}")
    print(f"저장 위치: {index_dir}")

def test_index():
    """빌드된 인덱스 테스트"""
    from services.rag_service import rag_service
    
    print("\n=== 인덱스 테스트 ===")
    test_query = "한국어 공부가 어려워요"
    
    try:
        results = rag_service.search_similar_examples(test_query, k=3)
        print(f"테스트 쿼리: {test_query}")
        print("검색 결과:")
        
        for i, (original, refined, score) in enumerate(results, 1):
            print(f"{i}. 유사도: {score:.3f}")
            print(f"   원문: {original}")
            print(f"   교정: {refined}")
            print()
            
    except Exception as e:
        print(f"테스트 실패: {e}")

if __name__ == "__main__":
    build_rag_index()
    test_index()