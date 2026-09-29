"""
Скрипт верификации и тестирования Задания 4.
Выполняет серию запросов к RAG-пайплайну:
- 5 успешных запросов по базе знаний Aethelgard
- 2 запроса вне домена (проверка ответа 'Я не знаю')
"""

import io
import json
import os
import sys

# Обеспечение корректной работы UTF-8 в Windows-консоли
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.rag_pipeline import RAGPipeline


def main():
    print("=" * 80)
    print("  ЗАПУСК ВЕРИФИКАЦИОННЫХ ТЕСТОВ (ЗАДАНИЕ 4)")
    print("=" * 80)

    pipeline = RAGPipeline()

    test_queries = [
        # Успешные запросы по базе знаний
        {
            "id": 1,
            "type": "success",
            "query": "Who is Archon Valerius and how do people in Aethelgard refer to him?"
        },
        {
            "id": 2,
            "type": "success",
            "query": "What is Necro-Miasma and why is it harmless to Kaelen the Ossuary?"
        },
        {
            "id": 3,
            "type": "success",
            "query": "What weapon does Matron Vespera the Cleaver carry?"
        },
        {
            "id": 4,
            "type": "success",
            "query": "What are Nether-Abominations and why are they attracted to Aether-Prana?"
        },
        {
            "id": 5,
            "type": "success",
            "query": "What is Citadel Sorrow and what happens to Aether-Weavers imprisoned there?"
        },
        # Запросы вне домена (должен быть строгий отказ 'Я не знаю')
        {
            "id": 6,
            "type": "not_found",
            "query": "What are the technical specifications of Intel Core i9-14900K processor?"
        },
        {
            "id": 7,
            "type": "not_found",
            "query": "Who won the Battle of Yavin in Star Wars and destroyed the Death Star?"
        }
    ]

    results = []

    for t in test_queries:
        print(f"\n--- [Тест {t['id']}] ({t['type']}): \"{t['query']}\" ---")
        res = pipeline.answer(t["query"])
        results.append({
            "id": t["id"],
            "type": t["type"],
            "query": t["query"],
            "cot": res.get("cot", ""),
            "answer": res.get("answer", ""),
            "sources": res.get("sources", []),
            "scores": res.get("scores", []),
            "status": res.get("status", "")
        })
        print(f"Статус: {res.get('status')}")
        print(f"Источники: {res.get('sources')}")
        print(f"Scores: {[round(s, 4) for s in res.get('scores', [])]}")
        print(f"Ответ: {res.get('answer')[:160]}...")

    output_path = os.path.join(ROOT_DIR, "data", "task4_verification_results.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 80)
    print(f"[OK] Все верификационные тесты Задания 4 завершены. Результаты сохранены в {output_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
