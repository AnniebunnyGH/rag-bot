# Задание 2. Подготовка базы знаний (Divinity: Original Sin 2 -> Aethelgard)

---

## 1. Выбор предметной области и обоснование

Для построения изолированной базы знаний, исключающей возможность «угадывания» ответов моделью из предобученных весов (zero prior knowledge), выбрана вселенная культовой ролевой игры **Divinity: Original Sin 2** (разработчик Larian Studios).

### Почему именно эта вселенная:
1. **Глубокий лор и разветвлённая система связей:** Включает в себя фундаментальные законы магии, противостояние богов и древней расы, межфракционные конфликты, персонажей с уникальными предысториями и детализированные локации.
2. **Идеальная аналогия с корпоративной базой знаний:**
   - Роли и фракции аналогичны отделам и стейкхолдерам компании (инквизиция, паладины, повстанцы, наемники).
   - Магические законы и артефакты аналогичны техническим регламентам, архитектурным решениям (ADR) и стандартам безопасности.
   - События и катаклизмы моделируют инциденты и исторические релизы.
3. **Строгая верификация RAG:** Замена всех ключевых терминов на вымышленные позволяет на 100% удостовериться, что LLM черпает факты исключительно из векторного индекса, а не из своей памяти.

---

## 2. Структура и состав базы знаний

Сформировано **37 уникальных сущностей** (в формате Markdown), разбитых на 6 тематических категорий:

| Категория | Количество документов | Примеры сущностей |
| :--- | :---: | :--- |
| **Персонажи** | 16 | Lucian the Divine, Dallis the Hammer, Alexandar, Malady, Fane, Lohse, Ifan, Sebille, Red Prince, Beast, Tarquin, Gareth, Braccus Rex, Adramahlihk, Lord Kemm, Arhu |
| **Концепции магии и мира** | 4 | Source & Sourcerers, The Void & Voidwoken, Godwoken, Silent Monks & Purging |
| **Артефакты и материи** | 4 | Source Collar, Deathfog, Lady Vengeance, Anathema |
| **Способности** | 1 | Source Vampirism |
| **Фракции и культы** | 5 | Divine Order, Paladins, The Black Ring, The Seekers, The Lone Wolves |
| **Локации** | 5 | Fort Joy, Reaper's Coast & Driftwood, Bloodmoon Island, Nameless Isle, Arx |
| **Исторические события** | 2 | Purge of the Elves, Council of Seven |
| **ИТОГО:** | **37** | **Полное покрытие ключевого лора** |

Каждая статья оформлена по принципу: *один файл — одна сущность*, с четкими разделами, фактами, характеристиками и взаимосвязями с другими субъектами мира.

---

## 3. Логика подмены терминов и словарь соответствий (`terms_map.json`)

Для обфускации разработан скрипт `src/prepare_kb.py`.  
Алгоритм подмены гарантирует целостность текста:
- Словарь содержит **90 пар замен**.
- Замены выполняются **по убыванию длины ключей** (от длинных фраз к коротким), чтобы избежать ложных частичных замен (например, замена `Source Collar` происходит раньше, чем замена одиночного слова `Source`).
- Применяются регулярные выражения с границами слов (`\b...\b`), сохраняющие падежи и пунктуацию.

### Ключевые соответствия в `terms_map.json`:

```json
{
  "Rivellon": "Aethelgard",
  "Source": "Aether-Prana",
  "Sourcerers": "Aether-Weavers",
  "The Void": "The Abyssal Rift",
  "Voidwoken": "Nether-Abominations",
  "God King": "The Nether-Monarch",
  "Lucian the Divine": "Archon Valerius",
  "The Divine": "The Sovereign Archon",
  "Godwoken": "Archon-Ascendants",
  "Seven Gods": "The Septem Pantheon",
  "Silent Monks": "Hollowed Thralls",
  "Purging": "Essence-Excision",
  "Dallis the Hammer": "Matron Vespera the Cleaver",
  "Bishop Alexandar": "Hierarch Aurelius",
  "Malady": "Morrigan the Half-Fiend",
  "Fane": "Kaelen the Ossuary",
  "Lohse": "Lyrissa the Chime",
  "Ifan ben-Mezd": "Theron Blackthorn",
  "Sebille": "Nyx the Scarred Needle",
  "Red Prince": "Crimson Scion Ignis",
  "Beast": "Torgar Ironbeard",
  "Tarquin": "Balthazar the Reliquary",
  "Braccus Rex": "Dread-Emperor Morvan",
  "Adramahlihk": "Lord Malphas",
  "The Doctor": "The Crimson Chirurgeon",
  "Divine Order": "The Inquisitorial Concordat",
  "Magisters": "Concordat Justiciars",
  "Paladins of the Divine Order": "Lumen Paladins",
  "The Black Ring": "The Obsidian Circle",
  "Seekers": "The Emancipators",
  "Lone Wolves": "The Ironfang Syndicate",
  "Deathfog": "Necro-Miasma",
  "Lady Vengeance": "The Timber-Revenant",
  "Anathema": "The Ruin-Glaive",
  "Source Collar": "Dampener Shackle",
  "Source Vampirism": "Prana-Siphoning",
  "Fort Joy": "Citadel Sorrow",
  "Reaper's Coast": "Gallow Shore",
  "Driftwood": "Mistport",
  "Bloodmoon Island": "Sanguine-Eclipse Atoll",
  "Nameless Isle": "Isle of the Forgotten Pantheon",
  "Arx": "Solaris Metropolis",
  "Purge of the Elves": "The Ash-Blight Holocaust",
  "Council of Seven": "The Conclave of Ascension"
}
```

---

## 4. Результат выполнения

1. **Директория `knowledge_base/`:** Создано **37 чистых Markdown-файлов** (`*.md`), при этом **имена самих файлов также полностью переименованы** в соответствии с вымышленными названиями (например, `kaelen_the_ossuary.md` вместо Fane, `archon_valerius.md` вместо Lucian, `necro_miasma.md` вместо Deathfog). Это гарантирует, что метаданные источника (`source`) также не раскрывают исходных имен.
2. **Скрипт генерации `src/prepare_kb.py`:** Автоматизирует очистку, подмену терминов за один проход regex и сохранение данных. Позволяет воспроизвести процесс одной командой `python src/prepare_kb.py`.
3. **Словарь `terms_map.json`:** Содержит полный маппинг исходных сущностей на синтетические.
4. **Невозможность угадывания:** Любой вопрос, сформулированный по терминам созданной базы (например: *«Какое оружие способно пробить божественный щит Archon Valerius?»* или *«Кто возглавляет The Emancipators на острове Citadel Sorrow?»*), модель LLM не сможет ответить без обращения к векторизованному контексту RAG.
