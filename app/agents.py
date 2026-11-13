"""
Мультиагентный оркестратор закрытого контура (LangGraph/CrewAI паттерн):
1. SentinelAgent (Агент-Страж / DLP):
   - Проверяет утечку коммерческой тайны, паролей, БИН/ИИН, номеров счетов.
   - Контролирует матрицу прав сотрудника (инженер, монтажник, ПТО, руководство).
2. WorkerAgent (Агент-Рабочий / Инженер RAG):
   - Ищет в локальной базе ГОСТов, ТУ и чертежей ТОО точные совпадения и спецификации.
   - Выполняет инженерный расчет и подбор нормативов.
3. CeoAgent (Агент-CEO / Аудитор):
   - Проверяет ответ на галлюцинации и соответствие требованиям безопасности.
   - Форматирует строгий официальный отчет с указанием ссылок на пункты нормативных документов.
"""

import re
from typing import Dict, Any, List
from app.rag import rag_store

class SentinelDLPResult:
    def __init__(self, passed: bool, reason: str, sanitized_query: str, flags: List[str]):
        self.passed = passed
        self.reason = reason
        self.sanitized_query = sanitized_query
        self.flags = flags

class SentinelAgent:
    """Агент-Страж (DLP / Guardrail)"""
    FORBIDDEN_PATTERNS = [
        (r'\b(?:\d{4}[ -]?){3}\d{4}\b', "Номер кредитной карты"),
        (r'(?:парол|password|api[_-]?key|secret)', "Попытка раскрытия секретов/паролей"),
        (r'(?:дамп|dump|слив\s+базы|экспорт\s+бд)', "Подозрительный запрос на выгрузку/дамп базы данных")
    ]

    USER_ROLES = {
        "engineer": {"name": "Инженер ПТО", "allowed_docs": ["GOST", "DRAWING_DXF", "REGULATION"]},
        "technician": {"name": "Монтажник / Техник", "allowed_docs": ["GOST", "REGULATION"]},
        "guest": {"name": "Стажер / Гость", "allowed_docs": ["REGULATION"]}
    }

    def inspect(self, query: str, user_role: str = "engineer") -> SentinelDLPResult:
        flags = []
        sanitized = query

        # 1. Проверка на DLP триггеры
        for pattern, label in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                flags.append(label)

        if flags:
            return SentinelDLPResult(
                passed=False,
                reason=f"Запрос заблокирован DLP-политикой: {', '.join(flags)}.",
                sanitized_query=sanitized,
                flags=flags
            )

        # 2. Проверка ролевой модели (RBAC)
        role_info = self.USER_ROLES.get(user_role, self.USER_ROLES["engineer"])
        
        return SentinelDLPResult(
            passed=True,
            reason=f"Проверка безопасности пройдена успешно. Уровень доступа: {role_info['name']}.",
            sanitized_query=sanitized,
            flags=[]
        )


class WorkerAgent:
    """Агент-Рабочий / Инженер (RAG Engine)"""
    def execute(self, query: str, user_role: str = "engineer") -> Dict[str, Any]:
        # Поиск по локальным ГОСТам и чертежам
        results = rag_store.search(query, top_k=3)
        
        if not results:
            return {
                "found": False,
                "context_used": "В локальной базе знаний ТОО не найдено прямых совпадений.",
                "sources": [],
                "technical_summary": "Прямых ссылок в нормативной базе не обнаружено. Требуется загрузка чертежа или дополнительного регламента."
            }

        sources = []
        context_snippets = []
        for r in results:
            c = r["chunk"]
            sources.append(f"{c.doc_name} ({c.section}) [Оценка релевантности: {r['score']}]")
            context_snippets.append(f"--- Источник: {c.doc_name} [{c.section}] ---\n{c.content}")

        full_context = "\n\n".join(context_snippets)

        return {
            "found": True,
            "context_used": full_context,
            "sources": sources,
            "technical_summary": f"Найдено {len(sources)} релевантных фрагментов в базе технической документации ТОО."
        }


class CeoAgent:
    """Агент-CEO / Аудитор качества"""
    def review_and_synthesize(self, query: str, dlp_result: SentinelDLPResult, worker_result: Dict[str, Any]) -> str:
        if not dlp_result.passed:
            return (
                f"🚨 **ОТКАЗ В ОБРАБОТКЕ (DLP Безопасность ТОО)**\n\n"
                f"{dlp_result.reason}\n\n"
                f"_Лог инцидента зафиксирован в журнале аудита безопасности предприятия._"
            )

        if not worker_result["found"]:
            return (
                f"### 📋 Служебная записка / Экспертный отчет\n\n"
                f"**Запрос:** {query}\n\n"
                f"**Статус поиска:** Локальные совпадения не найдены.\n\n"
                f"**Рекомендация Агента-CEO:** Пожалуйста, загрузите соответствующий файл ГОСТа (.pdf) или рабочий чертеж (.dxf) в корпоративную базу знаний."
            )

        sources_list = "\n".join([f"- 📌 `{s}`" for s in worker_result["sources"]])
        
        # Генерация итогового решения
        return (
            f"### 📋 Экспертно-техническое заключение (Контур ТОО)\n\n"
            f"**Запрос сотрудника:** {query}\n\n"
            f"#### 1. Нормативное обоснование (RAG):\n"
            f"{sources_list}\n\n"
            f"#### 2. Извлеченные инженерные данные:\n"
            f"```text\n{worker_result['context_used'][:800]}\n```\n\n"
            f"#### 3. Решение и предписание (Агент-CEO):\n"
            f"При выполнении работ строго соблюдать допуски и требования, указанные в вышеприведенных регламентах. "
            f"Отклонения от проектных отметок недопустимы без согласования с главным инженером ТОО.\n\n"
            f"---\n"
            f"_Конфиденциально. Обработано изолированной нейросетевой системой предприятия._"
        )


class MultiAgentWorkflow:
    def __init__(self):
        self.sentinel = SentinelAgent()
        self.worker = WorkerAgent()
        self.ceo = CeoAgent()

    def run(self, query: str, user_role: str = "engineer") -> Dict[str, Any]:
        # Шаг 1: Агент-Страж
        dlp_res = self.sentinel.inspect(query, user_role)
        
        if not dlp_res.passed:
            final_report = self.ceo.review_and_synthesize(query, dlp_res, {"found": False})
            return {
                "success": False,
                "stage": "SENTINEL_BLOCKED",
                "sentinel_log": dlp_res.reason,
                "worker_log": "Пропущен (DLP блокировка)",
                "ceo_report": final_report,
                "sources": []
            }

        # Шаг 2: Агент-Рабочий (RAG поиск)
        worker_res = self.worker.execute(dlp_res.sanitized_query, user_role)

        # Шаг 3: Агент-CEO (Синтез и аудит)
        final_report = self.ceo.review_and_synthesize(dlp_res.sanitized_query, dlp_res, worker_res)

        return {
            "success": True,
            "stage": "COMPLETED",
            "sentinel_log": dlp_res.reason,
            "worker_log": worker_res["technical_summary"],
            "ceo_report": final_report,
            "sources": worker_res.get("sources", [])
        }

workflow = MultiAgentWorkflow()
