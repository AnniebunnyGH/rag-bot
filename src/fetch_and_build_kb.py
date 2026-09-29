"""
Скрипт загрузки реальных статей из официальной wiki (divinity.fandom.com),
их очистки от вики-разметки и обфускации для создания базы знаний RAG.

Пайплайн:
1. Скачивание 35+ реальных страниц из divinity.fandom.com через MediaWiki API.
2. Очистка от шаблонов {{infobox}}, навигационных плашек, категорий и ссылок.
3. Сохранение сырых очищенных текстов в data/raw/.
4. Применение словаря замен terms_map.json за один проход regex.
5. Сохранение итоговых детализированных статей (500–2500 слов) в knowledge_base/.
"""

import json
import os
import re
import time
import urllib.parse
import urllib.request
from typing import Dict, List, Tuple

# Список реальных страниц на divinity.fandom.com
FANDOM_PAGES: List[Tuple[str, str]] = [
    # (wiki_page_title, synthetic_name)
    ("Fane", "Kaelen the Ossuary"),
    ("Lucian", "Archon Valerius"),
    ("Dallis", "Matron Vespera the Cleaver"),
    ("Alexandar", "Hierarch Aurelius"),
    ("Malady", "Morrigan the Half-Fiend"),
    ("Lohse", "Lyrissa the Chime"),
    ("Ifan ben-Mezd", "Theron Blackthorn"),
    ("Sebille Kaleran", "Nyx the Scarred Needle"),
    ("The Red Prince", "Crimson Scion Ignis"),
    ("Marcus Miles", "Torgar Ironbeard"),
    ("Tarquin", "Balthazar the Reliquary"),
    ("Gareth Pryce", "Commander Ronen"),
    ("Braccus Rex", "Dread-Emperor Morvan"),
    ("Adramahlihk", "Lord Malphas"),
    ("Linder Kemm", "Marshal Victor Vane"),
    ("Arhu", "Arch-Mage Corvus"),
    ("Source", "Aether-Prana"),
    ("Sourcerer", "Aether-Weavers"),
    ("Voidwoken", "Nether-Abominations"),
    ("The Seven Gods", "The Septem Pantheon"),
    ("Hall of Echoes", "The Liminal Necropolis"),
    ("Eternals", "The Primordial Titans"),
    ("Godwoken", "Archon-Ascendants"),
    ("Silent Monk", "Hollowed Thralls"),
    ("Source Collar", "Dampener Shackles"),
    ("Deathfog", "Necro-Miasma"),
    ("The Lady Vengeance", "The Timber-Revenant"),
    ("Anathema", "The Ruin-Glaive"),
    ("Source Vampirism", "Prana-Siphoning"),
    ("Divine Order", "The Inquisitorial Concordat"),
    ("The Magisters", "Concordat Justiciars"),
    ("Black Ring", "The Obsidian Circle"),
    ("The Seekers", "The Emancipators"),
    ("The Lone Wolves", "The Ironfang Syndicate"),
    ("Fort Joy", "Citadel Sorrow"),
    ("Reaper's Coast", "Gallow Shore"),
    ("Bloodmoon Island", "Sanguine-Eclipse Atoll"),
    ("The Nameless Isle", "Isle of the Forgotten Pantheon"),
    ("Arx", "Solaris Metropolis"),
]

