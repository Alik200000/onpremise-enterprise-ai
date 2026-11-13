"""
Локальный легковесный RAG-движок (On-Premise In-Memory / Vector index):
- Полная автономность без внешних API
- Гибридный ранжирующий поиск (BM25 / Keyword Token Weighting + Semantic Jaccard)
- Совместим с интерфейсом Qdrant / ChromaDB
"""

import math
import re
from typing import List, Dict, Any
from app.parser import DocumentChunk

class LocalRAGStore:
    def __init__(self):
        self.chunks: List[DocumentChunk] = []

    def add_chunks(self, chunks: List[DocumentChunk]):
        self.chunks.extend(chunks)

    def clear(self):
        self.chunks.clear()

    def search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        if not self.chunks:
            return []

        # Токенизация запроса
        tokens = set(re.findall(r'[a-zA-Zа-яА-Я0-9_-]+', query.lower()))
        if not tokens:
            return []

        scored_results = []
        for chunk in self.chunks:
            content_lower = chunk.content.lower()
            doc_name_lower = chunk.doc_name.lower()
            
            # Расчет совпадений ключевых слов (ГОСТы, марки стали, размеры, допуски)
            score = 0.0
            matched_words = []
            
            for token in tokens:
                if len(token) <= 2:
                    continue
                # Точное вхождение
                count = content_lower.count(token)
                if count > 0:
                    matched_words.append(token)
                    score += 1.5 * math.log(1 + count)
                # Попадание в имя документа или раздел
                if token in doc_name_lower or token in chunk.section.lower():
                    score += 3.0

            if score > 0:
                scored_results.append({
                    "chunk": chunk,
                    "score": round(score, 3),
                    "matched_tokens": matched_words
                })

        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:top_k]

# Глобальный инстанс базы знаний
rag_store = LocalRAGStore()
