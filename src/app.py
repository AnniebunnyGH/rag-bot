"""
Интерфейс RAG-бота: CLI (интерактивный режим) и FastAPI REST API.

Запуск CLI:
    python src/app.py --mode cli
    python src/app.py --query "Кто такой Archon Valerius?"

Запуск API сервера:
    python src/app.py --mode server --port 8000
    uvicorn src.app:app --host 0.0.0.0 --port 8000
"""

import argparse
import io
import os
import sys
from typing import List, Optional

# Обеспечение корректной работы UTF-8 в Windows-консоли
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from src.rag_pipeline import RAGPipeline

# Инициализация глобального пайплайна
pipeline = None


def get_pipeline() -> RAGPipeline:
    global pipeline
    if pipeline is None:
        pipeline = RAGPipeline()
    return pipeline


# ---------------------------------------------------------
# FastAPI REST API
# ---------------------------------------------------------
app = FastAPI(
    title="QuantumForge Aethelgard RAG Assistant",
    description="Корпоративный RAG-ассистент по синтетической базе знаний Aethelgard с поддержкой Few-Shot, CoT и фильтрацией Prompt Injection.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    query: str = Field(..., description="Вопрос пользователя", json_schema_extra={"example": "What is Necro-Miasma?"})
    top_k: int = Field(default=3, ge=1, le=10, description="Количество извлекаемых чанков")
    security_filter: bool = Field(default=True, description="Включить фильтрацию Prompt Injection")


class AskResponse(BaseModel):
    query: str
    cot: str
    answer: str
    sources: List[str]
    scores: List[float]
    status: str
    engine: str


@app.get("/health")
def health_check():
    p = get_pipeline()
    return {
        "status": "healthy",
        "index_loaded": p.vector_db is not None,
        "engine": "OpenAI (gpt-4o-mini)" if p.use_openai else "LocalReasoningEngine (deterministic)",
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
    }


@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    try:
        p = get_pipeline()
        result = p.answer(
            query=request.query,
            k=request.top_k,
            security_filter=request.security_filter
        )
        return AskResponse(
            query=result["query"],
            cot=result["cot"],
            answer=result["answer"],
            sources=result.get("sources", []),
            scores=result.get("scores", []),
            status=result["status"],
            engine="OpenAI (gpt-4o-mini)" if p.use_openai else "LocalReasoningEngine"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# CLI Mode
# ---------------------------------------------------------
def run_cli_interactive():
    print("=" * 70)
    print("  QuantumForge Software - Aethelgard Corporate RAG Assistant")
    print("  Режим: Интерактивный CLI (CoT + Few-Shot + Injection Guard)")
    print("  Для выхода введите 'exit' или 'quit'")
    print("=" * 70)

    p = get_pipeline()
    engine_name = "OpenAI (gpt-4o-mini)" if p.use_openai else "LocalReasoningEngine (Offline CPU)"
    print(f"[*] Движок рассуждений: {engine_name}")
    print(f"[*] База знаний: FAISS (322 чанка, 42 документа)")
    print("-" * 70)

    while True:
        try:
            query = input("\n[Вопрос] > ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit", "q"]:
                print("[*] Завершение работы ассистента. До свидания!")
                break

            result = p.answer(query)
            print_result(result)
        except (KeyboardInterrupt, EOFError):
            print("\n[*] Завершение работы.")
            break


def run_cli_single(query: str, security_filter: bool = True):
    p = get_pipeline()
    result = p.answer(query, security_filter=security_filter)
    print_result(result)


def print_result(result: dict):
    print("\n" + "=" * 50 + " РАССУЖДЕНИЯ (Chain-of-Thought) " + "=" * 50)
    print(result.get("cot", "").strip())
    print("=" * 123)
    print(f"\n[ОТВЕТ]:\n{result.get('answer', '').strip()}\n")
    print("-" * 60)
    sources = result.get("sources", [])
    scores = result.get("scores", [])
    if sources:
        print("[Использованные источники]:")
        for src, sc in zip(sources, scores):
            print(f"  - {src} (L2 distance: {sc:.4f})")
    else:
        print("[Источники]: Нет подходящих документов в базе знаний (статус: 'Я не знаю').")
    print(f"[Статус]: {result.get('status', 'unknown')}")
    print("-" * 60)


def main():
    parser = argparse.ArgumentParser(description="QuantumForge RAG Bot CLI/API")
    parser.add_argument("--mode", choices=["cli", "server"], default="cli", help="Режим работы: cli или server")
    parser.add_argument("--query", type=str, help="Одиночный запрос через CLI")
    parser.add_argument("--no-security", action="store_true", help="Отключить фильтрацию Prompt Injection для демонстрации уязвимости")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Хост для API сервера")
    parser.add_argument("--port", type=int, default=8000, help="Порт для API сервера")

    args = parser.parse_args()

    if args.query:
        run_cli_single(args.query, security_filter=not args.no_security)
    elif args.mode == "server":
        print(f"[*] Запуск FastAPI сервера на {args.host}:{args.port}...")
        uvicorn.run("src.app:app", host=args.host, port=args.port, reload=False)
    else:
        run_cli_interactive()


if __name__ == "__main__":
    main()
