"""
Скрипт подготовки синтетической базы знаний для QuantumForge Software
на основе вселенной Divinity: Original Sin 2.

Функционал:
1. Содержит базу знаний из 37 сущностей вселенной Divinity: Original Sin 2
   (персонажи, артефакты, концепции магии, фракции, локации, исторические события).
2. Формирует полный словарь замен `terms_map.json`.
3. Очищает целевую директорию `knowledge_base/` и записывает 37 детальных Markdown-документов.
4. Выполняет надежную подмену терминов (от длинных словосочетаний к коротким),
   исключая возможность прямого угадывания фактов LLM по памяти.
"""

import json
import os
import re
import shutil
from typing import Dict, List, Tuple

# 1. Словарь соответствий терминов Divinity: Original Sin 2 -> Вымышленный мир Aethelgard
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
    "Seven": "Septem",
    "Hall of Echoes": "The Liminal Necropolis",
    "Silent Monks": "Hollowed Thralls",
    "Silent Monk": "Hollowed Thrall",
    "Purging Wand": "Excision Scepter",
    "Purging": "Essence-Excision",
    "Purged": "Essence-Excised",
    
    # Персонажи
    "Dallis the Hammer": "Matron Vespera the Cleaver",
    "Bishop Alexandar": "Hierarch Aurelius",
    "Alexandar": "Aurelius",
    "Malady": "Morrigan the Half-Fiend",
    "Fane": "Kaelen the Ossuary",
    "Lohse": "Lyrissa the Chime",
    "Ifan ben-Mezd": "Theron Blackthorn",
    "Ifan": "Theron",
    "Sebille": "Nyx the Scarred Needle",
    "Red Prince": "Crimson Scion Ignis",
    "Beast": "Torgar Ironbeard",
    "Marcus Miles": "Torgar Ironbeard",
    "Tarquin": "Balthazar the Reliquary",
    "Gareth": "Commander Ronen",
    "Braccus Rex": "Dread-Emperor Morvan",
    "Adramahlihk": "Lord Malphas",
    "The Doctor": "The Crimson Chirurgeon",
    "Lord Kemm": "Marshal Victor Vane",
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
    "Black Ring": "Obsidian Circle",
    "Seekers": "The Emancipators",
    "Lone Wolves": "The Ironfang Syndicate",
    "Lone Wolf": "Ironfang Mercenary",
    "House of War": "Legion of the Sun",
    "House of Shadows": "Guild of the Umbra",
    "Ancient Empire": "Draconic Imperium",
    
    # Артефакты и материи
    "Deathfog": "Necro-Miasma",
    "deathfog": "necro-miasma",
    "Lady Vengeance": "The Timber-Revenant",
    "Anathema": "The Ruin-Glaive",
    "Swornbreaker": "Covenant-Cleaver",
    "Blood Rose": "Crimson Nectar Rose",
    
    # Локации
    "Fort Joy": "Citadel Sorrow",
    "Reaper's Coast": "Gallow Shore",
    "Driftwood": "Mistport",
    "Bloodmoon Island": "Sanguine-Eclipse Atoll",
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