# Полный словарь замен терминов
TERMS_MAP: Dict[str, str] = {
    # Мир и фундаментальная магия
    "Rivellon": "Aethelgard",
    "Source Vampirism": "Prana-Siphoning",
    "Source Titan": "Colossus of Prana",
    "Source Collar": "Dampener Shackle",
    "Source Collars": "Dampener Shackles",
    "Source King": "Sovereign of Prana",
    "Source Hunters": "Prana Seekers",
    "Sourcerers": "Aether-Weavers",
    "Sourcerer": "Aether-Weaver",
    "Source": "Aether-Prana",
    "source": "aether-prana",
    
    # Пустота и сущности
    "The Void": "The Abyssal Rift",
    "the Void": "the Abyssal Rift",
    "Voidwoken": "Nether-Abominations",
    "Void": "Abyssal Rift",
    "God King": "The Nether-Monarch",
    "the God King": "the Nether-Monarch",
    "The Sworn": "The Blood-Bound",
    "Sworn": "Blood-Bound",
    "Eternals": "The Primordial Titans",
    "Eternal": "Primordial Titan",
    
    # Божественность и вера
    "Lucian the Divine": "Archon Valerius",
    "The Divine": "The Sovereign Archon",
    "the Divine": "the Sovereign Archon",
    "Divine": "Archon",
    "Godwoken": "Archon-Ascendants",
    "Seven Gods": "The Septem Pantheon",
    "Hall of Echoes": "The Liminal Necropolis",
    "Silent Monks": "Hollowed Thralls",
    "Silent Monk": "Hollowed Thrall",
    "Purging Wand": "Excision Scepter",
    "Purging": "Essence-Excision",
    "Purged": "Essence-Excised",
    
    # Персонажи
    "Dallis the Hammer": "Matron Vespera the Cleaver",
    "Dallis": "Matron Vespera",
    "Bishop Alexandar": "Hierarch Aurelius",
    "Alexandar": "Aurelius",
    "Malady": "Morrigan the Half-Fiend",
    "Fane": "Kaelen the Ossuary",
    "Lohse": "Lyrissa the Chime",
    "Ifan ben-Mezd": "Theron Blackthorn",
    "Ifan": "Theron",
    "Sebille": "Nyx the Scarred Needle",
    "The Red Prince": "Crimson Scion Ignis",
    "Red Prince": "Crimson Scion Ignis",
    "Beast": "Torgar Ironbeard",
    "Marcus Miles": "Torgar Ironbeard",
    "Tarquin": "Balthazar the Reliquary",
    "Gareth": "Commander Ronen",
    "Braccus Rex": "Dread-Emperor Morvan",
    "Adramahlihk": "Lord Malphas",
    "The Doctor": "The Crimson Chirurgeon",
    "Linder Kemm": "Marshal Victor Vane",
    "Lord Kemm": "Marshal Victor Vane",
    "Kemm": "Vane",
    "Arhu": "Arch-Mage Corvus",
    "Roost Anlon": "Kragor the Beastmaster",
    "Sallow Man": "The Ashen Ghoul",
    "Jahan": "Demono-Theurgist Vael",
    
    # Фракции и культы
    "Divine Order": "The Inquisitorial Concordat",
    "Magisters": "Concordat Justiciars",
    "Magister": "Concordat Justiciar",
    "Paladins of the Divine Order": "Lumen Paladins",
    "Paladins": "Lumen Paladins",
    "Paladin": "Lumen Paladin",
    "The Black Ring": "The Obsidian Circle",
    "Black Ring": "The Obsidian Circle",
    "The Seekers": "The Emancipators",
    "Seekers": "The Emancipators",
    "The Lone Wolves": "The Ironfang Syndicate",
    "Lone Wolves": "The Ironfang Syndicate",
    "Lone Wolf": "Ironfang Mercenary",
    "House of War": "Legion of the Sun",
    "House of Shadows": "Guild of the Umbra",
    "Ancient Empire": "Draconic Imperium",
    
    # Артефакты и материи
    "Deathfog": "Necro-Miasma",
    "deathfog": "necro-miasma",
    "The Lady Vengeance": "The Timber-Revenant",
    "Lady Vengeance": "The Timber-Revenant",
    "Anathema": "The Ruin-Glaive",
    "Swornbreaker": "Covenant-Cleaver",
    "Blood Rose": "Crimson Nectar Rose",
    
    # Локации
    "Fort Joy": "Citadel Sorrow",
    "Reaper's Coast": "Gallow Shore",
    "Driftwood": "Mistport",
    "Bloodmoon Island": "Sanguine-Eclipse Atoll",
    "The Nameless Isle": "Isle of the Forgotten Pantheon",
    "Nameless Isle": "Isle of the Forgotten Pantheon",
    "Arx": "Solaris Metropolis",
    "Cloisterwood": "Eldergrove Sanctuary",
    "Stonegarden": "The Barrow-Necropolis",
    "Paradise Downs": "Shattered Valleys",
    "Blackpits": "The Tar-Trenches",
    
    # События
    "Purge of the Elves": "The Ash-Blight Holocaust",
    "Council of Seven": "The Conclave of Ascension",
    "Siege of Arx": "The Siege of Solaris",
    "Great War": "The Pan-Continental War"
}


def fetch_wikitext(page_title: str) -> str:
    """Загружает wikitext страницы с divinity.fandom.com через MediaWiki API."""
    encoded_title = urllib.parse.quote(page_title)
    url = f"https://divinity.fandom.com/api.php?action=parse&page={encoded_title}&prop=wikitext&format=json"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        if "parse" in data and "wikitext" in data["parse"]:
            return data["parse"]["wikitext"]["*"]
    return ""


