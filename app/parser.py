"""
Модуль парсинга корпоративной технической документации ТОО:
- PDF (ГОСТы, СНиПы, регламенты, ТУ)
- DXF/DWG (инженерные чертежи: извлечение слоев, блоков, текста, спецификаций)
- TXT/MD (внутренние инструкции)
"""

import os
import re
from typing import List, Dict, Any

class DocumentChunk:
    def __init__(self, doc_name: str, doc_type: str, section: str, content: str, metadata: Dict[str, Any] = None):
        self.doc_name = doc_name
        self.doc_type = doc_type  # 'GOST', 'DRAWING_DXF', 'REGULATION', 'TXT'
        self.section = section
        self.content = content.strip()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_name": self.doc_name,
            "doc_type": self.doc_type,
            "section": self.section,
            "content": self.content,
            "metadata": self.metadata
        }

class DocumentParser:
    @staticmethod
    def parse_pdf(file_path: str) -> List[DocumentChunk]:
        """Парсинг PDF с разбивкой по страницам и разделам."""
        chunks = []
        doc_name = os.path.basename(file_path)
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    chunks.append(DocumentChunk(
                        doc_name=doc_name,
                        doc_type="GOST_PDF",
                        section=f"Стр. {page_idx + 1}",
                        content=text,
                        metadata={"page": page_idx + 1, "total_pages": len(reader.pages)}
                    ))
        except Exception as e:
            # Fallback text reading
            chunks.append(DocumentChunk(
                doc_name=doc_name,
                doc_type="GOST_PDF",
                section="Полный документ",
                content=f"[Ошибка чтения PDF структуры: {e}]",
                metadata={"error": str(e)}
            ))
        return chunks

    @staticmethod
    def parse_dxf(file_path: str) -> List[DocumentChunk]:
        """Извлечение слоев, текстовых аннотаций, блоков и размеров из чертежей DXF/DWG."""
        chunks = []
        doc_name = os.path.basename(file_path)
        try:
            import ezdxf
            doc = ezdxf.readfile(file_path)
            msp = doc.modelspace()
            
            # Собираем текстовые выноски и спецификации
            texts = []
            layers = set()
            for entity in msp:
                layers.add(entity.dxf.layer)
                if entity.dxftype() in ('TEXT', 'MTEXT'):
                    plain_text = entity.plain_text() if hasattr(entity, 'plain_text') else getattr(entity.dxf, 'text', '')
                    if plain_text.strip():
                        texts.append(f"[{entity.dxf.layer}] {plain_text.strip()}")
            
            content_summary = (
                f"Чертеж: {doc_name}\n"
                f"Слои проекта: {', '.join(sorted(layers))}\n"
                f"Спецификации и размеры:\n" + "\n".join(texts[:50])
            )
            chunks.append(DocumentChunk(
                doc_name=doc_name,
                doc_type="DRAWING_DXF",
                section="Модель / Спецификации чертежа",
                content=content_summary,
                metadata={"layers": list(layers), "annotations_count": len(texts)}
            ))
        except Exception as e:
            chunks.append(DocumentChunk(
                doc_name=doc_name,
                doc_type="DRAWING_DXF",
                section="Чертеж",
                content=f"Метаданные чертежа {doc_name}: (Формат DXF/DWG CAD)",
                metadata={"error": str(e)}
            ))
        return chunks

    @staticmethod
    def parse_text(file_path: str, doc_type: str = "REGULATION") -> List[DocumentChunk]:
        """Парсинг текстовых регламентов, СНиПов и ГОСТов."""
        chunks = []
        doc_name = os.path.basename(file_path)
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_text = f.read()

        # Разбиваем по разделам/пунктам (например "Раздел 1", "Пункт 3.2", "Лист 1")
        sections = re.split(r'\n(?=[0-9]+\.|\bРаздел\b|\bПункт\b|\bЛист\b)', raw_text)
        for idx, sec in enumerate(sections):
            sec_text = sec.strip()
            if sec_text:
                header = sec_text.split('\n')[0][:50]
                chunks.append(DocumentChunk(
                    doc_name=doc_name,
                    doc_type=doc_type,
                    section=f"Раздел {idx + 1}: {header}",
                    content=sec_text,
                    metadata={"index": idx}
                ))
        return chunks
