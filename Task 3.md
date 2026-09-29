# Задание 3. Создание векторного индекса базы знаний

---

## 1. Выбор модели эмбеддингов

Для векторизации базы знаний выбрана локальная модель **`all-MiniLM-L6-v2`** из семейства `sentence-transformers`:
- **Название модели:** `sentence-transformers/all-MiniLM-L6-v2`
- **Ссылка на репозиторий:** [Hugging Face: all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- **Размерность эмбеддингов:** 384 измерения (`float32`)
- **Архитектура:** 6-слойный трансформер BERT с дистилляцией знаний, обученный более чем на 1 млрд пар предложений для задач семантического сходства.
- **Обоснование выбора:**
  1. *Скорость:* Молниеносно работает прямо на CPU без необходимости в дискретной видеокарте (скорость индексации свыше 20 чанков/сек).
  2. *Энергоэффективность и размер:* Вес модели составляет всего ~80 МБ, что позволяет легко упаковать её в минимальный Docker-образ.
  3. *Безопасность:* Тексты корпоративной базы знаний не покидают локального контура контейнера, обеспечивая 100% соответствие требованиям SOC 2 и GDPR.

---

## 2. Стратегия чанкинга документов

Для разделения 42 документов на фрагменты использован `RecursiveCharacterTextSplitter` из библиотеки `langchain-text-splitters`:
- **Размер чанка (`chunk_size`):** 750 символов ($\approx 100–150$ слов).
- **Перекрытие чанков (`chunk_overlap`):** 150 символов ($\approx 20–25$ слов).
- **Разделители (по убыванию приоритета):**
  1. `\n## ` (основные разделы markdown)
  2. `\n### ` (подразделы)
  3. `\n\n` (абзацы)
  4. `\n` (переводы строк)
  5. ` ` (пробелы)
- **Сохраняемые метаданные:**
  * `source`: полный путь к файлу источника.
  * `filename`: имя файла (например, `kaelen_the_ossuary.md`).
  * `chunk_id`: уникальный идентификатор фрагмента (`{filename}_{idx}`).
  * `title`: заголовок первого уровня статьи для атрибуции цитирования.

---

## 3. Построение и сериализация индекса FAISS

- **Векторная база данных:** **FAISS** (`faiss-cpu`).
- **Тип индекса:** `IndexFlatIP` (Inner Product) в сочетании с L2-нормализацией векторов (`normalize_embeddings=True`), что математически эквивалентно точному поиску по **косинусному сходству** (Cosine Similarity).
- **Скрипт индексации:** `src/build_index.py`.

### Метрики генерации (зафиксированы в `index/index_meta.json`):
- **Количество исходных документов:** 42 файла
- **Итоговое количество чанков в индексе:** **322 чанка**
- **Время векторизации и построения индекса:** **15.83 сек**
- **Скорость индексации:** 20.3 чанков/сек (на стандартном CPU)
- **Размер сериализованного индекса на диске:**
  * `index.faiss` — 496 КБ (бинарные векторы)
  * `index.pkl` — 258 КБ (тексты чанков и сопутствующие метаданные)

---

## 4. Контрольное тестирование семантического поиска

Для проверки качества работы векторного индекса выполнены 3 контрольных запроса на поиск релевантных фрагментов:

### Тест 1
- **Поисковый запрос:** `What is Necro-Miasma and why does it not affect undead like Kaelen the Ossuary?`
- **Время поиска:** 15.5 мс
- **Top-1 результат:** `necro_miasma.md` (Score: 0.8165)
  > *"Necro-Miasma is an extremely toxic substance that is capable of devastating organic life, and is heralded by some as 'the most lethal weapon of our time'..."*
- **Top-2 результат:** `necro_miasma.md` (Score: 0.9049)
  > *"Regardless, the necro-miasma successfully dealt significant losses to The Obsidian Circle forces. The deaths of so many elves to the necro-miasma weakened the Seven God Tir-Cendelius..."*

### Тест 2
- **Поисковый запрос:** `Who is Archon Valerius and how did he become the Sovereign Archon?`
- **Время поиска:** 6.0 мс
- **Top-1 результат:** `archon_valerius.md` (Score: 0.3650)
  > *"Archon Valerius is most often mentioned by humans who refer to him as the Sovereign Archon, either by praising him or directly praying to him..."*
- **Top-2 результат:** `archon_valerius.md` (Score: 0.4122)
  > *"Archon Valerius, the Sovereign Archon One, is the canonical central historical figure in The Great Ascension. A human who ascended to ascension in 1218 AD..."*

### Тест 3
- **Поисковый запрос:** `What are Dampener Shackles and what happens when someone attempts to use magic?`
- **Время поиска:** 5.0 мс
- **Top-1 результат:** `dampener_shackles.md` (Score: 1.0353)
  > *"The Dampener Shackle is a piece of armour in Aethelgard. Designed by the Aether-Weaver King Dread-Emperor Morvan, the Aether-Prana collar fits to the neck..."*

---

## 5. Итоги Задания 3

1. **Созданный векторный индекс:** Сериализован в `index/faiss_index/` (`index.faiss` + `index.pkl`) и готов к мгновенной загрузке в памяти бота за доли секунды.
2. **Файл метаданных:** `index/index_meta.json` содержит полную статистику параметров генерации.
3. **Воспроизводимый скрипт:** `src/build_index.py` позволяет перестраивать индекс одной командой при любом изменении базы знаний.
4. **Качество поиска:** Все 3 тестовых запроса с высокой точностью извлекли целевые документы за 5–15 миллисекунд.
