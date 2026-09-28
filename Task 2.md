# Задание 2. Подготовка базы знаний (Divinity: Original Sin 2 -> Aethelgard)

---

## 1. Выбор предметной области и обоснование

Для построения изолированной базы знаний, исключающей возможность «угадывания» ответов моделью из предобученных весов (zero prior knowledge), выбрана вселенная культовой ролевой игры **Divinity: Original Sin 2** (разработчик Larian Studios).

### Источник данных:
Статьи выгружены напрямую из официальной энциклопедии **[divinity.fandom.com](https://divinity.fandom.com/)** через **MediaWiki API** с помощью автоматического пайплайна `src/fetch_and_build_kb.py`.

### Почему именно эта вселенная:
1. **Глубокий лор и разветвлённая система связей:** Включает в себя фундаментальные законы магии, противостояние богов и древней расы, межфракционные конфликты, персонажей с уникальными предысториями и детализированные локации.
2. **Идеальная аналогия с корпоративной базой знаний:**
   - Роли и фракции аналогичны отделам и стейкхолдерам компании (инквизиция, паладины, повстанцы, наемники).
   - Магические законы и артефакты аналогичны техническим регламентам, архитектурным решениям (ADR) и стандартам безопасности.
   - События и катаклизмы моделируют инциденты и исторические релизы.
3. **Строгая верификация RAG:** Замена всех ключевых терминов на вымышленные позволяет на 100% удостовериться, что LLM черпает факты исключительно из векторного индекса, а не из своей памяти.

---

## 2. Пайплайн сбора и очистки данных (`src/fetch_and_build_kb.py`)

1. **Выгрузка через API:** Скрипт обращается к эндпоинту `https://divinity.fandom.com/api.php?action=parse&prop=wikitext&format=json` и скачивает полный wikitext для 39 ключевых сущностей.
2. **Глубокая очистка разметки:**
   - Удаление HTML-комментариев, сносок `<ref>...</ref>` и галерей `<gallery>`.
   - Рекурсивная очистка шаблонов инфобоксов `{{infobox...}}` и навигационных плашек.
   - Конвертация уровней заголовков `== H2 ==` $\rightarrow$ `## H2`, `=== H3 ==` $\rightarrow$ `### H3`.
   - Нормализация внутренних ссылок `[[Статья|Отображение]]` $\rightarrow$ `Отображение`, `[[Статья]]` $\rightarrow$ `Статья`.
   - Удаление внешних ссылок и служебных разделов (References, Navigation, Gallery).
3. **Сохранение сырых данных:** Все очищенные оригиналы сохранены в папке `data/raw/` (39 документов).
4. **Обфускация:** Применение словаря замен `terms_map.json` за один проход regex с границами слов `\b...\b`.
5. **Сохранение базы:** Итоговые статьи с полностью переименованными именами сохранены в `knowledge_base/`.

---

## 3. Структура и статистика базы знаний

Сформировано **42 детализированных Markdown-документа** в `knowledge_base/`:
- **Суммарный объём:** **22 320 слов** ($\approx 29 000$ токенов).
- **Средний объём документа:** **572 слова** на статью.
- **Крупнейшие статьи:**
  * `archon_valerius.md` (Lucian) — **3 180 слов**
  * `the_inquisitorial_concordat.md` (Divine Order) — **1 502 слова**
  * `citadel_sorrow.md` (Fort Joy) — **1 235 слов**
  * `gallow_shore.md` (Reaper's Coast) — **1 201 слово**
  * `the_obsidian_circle.md` (Black Ring) — **1 153 слова**
  * `the_septem_pantheon.md` (The Seven Gods) — **910 слов**
  * `theron_blackthorn.md` (Ifan) — **896 слов**
  * `hierarch_aurelius.md` (Alexandar) — **819 слов**
  * `arch_mage_corvus.md` (Arhu) — **780 слов**
  * `nether_abominations.md` (Voidwoken) — **748 слов**
  * `kaelen_the_ossuary.md` (Fane) — **626 слов**

| Категория | Количество документов | Примеры сущностей |
| :--- | :---: | :--- |
| **Персонажи** | 17 | Lucian the Divine, Dallis, Alexandar, Malady, Fane, Lohse, Ifan, Sebille, Red Prince, Beast, Tarquin, Gareth, Braccus Rex, Adramahlihk, Lord Kemm, Arhu |
| **Концепции магии и мира** | 6 | Source, Sourcerers, The Void, Voidwoken, Godwoken, Silent Monks |
| **Артефакты и материи** | 5 | Source Collar, Deathfog, Lady Vengeance, Anathema, Swornbreaker |
| **Способности** | 1 | Source Vampirism |
| **Фракции и культы** | 6 | Divine Order, The Magisters, Paladins, The Black Ring, The Seekers, The Lone Wolves |
| **Локации** | 5 | Fort Joy, Reaper's Coast, Bloodmoon Island, Nameless Isle, Arx |
| **События и миры** | 2 | Purge of the Elves, Council of Seven |
| **ИТОГО:** | **42** | **Полноценная, глубокая база знаний** |

---

## 4. Логика подмены терминов (`terms_map.json`)

Словарь `terms_map.json` содержит **97 пар соответствий**.  
Замена выполняется за один проход скомпилированного регулярного выражения с альтернацией (`|`) по ключам, отсортированным по убыванию длины:

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
  "The Red Prince": "Crimson Scion Ignis",
  "Beast": "Torgar Ironbeard",
  "Tarquin": "Balthazar the Reliquary",
  "Braccus Rex": "Dread-Emperor Morvan",
  "Adramahlihk": "Lord Malphas",
  "The Doctor": "The Crimson Chirurgeon",
  "Linder Kemm": "Marshal Victor Vane",
  "Divine Order": "The Inquisitorial Concordat",
  "The Magisters": "Concordat Justiciars",
  "Paladins of the Divine Order": "Lumen Paladins",
  "The Black Ring": "The Obsidian Circle",
  "The Seekers": "The Emancipators",
  "The Lone Wolves": "The Ironfang Syndicate",
  "Deathfog": "Necro-Miasma",
  "The Lady Vengeance": "The Timber-Revenant",
  "Anathema": "The Ruin-Glaive",
  "Source Collar": "Dampener Shackles",
  "Source Vampirism": "Prana-Siphoning",
  "Fort Joy": "Citadel Sorrow",
  "Reaper's Coast": "Gallow Shore",
  "Driftwood": "Mistport",
  "Bloodmoon Island": "Sanguine-Eclipse Atoll",
  "The Nameless Isle": "Isle of the Forgotten Pantheon",
  "Arx": "Solaris Metropolis"
}
```

---

## 5. Итоги Задания 2

1. **Сырые данные (`data/raw/`):** 39 оригинальных страниц из `divinity.fandom.com`, очищенных от HTML и разметки.
2. **Синтетическая база (`knowledge_base/`):** 42 больших, глубоких документа Markdown (22 320 слов), полностью переименованных в соответствии с миром Aethelgard.
3. **Словарь (`terms_map.json`):** 97 пар терминов.
4. **Скрипт (`src/fetch_and_build_kb.py`):** Воспроизводимый пайплайн автоматической выгрузки и преобразования.
5. **Готовность к чанкингу:** Благодаря объёму в 22k слов документы будут разделены на сотни полноценных чанков, что обеспечит реалистичную и честную проверку качества семантического поиска в Задании 3.
