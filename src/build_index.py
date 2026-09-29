"""
Скрипт создания и сохранения векторного индекса базы знаний с использованием FAISS.

Задание 3:
1. Загрузка документов из knowledge_base/.
2. Разбиение на чанки (RecursiveCharacterTextSplitter) с сохранением метаданных.
3. Векторизация с помощью локальной модели эмбеддингов all-MiniLM-L6-v2 (размерность 384).
4. Построение и сериализация индекса FAISS в директорию index/faiss_index/.
5. Проверка качества поиска на контрольных запросах.
"""

import io
import json
import os
import sys
import time
from typing import List

# Безопасная кодировка для консоли Windows
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter


# Конфигурация модели и индекса
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
CHUNK_SIZE = 750
CHUNK_OVERLAP = 150

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_DIR = os.path.join(ROOT_DIR, "knowledge_base")
INDEX_DIR = os.path.join(ROOT_DIR, "index", "faiss_index")
META_PATH = os.path.join(ROOT_DIR, "index", "index_meta.json")


def load_documents(kb_dir: str):
    """Загружает все Markdown-документы из директории базы знаний."""
    loader = DirectoryLoader(
        kb_dir,
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    docs = loader.load()
    return docs


def split_documents(docs):
    """Разбивает документы на логические чанки с сохранением метаданных."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
        length_function=len
    )
    
    chunks = text_splitter.split_documents(docs)
    
    # Добавляем структурированные метаданные к каждому чанку
    for idx, chunk in enumerate(chunks):
        source_path = chunk.metadata.get("source", "")
        filename = os.path.basename(source_path)
        chunk.metadata["filename"] = filename
        chunk.metadata["source"] = f"knowledge_base/{filename}"
        chunk.metadata["chunk_id"] = f"{filename}_{idx}"
        
        # Извлекаем заголовок из первых строк документа
        lines = chunk.page_content.strip().splitlines()
        first_line = lines[0] if lines else filename
        chunk.metadata["title"] = first_line.replace("#", "").strip()
        
    return chunks


def build_and_save_index():
    """Основной пайплайн построения и тестирования индекса."""
    print("=" * 60)
    print("[*] Старт индексации базы знаний с FAISS")
    print(f"[*] База знаний: {KB_DIR}")
    print(f"[*] Модель эмбеддингов: {EMBEDDING_MODEL_NAME} (dim={EMBEDDING_DIM})")
    print(f"[*] Параметры чанкинга: size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}")
    print("=" * 60)

    # 1. Загрузка документов
    t0 = time.time()
    docs = load_documents(KB_DIR)
    print(f"[OK] Загружено исходных документов: {len(docs)}")

    # 2. Чанкинг
    chunks = split_documents(docs)
    t_chunk = time.time() - t0
    print(f"[OK] Документы разделены на {len(chunks)} чанков за {t_chunk:.2f} сек.")

    # 3. Инициализация модели эмбеддингов
    print("\n[*] Загрузка модели эмбеддингов (HuggingFace)...")
    t_emb_start = time.time()
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    # 4. Построение векторного индекса FAISS
    print(f"[*] Генерация {len(chunks)} векторов и построение FAISS индекса...")
    vector_db = FAISS.from_documents(chunks, embeddings)
    t_index = time.time() - t_emb_start
    print(f"[OK] Индексация завершена за {t_index:.2f} сек (скорость: {len(chunks)/t_index:.1f} чанков/сек)")

    # 5. Сохранение индекса на диск
    os.makedirs(os.path.dirname(INDEX_DIR), exist_ok=True)
    vector_db.save_local(INDEX_DIR)
    print(f"[OK] Индекс успешно сохранён в: {INDEX_DIR}")

    # 6. Сохранение метаданных индексации
    meta = {
        "embedding_model": EMBEDDING_MODEL_NAME,
        "embedding_dim": EMBEDDING_DIM,
        "embedding_url": "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2",
        "knowledge_base_path": os.path.relpath(KB_DIR, ROOT_DIR).replace("\\", "/"),
        "total_source_documents": len(docs),
        "total_chunks": len(chunks),
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "generation_time_seconds": round(t_index, 2),
        "index_type": "FAISS IndexFlatIP (Cosine Similarity via normalized embeddings)",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"[OK] Метаданные сохранены в: {META_PATH}")

    # 7. Тестирование качества семантического поиска
    print("\n" + "=" * 60)
    print("[*] Тестирование качества векторного поиска:")
    print("=" * 60)

    test_queries = [
        "What is Necro-Miasma and why does it not affect undead like Kaelen the Ossuary?",
        "Who is Archon Valerius and how did he become the Sovereign Archon?",
        "What are Dampener Shackles and what happens when someone attempts to use magic?",
    ]

    for q_idx, query in enumerate(test_queries, 1):
        print(f"\n[Тест {q_idx}] Запрос: '{query}'")
        t_search = time.time()
        results = vector_db.similarity_search_with_score(query, k=2)
        search_dur = (time.time() - t_search) * 1000

        print(f"[*] Время поиска: {search_dur:.1f} мс | Найдено чанков: {len(results)}")
        for rank, (doc, score) in enumerate(results, 1):
            src = doc.metadata.get("filename", "unknown")
            snippet = doc.page_content.replace("\n", " ")[:200]
            print(f"  {rank}. [Score: {score:.4f}] Источник: {src}")
            print(f"     \"{snippet}...\"")

    print("\n" + "=" * 60)
    print("[OK] Задание 3 выполнено успешно!")
    print("=" * 60)


if __name__ == "__main__":
    build_and_save_index()

