"""
Скрипт нарративной очистки базы знаний:
Устраняет мета-игровые артефакты (упоминания Divinity, NPC, Early Access, Category:, ru:),
приводя базу к стилю аутентичной энциклопедии вымышленного мира Aethelgard.
"""

import os
import re

KB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge_base")

REPLACEMENTS = [
    # Игра -> Мир
    (r"\bDivinity:\s*Original\s*Sin\s*(II|2)?\b", "Aethelgard"),
    (r"\bDivinity\s*II:\s*[A-Za-z\s]+\b", "the Ancient Chronicles"),
    (r"\bDivinity:\s*Fallen\s*Heroes\b", "the Later Wars"),
    (r"\bArchon\s*Divinity\b", "The Great Ascension"),
    (r"\bDivinity\b", "Ascension"),
    (r"\bdivinity\b", "ascension"),
    (r"\bRivellonian\b", "Aethelgardian"),
    (r"\bLucian\b", "Archon Valerius"),
    (r"\bSourcery Skill\b", "Aether-Weaving discipline"),
    (r"\bSourcery\b", "Aether-Weaving"),
    (r"\bsourcery\b", "aether-weaving"),
    (r"\bcannot be bought from any NPCs in the game\b", "cannot be acquired through standard scholarly or commercial trade"),
    (r"\bthe player can take control of\b", "historical chronicles document the actions of"),
    (r"\bplayer character\b", "central historical figure"),
    (r"\bplayers\b", "initiates"),
    (r"\bplayer\b", "initiate"),
    (r"\bNPCs\b", "merchants and scholars"),
    (r"\bNPC\b", "scholar"),
    (r"\bin the game\b", "in the realm"),
    (r"\bIn the game\b", "In the realm"),
]

STRIP_PATTERNS = [
    r"^Category:.*$",
    r"^[a-z]{2}:[А-Яа-яA-Za-z\s]+$",
    r"^thumb\|.*$",
    r"^.*Early Access.*$",
    r"^.*Baldur's Gate.*$",
    r"^.*Chris Avellone.*$",
    r"^.*Stephen Rooney.*$",
    r"^.*voice actor.*$",
    r"^.*Rhianna Pratchett.*$",
    r"^.*normal difficulty.*$",
    r"^.*Classic Difficulty.*$",
    r"^.*Special Skills \(Original Sin 2\).*$",
]


def clean_content(content: str) -> str:
    lines = content.splitlines()
    cleaned_lines = []
    skip_section = False

    for line in lines:
        trimmed = line.strip()
        
        # Пропуск секций разработки и других игр
        if trimmed.startswith("### Baldur's Gate") or trimmed.startswith("### Development") or trimmed.startswith("## Notes"):
            if "Baldur" in trimmed or "Development" in trimmed:
                skip_section = True
                continue
        elif trimmed.startswith("#") and not (trimmed.startswith("### Baldur") or trimmed.startswith("### Dev")):
            skip_section = False
            
        if skip_section:
            continue

        # Проверка на строки для удаления
        matched_strip = False
        for pat in STRIP_PATTERNS:
            if re.search(pat, trimmed, flags=re.IGNORECASE):
                matched_strip = True
                break
        if matched_strip:
            continue

        # Замены фраз
        new_line = line
        for pat, repl in REPLACEMENTS:
            new_line = re.sub(pat, repl, new_line)
        cleaned_lines.append(new_line)

    result = "\n".join(cleaned_lines)
    result = re.sub(r"\n{3,}", "\n\n", result).strip()
    return result + "\n"


def main():
    count = 0
    for filename in os.listdir(KB_DIR):
        if not filename.endswith(".md"):
            continue
        filepath = os.path.join(KB_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        cleaned = clean_content(content)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(cleaned)
        count += 1

    print(f"Успешно очищено и приведено к лорному стилю {count} файлов в {KB_DIR}")


if __name__ == "__main__":
    main()