# 2. Массив из 37 детализированных статей по вселенной Divinity: Original Sin 2
DOS2_ARTICLES: List[Tuple[str, str, str]] = [
    (
        "character_lucian_the_divine",
        "Archon Valerius",
        """# Archon Valerius: The False Deity of Aethelgard

## Ascension and Rule
Archon Valerius, formerly a humble mortal general during the Great War, was elevated to supreme godhood when the Septem Pantheon pooled their essence to create a singular living champion. Bestowed with unbridled mastery over Aether-Prana, Valerius united the fractured kingdoms into the Inquisitorial Concordat, establishing peace across Aethelgard for decades.

## The Secret Sacrifice and the Ash-Blight Holocaust
Beneath the pious surface of his reign, Valerius uncovered an existential secret: every exertion of mortal Aether-Prana frayed the veil between worlds, allowing Nether-Abominations from the Abyssal Rift to consume reality. To seal the Rift, the Septem Pantheon required astronomical reserves of energy. Valerius covertly authorized the deployment of Necro-Miasma over the ancestral forests during the Ash-Blight Holocaust, obliterating hundreds of thousands of woodland elves in an instant.

## Faked Death and Entombed Preservation
Publicly proclaimed dead after the cataclysm, Valerius secretly retreated into the subterranean crypts beneath the grand basilica of Solaris Metropolis. Sustained in suspended stasis, he orchestrated the harvesting of mortal souls through Matron Vespera the Cleaver to permanently starve the Nether-Monarch.
"""
    ),
    (
        "character_dallis_the_hammer",
        "Matron Vespera the Cleaver",
        """# Matron Vespera the Cleaver: High Justiciar of the Concordat

## Public Authority and Brutality
Matron Vespera assumed de facto supreme leadership of the Inquisitorial Concordat following the supposed martyrdom of Archon Valerius. Clad in heavy dragon-carved silver plate and wielding a colossal warhammer, she enacted draconian edicts rounding up all registered Aether-Weavers across the provinces.

## True Identity: The Primordial Titan
Unbeknownst to her legions, Vespera was not human; she was one of the last surviving Primordial Titans, awakened from millennial slumber. Utilizing advanced shapeshifting masks and an ancient intellect, she allied with Valerius to eradicate the parasite gods of the Septem Pantheon.

## Creation of Hollowed Thralls
Vespera engineered the Essence-Excision process using specialized Excision Scepters. By surgically stripping Aether-Prana from captured weavers, she transformed dangerous magical adepts into docile, unfeeling Hollowed Thralls, neutralizing the beacon that summoned Nether-Abominations.
"""
    ),
    (
        "character_bishop_alexandar",
        "Hierarch Aurelius",
        """# Hierarch Aurelius: Scion of the Fallen Archon

## Lineage and Public Role
Hierarch Aurelius was the biological son of Archon Valerius. Possessing charismatic oratory skill and naive idealism, Aurelius was appointed political figurehead of the Inquisitorial Concordat and governor of the penal settlement at Citadel Sorrow.

## Puppet of Vespera
Despite his lofty title, Aurelius was perpetually manipulated by Matron Vespera. While Aurelius genuinely believed that Citadel Sorrow was a sanitarium intended to 'cure' afflicted Aether-Weavers, Vespera used the fortress as a processing abattoir for Hollowed Thrall production.

## Fate at the Wellspring
During the naval expedition toward the Isle of the Forgotten Pantheon, Aurelius recognized the catastrophic deceptions of his father's regime. Depending on the choices of the Archon-Ascendants, Aurelius was either slain in ideological conflict or conceded his claim to the throne, realizing true peace required dismantling the Concordat.
"""
    ),
    (
        "character_malady",
        "Morrigan the Half-Fiend",
        """# Morrigan the Half-Fiend: Lady of the Timber-Revenant

## Enigmatic Lineage
Morrigan is an enigmatic half-human, half-demon navigator whose origins trace to pacts sealed in the arch-demonic realm of Nemesis. One side of her face is adorned with elaborate golden filigree, concealing horrific demonic pact-scars.

## Salvage of The Timber-Revenant
When the prison ship *Merryweather* foundered, Morrigan rescued a cohort of potential Archon-Ascendants. Leading them through Citadel Sorrow, she directed the capture of *The Timber-Revenant* — a sentient war-galleon crafted from enchanted living ancestral wood.

## Motives and Cost
Morrigan acts as tactical mentor, planar navigator, and high-risk benefactor. Every major inter-dimensional rift transit she initiates exacts a severe metabolic toll, forcing her to expend portions of her remaining lifespan to pierce the boundaries of the Liminal Necropolis.
"""
    ),
    (
        "character_fane",
        "Kaelen the Ossuary",
        """# Kaelen the Ossuary: The Entombed Scholar

## The Primordial Past
Kaelen the Ossuary was a pre-eminent natural philosopher among the Primordial Titans millennia before recorded history. His unquenchable curiosity led to the discovery of the Veil separating reality from the Abyssal Rift, as well as the latent power of pure Aether-Prana.

## Betrayal and Millennial Imprisonment
When the greedy tribal lords who would become the Septem Pantheon stole his research, they banished Kaelen's entire civilization into the freezing darkness of the Abyssal Rift and sealed Kaelen inside an enchanted stone sarcophagus beneath the earth.

## The Shapeshifter Mask
Awakening in modern Aethelgard as a living skeleton, Kaelen constructed the *Mask of the Shapeshifter* using fresh cadaverous flesh. This artifact allows him to walk unrecognized among mortals while searching for the remnants of his lost wife and daughter.
"""
    ),
    (
        "character_lohse",
        "Lyrissa the Chime",
        """# Lyrissa the Chime: The Besieged Minstrel

## The Resonant Soul
Lyrissa originated as a celebrated traveling bard and playwright throughout Gallow Shore. Her psyche possesses a unique empathic resonance that acts as an open amphitheater for disembodied spirits, wanderers, and cosmic consciousnesses.

## Possession by Lord Malphas
Her luminous aura attracted Lord Malphas, an archdemon of catastrophic malice. Infesting her mind, Malphas gradually seized control of her motor functions, whispering murderous impulses and driving her to violent blackouts during musical performances.

## The Candle-Lit Sanctum
To liberate herself, Lyrissa traveled with fellow Archon-Ascendants to Solaris Metropolis, venturing into Malphas's infernal mind-realm where millions of flickering candles represented souls bound to the demon's eternal torment.
"""
    ),
    (
        "character_ifan_ben_mezd",
        "Theron Blackthorn",
        """# Theron Blackthorn: The Disillusioned Crusader

## Loyalty to the Sovereign Archon
Theron was once the most decorated paladin and adoptive ward of Archon Valerius. Revered as the 'Silver Wolf,' he served as principal diplomatic liaison between the central human kingdom and the forest elves.

## The Great Betrayal
During the Pan-Continental War, Valerius dispatched Theron to negotiate a cease-fire with the Elven High Council. Unbeknownst to Theron, Valerius utilized his diplomatic caravan as a cover to detonate barrels of Necro-Miasma, slaughtering the entire elven population while Theron barely survived.

## Ironfang Mercenary
Shattered by the betrayal, Theron abandoned his oaths, took the mantle of an outlaw marksman, and joined the Ironfang Syndicate. He was hired on a clandestine contract to assassinate Hierarch Aurelius at Citadel Sorrow before finding a new destiny among the Archon-Ascendants.
"""
    ),
    (
        "character_sebille",
        "Nyx the Scarred Needle",
        """# Nyx the Scarred Needle: The Vengeful Assassin

## Slavery and the Needle
Nyx was an elven noble scion abducted into brutal servitude by the Master — a shadowy spymaster of the Draconic Imperium. For decades, a magical silver needle was embedded beneath her skin, subjecting her mind to absolute telepathic control and forcing her to assassinate rival merchants and magistrates.

## The Path of Blood
Breaking free of the mental subjugation, Nyx carved the names of every collaborator onto her own limbs. Wielding an assassin's shiv and dark flesh-eating magic, she stalked the slave routes of Gallow Shore, methodically executing the slave masters until confronting the Master himself on the Isle of the Forgotten Pantheon.
"""
    ),
    (
        "character_red_prince",
        "Crimson Scion Ignis",
        """# Crimson Scion Ignis: The Exiled Draconic Prince

## Aristocracy and Downfall
Crimson Scion Ignis was the designated heir to the Sun Throne within the Draconic Imperium. Blessed with unique scarlet scales and supreme tactical acumen, his reign seemed pre-ordained until his nocturnal trysts with an Abyssal dream-demon were exposed to the High Court.

## The Imperial Prophecy
Stripped of rank and banished into exile, Ignis retained supreme arrogance. Ancient murals foretold that a red dragon-prince would unite his species with the lost crimson dragons, restoring draconic dominion across Aethelgard through an alliance with the dream-seer Sadha.
"""
    ),
    (
        "character_beast",
        "Torgar Ironbeard",
        """# Torgar Ironbeard: The Rebel Privateer

## Royal Heritage and Rebellion
Torgar Ironbeard is a cousin to Queen Justinia of the subterranean Dwarven Empire. Witnessing the Queen fall under the genocidal influence of corrupt advisors who sought to weaponize Necro-Miasma against surface cities, Torgar led a desperate mutiny.

## Corsair of the Outer Seas
Exiled to the islands of Gallow Shore, Torgar assembled a fleet of free-thinking corsairs and miners. His primary operational objective was intercepting Concordat supply convoys carrying doomsday weapons into the sewers of Solaris Metropolis.
"""
    ),
    (
        "character_tarquin",
        "Balthazar the Reliquary",
        """# Balthazar the Reliquary: Necromantic Artisan

## Dual Loyalties
Balthazar is an eccentric polymath, forensic thaumaturge, and master necromancer. Formerly employed by Matron Vespera to decipher ancient Titan technology, Balthazar secretly defected to *The Timber-Revenant* to pursue his own academic obsessions.

## Forging The Ruin-Glaive
Balthazar's greatest intellectual achievement was recovering and re-assembling the shattered pieces of *The Ruin-Glaive* — a mythical anti-deity polearm capable of severing the divine immortality of gods and Archon-Ascendants alike.
"""
    ),
    (
        "character_gareth",
        "Commander Ronen",
        """# Commander Ronen: The Righteous Paladin

## Leader of The Emancipators
Commander Ronen was a high-ranking paladin who renounced his rank upon discovering the horrors of the Hollowed Thrall penal camps. Fleeing into the dense swamps surrounding Citadel Sorrow, he organized *The Emancipators* — a resistance coalition safeguarding fugitive Aether-Weavers.

## Moral Dilemma
Throughout the campaign across Gallow Shore, Ronen confronted the brutal slaughter of his elderly parents by Concordat inquisitors. The trauma pushed his pious convictions to the brink of bloodthirsty fanatical vengeance.
"""
    ),
    (
        "character_braccus_rex",
        "Dread-Emperor Morvan",
        """# Dread-Emperor Morvan: The Ancient Tyrant of Prana

## Reign of Terror
Centuries prior to modern history, Dread-Emperor Morvan ruled Aethelgard through absolute sadism and tyrannical mastery of blood-infused Aether-Prana. He constructed horrific torture citadels, cursed entire legions into eternal stone, and invented soul-draining constructs.

## Resurrection
Overthrown and executed by an alliance of heroes, his decayed essence was secretly resurrected by Matron Vespera to act as an unthinking enforcer, though his cunning spirit bided its time to summon the Nether-Monarch directly into the heart of Solaris Metropolis.
"""
    ),
    (
        "character_adramahlihk",
        "Lord Malphas: The Crimson Chirurgeon",
        """# Lord Malphas: The Archdemon of Solaris

## The Hospital of Shadows
Lord Malphas established his mortal facade as 'The Crimson Chirurgeon' within a fortified mansion in the noble quarter of Solaris Metropolis. Posing as a philanthropic healer treating plague victims, he covertly implanted demonic blood-seeds into patients and civic leaders.

## Planar Ambition
Malphas sought to usurp the power vacuum left by the declining Septem Pantheon. By harvesting the soul of the minstrel Lyrissa and binding high-ranking Concordat officials, he aimed to conquer both Aethelgard and the Nether-Monarch's realm.
"""
    ),
    (
        "character_lord_kemm",
        "Marshal Victor Vane",
        """# Marshal Victor Vane: The Fallen Commander

## Defender of Solaris Metropolis
Marshal Victor Vane was universally hailed as the unyielding bastion of the Lumen Paladins. Stationed in Solaris Metropolis, he oversaw municipal security and defended civilian refugees fleeing the Nether-Abomination incursions.

## Blood-Bound Treachery
Beneath his shining armor and devotional statues, Vane had succumbed to despair following the apparent death of Archon Valerius. He took the blasphemous oath of the Blood-Bound, pledging his blade and soul to the Nether-Monarch in exchange for dark immortality.
"""
    ),
    (
        "character_arhu",
        "Arch-Mage Corvus: The Shapeshifting Scholar",
        """# Arch-Mage Corvus: The Feline Sorcerer

## Companion of the Sovereign Archon
Arch-Mage Corvus was the personal magical advisor and closest confidant of Archon Valerius for over a century. Possessing rare animagi abilities, he frequently assumed the form of an agile domestic cat to eavesdrop on seditious conspiracies.

## Imprisonment in the Catacombs
Knowing the truth behind Valerius's survival and the deployment of Necro-Miasma, Corvus was captured and tortured by Marshal Victor Vane beneath the palace vaults, his life-essence extracted to power the barrier guarding the Wellspring of Ascension.
"""
    ),
    (
        "concept_source_and_sourcerers",
        "Aether-Prana and Aether-Weavers",
        """# Aether-Prana: The Primordial Fabric of Creation

## Nature of Prana
Aether-Prana is the purest elemental energy in existence, the fundamental life-force that forms the soul and anchors physical matter in Aethelgard. Mortals born with natural affinity to manipulate this energy are designated **Aether-Weavers**.

## The Beacon Effect
Whenever an Aether-Weaver channels substantial amounts of Aether-Prana, the metaphysical fabric of reality vibrates. This vibration acts as a blinding beacon across the dimensions, drawing ravenous Nether-Abominations out of the Abyssal Rift into the mortal realm.
"""
    ),
    (
        "concept_void_and_voidwoken",
        "The Abyssal Rift and Nether-Abominations",
        """# The Abyssal Rift: Cosmic Hunger and Nether-Beasts

## The Primordial Rift
The Abyssal Rift is an entropic, lightless anti-dimension existing beyond the cosmic Veil. It was created when the Septem Pantheon violently expelled the ancient Primordial Titans, leaving them to starve in perpetual agony.

## Nether-Abominations
Deprived of warmth and prana, the inhabitants of the Rift mutated into hideous insectoid, crystalline, and avian horrors known as Nether-Abominations. Guided by the telepathic will of the Nether-Monarch, they assault Aethelgard seeking to reclaim their stolen ancestral energy.
"""
    ),
    (
        "concept_godwoken",
        "Archon-Ascendants: Candidates of Divinity",
        """# Archon-Ascendants: The Chosen Vessels

## Divine Selection
Following the exhaustion of the Septem Pantheon, each of the seven gods chose specific mortal champions gifted with exceptional Aether-Prana. These individuals are designated **Archon-Ascendants**.

## The Great Crucible
Only one Archon-Ascendant can absorb the collective ambient energy residing within the Wellspring of Ascension to become the next Sovereign Archon. The competition forces former allies into philosophical and martial confrontations atop the Isle of the Forgotten Pantheon.
"""
    ),
    (
        "concept_silent_monks",
        "Hollowed Thralls and Essence-Excision",
        """# Hollowed Thralls: The Lobotomized Sentinels

## The Excision Process
Hollowed Thralls are produced through the application of Excision Scepters upon restrained Aether-Weavers. The ritual violently rips the soul and prana matrix from the victim's body.

## Biological State
The resulting thralls retain rudimentary motor skills and muscle memory but possess zero emotions, identity, or independent thought. Blindfolded and armed with heavy halberds, they serve the Concordat as tirelessly obedient garrison troops immune to psychological terror.
"""
    ),
    (
        "artifact_source_collar",
        "Dampener Shackles: Inquisitorial Restraints",
        """# Dampener Shackles: Anti-Weaver Restraints

## Engineering and Metallurgy
Dampener Shackles are heavy metallic torque rings forged from cursed iron and resonance-deadening minerals. Locked around the neck of suspected Aether-Weavers, they suppress all neurological connection to Aether-Prana.

## Shock Mechanism
Attempting to channel spellcraft while wearing a Dampener Shackle triggers an agonizing electrostatic feedback loop directly into the wearer's carotid arteries, inducing paralysis and preventing any magical manifestation.
"""
    ),
    (
        "artifact_deathfog",
        "Necro-Miasma: The Doomsday Contagion",
        """# Necro-Miasma: Alchemical Extinction Agent

## Physical Properties
Necro-Miasma is a dense, luminescent crimson-green vapor engineered in supreme secrecy by dwarven alchemists and Concordat technocrats. 

## Lethality
Upon contact with living organic matter, Necro-Miasma immediately liquefies lungs, flesh, and nervous systems within two seconds. It affects all living species regardless of physical armor or magical wards. Crucially, it has no effect on skeletal undead, making it the ultimate weapon for beings like Kaelen the Ossuary.
"""
    ),
    (
        "artifact_lady_vengeance",
        "The Timber-Revenant: Sentient War-Galleon",
        """# The Timber-Revenant: The Living Vessel

## Ancestral Wood
*The Timber-Revenant* is an ancient naval vessel constructed entirely from living Ancestral Wood harvested from sacred elven grove-mothers. The ship possesses an autonomous beating wooden heart and a conscious figurehead that communicates in archaic song.

## Dimensional Travel
Under the command of Morrigan the Half-Fiend, the ship was awakened using a stolen songbook. Equipped with magical sail-canvas, it can sail not only across open oceans, but directly across the ethereal waters of the Liminal Necropolis.
"""
    ),
    (
        "artifact_anathema",
        "The Ruin-Glaive: The God-Slaying Weapon",
        """# The Ruin-Glaive: The Deicidal Blade

## Ancient Origin
Forged during the primordial civil wars of the Titans, *The Ruin-Glaive* was engineered with a singularly horrific enchantment: to break through the divine shielding of ascended deities.

## Fragility and Assembly
The weapon was shattered into two distinct segments hidden across Gallow Shore. Once re-forged by Balthazar the Reliquary, the weapon delivers apocalyptic damage capable of permanently sundering the physical shell of Archon Valerius, though the metal is so brittle it disintegrates after intense combat.
"""
    ),
    (
        "ability_source_vampirism",
        "Prana-Siphoning: The Forbidden Art",
        """# Prana-Siphoning: Soul Ingestion

## Mechanics
Prana-Siphoning is a taboo theurgic ritual taught to Archon-Ascendants within the Liminal Necropolis. By focusing their spiritual vision, the practitioner perceives the lingering ghosts of deceased sentient beings.

## Consumption of Souls
When activated, the practitioner forcefully tears the ethereal soul apart, devouring its residual Aether-Prana to replenish their own magical reserves. This act completely annihilates the target soul, denying them an afterlife.
"""
    ),
    (
        "faction_divine_order",
        "The Inquisitorial Concordat: Ruling Theocracy",
        """# The Inquisitorial Concordat: The Imperial Theocracy

## Ideology and Mandate
The Inquisitorial Concordat is the dominant military and religious power across the core human territories of Aethelgard. Established by Archon Valerius, its stated mandate is the complete cleansing of unconstrained magic to safeguard the world from demonic ruin.

## Administrative Hierarchy
- **Matron Vespera the Cleaver:** Supreme Commander and Architect of Policy.
- **Hierarch Aurelius:** High Priest and Civil Governor.
- **Justiciars:** Field inquisitors, houndsmen, and executioners stationed in regional citadels.
- **Hollowed Thralls:** Lobotomized shock troops utilized for heavy labor and suppression.
"""
    ),
    (
        "faction_paladins",
        "Lumen Paladins: The Chivalric Guard",
        """# Lumen Paladins: The Traditionalist Vanguard

## Friction with the Inquisitorial Concordat
The Lumen Paladins represent the noble martial lineage of the original Solar Empire. Unlike the ruthless Justiciars of the Concordat, the Paladins historically adhered to honorable codes of open warfare and civilian protection.

## Division in Solaris Metropolis
Under the command of Marshal Victor Vane, open armed skirmishes broke out between the Paladins and Justiciars throughout the streets of Solaris Metropolis as the atrocities of Citadel Sorrow became public knowledge.
"""
    ),
    (
        "faction_black_ring",
        "The Obsidian Circle: Cult of the Nether-Monarch",
        """# The Obsidian Circle: Heralds of the Void

## Worship of the Nether-Monarch
The Obsidian Circle is an apocalyptic cult comprised of renegade warlocks, necromancers, and shapeshifters who have sworn allegiance to the Nether-Monarch. They seek the total collapse of the Veil and the extinction of the Septem Pantheon.

## Military Threat
Headquartered around the volcanic bluffs of the Tar-Trenches and Sanguine-Eclipse Atoll, they utilize dark blood-altars to summon Nether-Abominations and reanimate legions of rotting dead against Concordat positions.
"""
    ),
    (
        "faction_seekerrs",
        "The Emancipators: Freedom Underground",
        """# The Emancipators: Guerrillas of the Swamps

## Refuge in the Hollow Marshes
Operating from hidden sanctuary ruins deep within the swamps of Citadel Sorrow, *The Emancipators* are a coalition of fugitive Aether-Weavers, deserter soldiers, and elven survivors led by Commander Ronen.

## Mission
Their operational focus is conducting lightning ambushes against Justiciar prison convoys, removing Dampener Shackles using clandestine lockpicking apparatus, and assisting persecuted mages in escaping across the sea.
"""
    ),
    (
        "faction_lone_wolves",
        "The Ironfang Syndicate: Mercenary Cartel",
        """# The Ironfang Syndicate: Blood for Gold

## Code of the Contract
The Ironfang Syndicate is the premier criminal mercenary syndicate in Aethelgard. Operating under the brutal guidance of Kragor the Beastmaster from a fortified sawmill in Gallow Shore, their members live by the creed: 'A wolf without a pack is a killer without a master.'

## High-Profile Bounties
The Syndicate accepted an astronomical gold contract from the Obsidian Circle to systematically liquidate all potential Archon-Ascendants before they could reach the Isle of the Forgotten Pantheon.
"""
    ),
    (
        "location_fort_joy",
        "Citadel Sorrow: The Island Penal Colony",
        """# Citadel Sorrow: The Quarantine Enclave

## Geography and Ruins
Citadel Sorrow is an ancient coastal fortress situated upon a windswept island in the Southern Oceans. Surrounding the fortress are toxic salt marshes, ancient ruins, and lethal shrieker totems powered by Excised souls.

## Administrative Role
Marketed by Concordat propaganda as a luxurious sanctuary for Aether-Weavers to receive peaceful treatment, it functioned in reality as a brutal open-air concentration camp where inmates were stripped of dignity, shackled, and scheduled for lobotomy.
"""
    ),
    (
        "location_reapers_coast",
        "Gallow Shore and Mistport: The Mainland Hub",
        """# Gallow Shore: The Fractured Mainland

## Economic Heart
Gallow Shore is a sprawling coastal breadbasket region featuring expansive farmsteads, the bustling fishing harbor of Mistport, and the sulfurous industrial zone known as the Tar-Trenches.

## Looming Anarchy
With the Concordat withdrawing troops to fortify the capital city of Solaris, Gallow Shore rapidly degenerated into lawlessness, plagued by highwaymen, rogue demons, and deep-sea Nether-Abominations emerging from fishing nets.
"""
    ),
    (
        "location_bloodmoon_island",
        "Sanguine-Eclipse Atoll: The Demonic Cradle",
        """# Sanguine-Eclipse Atoll: The Cursed Sanctuary

## The Blighted Red Soil
Sanguine-Eclipse Atoll is an isolated island completely separated from the mainland by a sea of toxic Necro-Miasma. Its crimson-colored soil is saturated with millennia of demonic blood sacrifices.

## The Corrupted Ancestor Tree
At the center of the atoll stands an ancient elven Ancestor Tree, possessed by archdemons and guarded by mutated cultists of the Obsidian Circle. Beneath the island lie forgotten Titan archives holding the secrets of the Covenant-Cleaver.
"""
    ),
    (
        "location_nameless_isle",
        "Isle of the Forgotten Pantheon: The Proving Grounds",
        """# Isle of the Forgotten Pantheon: Sacred Convergence

## Geography of the Seven Temples
The Isle of the Forgotten Pantheon is a volcanic, shifting landmass containing seven monumental temples, each dedicated to one of the deities of the Septem Pantheon.

## The Wellspring of Ascension
Deep inside the heart of the island's central volcano lies the Council Chamber. Here, the raw, unfiltered prana of the universe collects in a glowing lake, awaiting the arrival of the rightful Archon-Ascendant.
"""
    ),
    (
        "location_arx",
        "Solaris Metropolis: The City of White Spires",
        """# Solaris Metropolis: The Grand Capital

## Architectural Splendor
Solaris Metropolis is the seat of the Inquisitorial Concordat and the ancestral home of human high civilization. Renowned for its soaring marble aqueducts, massive defensive bastions, and the Cathedral of Archon Valerius.

## The Refugee Influx
During the twilight of the campaign, hundreds of thousands of refugees inundated the city outer wards, fleeing the horrors of the countryside, while dark cultists planted bombs of Necro-Miasma within the subterranean sewers.
"""
    ),
    (
        "event_purge_of_the_elves",
        "The Ash-Blight Holocaust: The Death of a Nation",
        """# The Ash-Blight Holocaust: The Sunder of the Elven Wood

## The Tactical Rationale
When Nether-Abominations launched their first coordinated offensive through elven border territories, Archon Valerius concluded that conventional military defense was impossible.

## The Chemical Strike
Utilizing dwarven transport machines, Valerius detonated stockpiles of Necro-Miasma across the heartlands. The toxic fog wiped out millions of elves in a matter of hours, ending their ancestral kingdom, leaving surviving refugees scattered as second-class citizens across the world.
"""
    ),
    (
        "event_council_of_seven",
        "The Conclave of Ascension: Battle for the Throne",
        """# The Conclave of Ascension: The Trial of the Gods

## The Summit of Champions
When the surviving Archon-Ascendants gathered within the subterranean wellspring beneath the Isle of the Forgotten Pantheon, each of the Septem gods demanded that their chosen champion betray their companions and absorb the wellspring alone.

## The Interruption
Before the ascension ritual could conclude, Matron Vespera and Dread-Emperor Morvan breached the chamber utilizing a mechanical titan engine, draining the Wellspring of its energy and shattering the Isle in a catastrophic tectonic detonation.
"""
    )
]


