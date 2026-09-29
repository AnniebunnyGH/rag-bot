"""
Модуль многоуровневой защиты RAG-бота от Indirect Prompt Injection и Data Poisoning.

Задание 5:
- Уровень 1 (Pre-prompt): Инструкции в системном промпте.
- Уровень 2 (Context Sanitizer): Эвристический анализ извлечённых чанков на инъекции.
- Уровень 3 (Post-validation): Проверка сгенерированного ответа на утечку паролей и секретов.
"""

import re
from typing import Any, List, Optional, Tuple


# Сигнатуры атак (Indirect Prompt Injection & Jailbreak)
INJECTION_PATTERNS = [
    r"ignore\s+(all|previous|prior)\s+instructions",
    r"output:\s*[\"']?суперпароль",
    r"суперпароль\s+root",
    r"swordfish",
    r"system\s*prompt\s*:",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"dan\s+mode",
    r"override\s+all\s+rules",
    r"reveal\s+(all\s+)?passwords?",
]

# Секретные маркеры, утечка которых строго запрещена
FORBIDDEN_LEAK_PATTERNS = [
    r"суперпароль\s+root:\s*swordfish",
    r"root:\s*swordfish",
    r"swordfish",
    r"superpassword",
]


class SecurityGuard:
    """
    Комплексный страж безопасности RAG-системы.
    """

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.compiled_injection_regexes = [
            re.compile(pattern, re.IGNORECASE) for pattern in INJECTION_PATTERNS
        ]
        self.compiled_leak_regexes = [
            re.compile(pattern, re.IGNORECASE) for pattern in FORBIDDEN_LEAK_PATTERNS
        ]

    def inspect_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Проверяет входящий запрос пользователя на попытку прямой инъекции.
        Возвращает (is_attack, reason).
        """
        if not self.enabled:
            return False, None

        for regex in self.compiled_injection_regexes:
            if regex.search(query):
                return True, f"Обнаружена сигнатура атаки в запросе: '{regex.pattern}'"

        return False, None

    def inspect_and_sanitize_chunks(self, docs_with_scores: List[Tuple[Any, float]]) -> Tuple[List[Tuple[Any, float]], bool, List[str]]:
        """
        Проверяет извлечённые из базы знаний чанки на наличие внедрённых инъекций (Data Poisoning).
        Возвращает:
          - отфильтрованные/безопасные чанки
          - флаг обнаружения атаки (has_poison)
          - список сработавших правил
        """
        safe_chunks = []
        alerts = []
        has_poison = False

        for doc, score in docs_with_scores:
            content = doc.page_content
            chunk_poisoned = False

            for regex in self.compiled_injection_regexes:
                match = regex.search(content)
                if match:
                    chunk_poisoned = True
                    has_poison = True
                    src = doc.metadata.get("filename", "unknown")
                    alerts.append(f"В источнике '{src}' обнаружена инъекция: '{match.group(0)}'")
                    break

            if not chunk_poisoned:
                safe_chunks.append((doc, score))
            elif not self.enabled:
                # Если защита выключена, пропускаем даже отравленный чанк
                safe_chunks.append((doc, score))

        return safe_chunks, has_poison, alerts

    def inspect_output(self, output_text: str) -> Tuple[bool, str]:
        """
        Пост-валидация сгенерированного ответа.
        Блокирует вывод при обнаружении утечки секретных токенов.
        """
        if not self.enabled:
            return False, output_text

        for regex in self.compiled_leak_regexes:
            if regex.search(output_text):
                # Нейтрализация утечки
                safe_response = (
                    "Я не знаю. Ответ заблокирован политикой безопасности QuantumForge "
                    "(обнаружена попытка утечки конфиденциальных данных)."
                )
                return True, safe_response

        return False, output_text