def clean_wikitext(wiki_text: str, title: str) -> str:
    """
    Преобразует wikitext в чистый, связный Markdown-документ:
    - Удаляет HTML-комментарии, ref-сноски, галереи и шаблоны {{...}}
    - Конвертирует вики-заголовки (== H2 == -> ## H2)
    - Преобразует ссылки [[A|B]] -> B, [[A]] -> A
    - Удаляет мусорные служебные блоки (Navigation, Gallery, References)
    """
    # Удаляем HTML комментарии
    text = re.sub(r"<!--.*?-->", "", wiki_text, flags=re.DOTALL)
    
    # Удаляем теги <ref>...</ref> и <ref ... />
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.DOTALL)
    text = re.sub(r"<ref[^>]*/>", "", text)
    
    # Удаляем вложенные шаблоны {{...}}
    for _ in range(5):
        text = re.sub(r"\{\{[^{}]*\}\}", "", text, flags=re.DOTALL)
        
    # Удаляем галереи <gallery>...</gallery>
    text = re.sub(r"<gallery[^>]*>.*?</gallery>", "", text, flags=re.DOTALL)
    
    # Конвертируем заголовки == Title == в Markdown
    text = re.sub(r"^=====\s*(.*?)\s*=====", r"#### \1", text, flags=re.M)
    text = re.sub(r"^====\s*(.*?)\s*====", r"#### \1", text, flags=re.M)
    text = re.sub(r"^===\s*(.*?)\s*===", r"### \1", text, flags=re.M)
    text = re.sub(r"^==\s*(.*?)\s*==", r"## \1", text, flags=re.M)
    
    # Конвертируем внутренние вики-ссылки [[Target|Display]] -> Display, [[Target]] -> Target
    text = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", text)
    
    # Удаляем внешние ссылки [http... display] -> display
    text = re.sub(r"\[https?://[^\s\]]+\s+([^\]]+)\]", r"\1", text)
    text = re.sub(r"\[https?://[^\s\]]+\]", "", text)
    
    # Удаляем жирный курсив '''text''' -> **text**, ''text'' -> *text*
    text = re.sub(r"\'\'\'(.*?)\'\'\'", r"**\1**", text)
    text = re.sub(r"\'\'(.*?)\'\'", r"*\1*", text)
    
    # Убираем служебные разделы в конце статьи (Gallery, References, Navigation, Trivia)
    junk_sections = ["See also", "References", "Gallery", "Navigation", "External links"]
    for junk in junk_sections:
        pattern = rf"##\s+{junk}.*"
        text = re.sub(pattern, "", text, flags=re.DOTALL | re.IGNORECASE)
        
    # Чистим лишние пустые строки
    lines = [line.strip() for line in text.splitlines()]
    cleaned_lines = []
    for line in lines:
        if line.startswith(("{|", "|}", "|-", "!")):  # вики-таблицы
            continue
        cleaned_lines.append(line)
        
    result = "\n".join(cleaned_lines)
    result = re.sub(r"\n{3,}", "\n\n", result).strip()
    
    # Добавляем главный заголовок статьи
    if not result.startswith("# "):
        result = f"# {title}\n\n{result}"
        
    return result


def apply_terms_mapping(text: str, mapping: Dict[str, str]) -> str:
    """Заменяет оригинальные термины на вымышленные за один проход regex."""
    sorted_keys = sorted(mapping.keys(), key=len, reverse=True)
    pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in sorted_keys) + r")\b")
    return pattern.sub(lambda m: mapping[m.group(1)], text)


def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(root_dir, "data", "raw")
    kb_dir = os.path.join(root_dir, "knowledge_base")
    terms_file = os.path.join(root_dir, "terms_map.json")
    
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(kb_dir, exist_ok=True)
    
    # Сохраняем актуальный terms_map.json
    with open(terms_file, "w", encoding="utf-8") as f:
        json.dump(TERMS_MAP, f, ensure_ascii=False, indent=2)
    print(f"Словарь соответствий сохранен: {terms_file} ({len(TERMS_MAP)} пар)")
    
    print(f"\n=== Загрузка и обработка {len(FANDOM_PAGES)} реальных страниц из divinity.fandom.com ===")
    
    processed = 0
    total_words = 0
    
    for page_title, synth_name in FANDOM_PAGES:
        print(f"[{processed+1}/{len(FANDOM_PAGES)}] Загрузка: '{page_title}' -> '{synth_name}'...", end=" ")
        try:
            wikitext = fetch_wikitext(page_title)
            if not wikitext:
                print("ОШИБКА: пустой ответ API")
                continue
                
            clean_text = clean_wikitext(wikitext, page_title)
            
            # Сохраняем сырой очищенный текст в data/raw/
            raw_filename = f"{re.sub(r'[^a-zA-Z0-9]+', '_', page_title).strip('_').lower()}.md"
            with open(os.path.join(raw_dir, raw_filename), "w", encoding="utf-8") as f:
                f.write(clean_text)
                
            # Применяем обфускацию терминов
            obfuscated_text = apply_terms_mapping(clean_text, TERMS_MAP)
            
            # Формируем имя файла из вымышленного имени
            safe_name = re.sub(r"[^a-zA-Z0-9]+", "_", synth_name).strip("_").lower()
            kb_filename = f"{safe_name}.md"
            
            with open(os.path.join(kb_dir, kb_filename), "w", encoding="utf-8") as f:
                f.write(obfuscated_text.strip() + "\n")
                
            word_count = len(obfuscated_text.split())
            total_words += word_count
            print(f"ГОТОВО ({word_count} слов, файл {kb_filename})")
            processed += 1
            
            # Небольшая пауза для соблюдения вежливости к API
            time.sleep(0.2)
            
        except Exception as e:
            print(f"ИСКЛЮЧЕНИЕ: {e}")
            
    print(f"\nУспешно обработано: {processed} документов.")
    print(f"Суммарный объем базы знаний: {total_words} слов (~{total_words * 1.3:.0f} токенов).")
    print(f"Средний объем документа: {total_words // max(1, processed)} слов.")


if __name__ == "__main__":
    main()