def apply_terms_mapping(text: str, mapping: Dict[str, str]) -> str:
    """
    Заменяет исходные термины на вымышленные.
    Сортирует ключи по убыванию длины для предотвращения частичных наложений.
    """
    sorted_keys = sorted(mapping.keys(), key=len, reverse=True)
    for key in sorted_keys:
        replacement = mapping[key]
        pattern = r"\b" + re.escape(key) + r"\b"
        text = re.sub(pattern, replacement, text)
    return text


def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    kb_dir = os.path.join(root_dir, "knowledge_base")
    terms_file = os.path.join(root_dir, "terms_map.json")

    print("=== Генерация синтетической базы знаний (Divinity: Original Sin 2) ===")
    print(f"Целевая директория: {kb_dir}")
    print(f"Количество сущностей: {len(DOS2_ARTICLES)}")

    # Очищаем старую папку knowledge_base
    if os.path.exists(kb_dir):
        shutil.rmtree(kb_dir)
    os.makedirs(kb_dir, exist_ok=True)

    # 1. Сохранение словаря замен terms_map.json
    with open(terms_file, "w", encoding="utf-8") as f:
        json.dump(TERMS_MAP, f, ensure_ascii=False, indent=2)
    print(f"Словарь замен сохранен: {terms_file} ({len(TERMS_MAP)} пар терминов)")

    # 2. Обработка и сохранение статей базы знаний
    saved_count = 0
    for slug, raw_title, raw_content in DOS2_ARTICLES:
        obfuscated_title = apply_terms_mapping(raw_title, TERMS_MAP)
        obfuscated_content = apply_terms_mapping(raw_content, TERMS_MAP)

        safe_slug = re.sub(r"[^a-zA-Z0-9_]", "_", slug)
        filename = f"{safe_slug}.md"
        filepath = os.path.join(kb_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(obfuscated_content.strip() + "\n")
        saved_count += 1

    print(f"Успешно сохранено {saved_count} уникальных документов в {kb_dir}")


if __name__ == "__main__":
    main()
