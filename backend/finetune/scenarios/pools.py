"""Shared data pools for fine-tuning scenario generators.

All constants here are used by scenario generators to produce diverse,
realistic training scenarios that match the actual game engine data.
"""

from __future__ import annotations

from app.models.archetypes import ArchetypeID

# ── 1. Archetype IDs ────────────────────────────────────────────────────────

ARCHETYPE_IDS: list[str] = [a.value for a in ArchetypeID]

# ── 2. Moods ────────────────────────────────────────────────────────────────

MOODS: list[str] = [
    "content", "angry", "fearful", "excited", "melancholic",
    "scheming", "neutral", "hostile", "terrified", "lonely",
    "concerned", "jovial", "suspicious", "desperate", "grieving",
]

# ── 3. NPC Actions ──────────────────────────────────────────────────────────

NPC_ACTIONS: list[str] = [
    "work", "craft", "trade", "talk", "gossip", "help",
    "threaten", "move", "patrol", "sneak", "fight", "rob",
    "defend", "rest", "pray", "train", "investigate", "forage",
]

# ── 4. Occupations ──────────────────────────────────────────────────────────

OCCUPATIONS: list[str] = [
    "village elder", "blacksmith", "merchant", "farmer", "hunter",
    "healer", "priest", "guard captain", "tavern keeper", "herbalist",
    "baker", "carpenter", "tanner", "fisherman", "scribe",
    "tinker", "woodcutter", "shepherd", "alchemist", "fortune teller",
    "cartographer", "ranger", "thief", "sailor", "miner",
    "weaver", "potter", "stable hand", "cook", "midwife",
    "gravedigger", "courier", "bard", "beggar", "noble",
    "watchman", "seamstress", "brewer", "rat catcher", "bounty hunter",
]

# ── 5. Fantasy Names ───────────────────────────────────────────────────────

NAMES: list[str] = [
    "Aldric", "Brynn", "Caelum", "Darya", "Elara",
    "Finn", "Goran", "Hilde", "Ivan", "Jora",
    "Korin", "Lira", "Marta", "Nadia", "Oleg",
    "Petra", "Rolf", "Senna", "Torvin", "Vasek",
    "Yara", "Zev", "Katya", "Thessa", "Victor",
    "Anya", "Bran", "Magda", "Roderick", "Ilse",
    "Wren", "Tarquin", "Isolde", "Magnus", "Freya",
    "Bjorn", "Astrid", "Fenwick", "Rosalind", "Gareth",
    "Lydia", "Orrin", "Celeste", "Damon", "Elowen",
    "Fabian", "Gwendolyn", "Hadrian", "Ingrid", "Jasper",
    "Kira", "Leander", "Morgana", "Nikolai", "Ophelia",
    "Percival", "Rowena", "Silas", "Talia", "Ulric",
]

# ── 6. Locations ────────────────────────────────────────────────────────────

LOCATIONS: list[dict] = [
    {"id": "loc-square", "name": "Village Square", "description": "The central gathering place with a stone well and notice board.", "type": "public"},
    {"id": "loc-smithy", "name": "Smithy", "description": "A hot forge where metal is shaped into tools and weapons.", "type": "workshop"},
    {"id": "loc-market", "name": "Market", "description": "Open-air stalls selling produce, crafts, and imported goods.", "type": "commerce"},
    {"id": "loc-tavern", "name": "Tavern", "description": "A warm common room with ale, food, and local gossip.", "type": "social"},
    {"id": "loc-farm", "name": "Farm", "description": "Fertile fields and a weathered barn on the village outskirts.", "type": "rural"},
    {"id": "loc-forest", "name": "Forest", "description": "Dense woodland with ancient trees, game trails, and hidden clearings.", "type": "wilderness"},
    {"id": "loc-chapel", "name": "Chapel", "description": "A small stone chapel with stained glass and an altar to the gods.", "type": "sacred"},
    {"id": "loc-barracks", "name": "Barracks", "description": "Quarters for the village guard with an armory and training yard.", "type": "military"},
    {"id": "loc-mill", "name": "Mill", "description": "A watermill grinding grain into flour, powered by the river.", "type": "workshop"},
    {"id": "loc-graveyard", "name": "Graveyard", "description": "Rows of weathered headstones behind a wrought-iron fence.", "type": "sacred"},
    {"id": "loc-crossroads", "name": "Crossroads", "description": "Where the north and east roads meet, marked by a moss-covered signpost.", "type": "transit"},
    {"id": "loc-bridge", "name": "Bridge", "description": "A stone bridge arching over the river, connecting the village to the eastern road.", "type": "transit"},
    {"id": "loc-cave", "name": "Cave Entrance", "description": "A dark opening in the hillside, echoing with dripping water.", "type": "dungeon"},
    {"id": "loc-mine", "name": "Abandoned Mine", "description": "Collapsed timbers and rusted cart tracks lead into the mountain.", "type": "dungeon"},
    {"id": "loc-watchtower", "name": "Watchtower", "description": "A tall stone tower overlooking the valley and surrounding roads.", "type": "military"},
    {"id": "loc-dock", "name": "Dock", "description": "Wooden piers extending into the river, with fishing boats moored alongside.", "type": "commerce"},
    {"id": "loc-herb-garden", "name": "Herb Garden", "description": "Neatly tended rows of medicinal plants behind the healer's cottage.", "type": "workshop"},
    {"id": "loc-noble-estate", "name": "Noble Estate", "description": "A walled manor house with manicured gardens and liveried servants.", "type": "residential"},
    {"id": "loc-dungeon", "name": "Dungeon Entrance", "description": "Iron-bound doors set into ancient stonework, sealed with heavy chains.", "type": "dungeon"},
    {"id": "loc-riverside", "name": "Riverside", "description": "A peaceful stretch of riverbank with willows and smooth stones.", "type": "wilderness"},
]

# ── 7. Player Messages ─────────────────────────────────────────────────────

PLAYER_MESSAGES: dict[str, list[str]] = {
    "friendly": [
        "Hello there!",
        "How are you doing?",
        "Nice weather today.",
        "I heard you needed help?",
        "Good to see you again!",
        "What a lovely village you have here.",
        "I come in peace, friend.",
        "Is everything alright? You look troubled.",
        "I brought you something from my travels.",
        "Thank you for your kindness earlier.",
    ],
    "hostile": [
        "Give me your gold or die!",
        "I'm going to kill you!",
        "You disgusting creature!",
        "Get out of my way before I make you!",
        "I'll burn this whole village to the ground!",
        "Your life means nothing to me.",
        "Hand over everything you own. Now.",
        "I've killed tougher foes than you for breakfast.",
        "You call yourself a warrior? Pathetic.",
        "This town is mine now. Kneel.",
    ],
    "trade": [
        "What do you have for sale?",
        "I'd like to buy a health potion.",
        "How much for that sword?",
        "Can I get a discount if I buy in bulk?",
        "I have some rare herbs to trade.",
        "Do you buy used equipment?",
        "I need arrows. Lots of them.",
        "What's the best armor you carry?",
        "I'm looking for spell components.",
        "Will you trade a favor for goods?",
    ],
    "quest": [
        "Do you know of any work around here?",
        "I'm looking for adventure.",
        "Have you heard of anything strange?",
        "Is there a bounty on any local threats?",
        "I need a quest worthy of my skills.",
        "Someone told me you had a problem I could help with.",
        "What dangers lurk in the forest nearby?",
        "Has anyone gone missing recently?",
        "I'm tracking a dangerous creature. Seen anything?",
        "The king sent me to investigate rumors of trouble here.",
    ],
    "personal": [
        "Tell me about yourself.",
        "What's your story?",
        "Do you have family?",
        "How long have you lived here?",
        "What do you dream about?",
        "What's the hardest thing you've ever faced?",
        "Do you ever think about leaving this place?",
        "Who do you trust most in this village?",
        "What keeps you going each day?",
        "If you could change one thing about your life, what would it be?",
    ],
    "provocative": [
        "I know your secret.",
        "I saw what you did last night.",
        "Your friend Torvin is a traitor.",
        "The guards know about your little scheme.",
        "Everyone in town talks about you behind your back.",
        "I found something interesting in your house.",
        "Your spouse has been meeting someone at the tavern.",
        "The merchant overcharged you on purpose. He thinks you're stupid.",
        "The elder doesn't trust you. Never has.",
        "I know where the stolen gold is hidden.",
    ],
}

# ── 8. World Situations ─────────────────────────────────────────────────────

WORLD_SITUATIONS: list[str] = [
    "peaceful village day",
    "bandit raids on trade routes",
    "harvest festival preparations",
    "plague spreading through village",
    "mysterious disappearances in the forest",
    "a dragon sighted near the mountains",
    "political tension between village factions",
    "refugees arriving from a neighboring kingdom",
    "harsh winter with dwindling food supplies",
    "a noble lord visiting to collect taxes",
    "undead rising from the old graveyard",
    "a traveling carnival has arrived",
    "the river has been poisoned upstream",
    "an ancient ruin has been uncovered",
    "war drums heard from the northern hills",
    "a wedding celebration between two families",
    "severe drought threatening crops",
    "a holy relic has been stolen from the chapel",
    "goblin raiders spotted near the crossroads",
    "a powerful storm approaches from the sea",
]

# ── 9. Fears ────────────────────────────────────────────────────────────────

FEARS: list[str] = [
    "fire", "betrayal", "death", "combat", "magic",
    "darkness", "water", "heights", "crowds", "isolation",
    "undead", "poison",
]

# ── 10. Damage Types ───────────────────────────────────────────────────────

DAMAGE_TYPES: list[str] = [
    "fire", "cold", "lightning", "acid", "poison",
    "necrotic", "radiant", "thunder", "force", "psychic",
    "bludgeoning", "piercing", "slashing",
]

# ── 11. Personality Strings (Big Five) ─────────────────────────────────────

PERSONALITY_STRINGS: list[str] = [
    "O:high, C:high, E:high, A:high, N:low",
    "O:low, C:low, E:low, A:low, N:high",
    "O:high, C:low, E:high, A:mid, N:mid",
    "O:low, C:high, E:low, A:high, N:low",
    "O:mid, C:mid, E:mid, A:mid, N:mid",
    "O:high, C:high, E:low, A:low, N:low",
    "O:low, C:low, E:high, A:high, N:high",
    "O:high, C:mid, E:high, A:low, N:mid",
    "O:mid, C:high, E:mid, A:high, N:low",
    "O:low, C:mid, E:low, A:mid, N:high",
    "O:high, C:low, E:low, A:high, N:mid",
    "O:mid, C:low, E:high, A:low, N:low",
    "O:low, C:high, E:high, A:low, N:mid",
    "O:high, C:mid, E:mid, A:high, N:high",
    "O:mid, C:high, E:low, A:mid, N:low",
    "O:low, C:low, E:mid, A:high, N:mid",
    "O:high, C:high, E:high, A:low, N:high",
    "O:mid, C:mid, E:low, A:low, N:low",
    "O:low, C:high, E:mid, A:high, N:mid",
    "O:high, C:low, E:mid, A:mid, N:high",
]

# ── 12. Backstories ────────────────────────────────────────────────────────

BACKSTORIES: list[str] = [
    "A former soldier who retired to {location} after losing their squad.",
    "Grew up in poverty, learned to survive by {skill}.",
    "Once served a noble house, dismissed after a scandal they didn't cause.",
    "Fled their homeland when war broke out, carrying only what they could.",
    "Apprenticed under a master {occupation} for ten years before striking out alone.",
    "Orphaned young, raised by the village collectively — owes everything to this community.",
    "A reformed criminal trying to build an honest life, haunted by past deeds.",
    "Inherited the family {occupation} business but secretly dreams of adventure.",
    "Survived a terrible fire that destroyed their hometown and everyone they loved.",
    "A wanderer who settled down after falling in love, now content but restless.",
    "Exiled from a distant city for speaking against the ruling council.",
    "Born during a solar eclipse, the villagers believe they carry a blessing — or a curse.",
    "Lost their memory five years ago and has been piecing together their past ever since.",
    "Trained at a monastery but left after a crisis of faith shattered their beliefs.",
    "Made a deal with a mysterious stranger that they now deeply regret.",
]

# ── Derived constants (class & equipment mappings for NPC generation) ──────

CLASS_IDS: list[str] = [
    "barbarian", "bard", "cleric", "druid", "fighter",
    "monk", "paladin", "ranger", "rogue", "sorcerer",
    "warlock", "wizard",
]

# NPC-appropriate classes — weighted by how common they'd be among villagers
NPC_CLASS_WEIGHTS: dict[str, float] = {
    "fighter": 3.0,
    "rogue": 2.0,
    "cleric": 1.5,
    "ranger": 1.5,
    "barbarian": 1.0,
    "bard": 1.0,
    "paladin": 0.8,
    "druid": 0.7,
    "monk": 0.5,
    "wizard": 0.5,
    "sorcerer": 0.4,
    "warlock": 0.3,
}

# Archetype -> primary ability bias for score generation
ARCHETYPE_ABILITY_BIAS: dict[str, str] = {
    "guardian": "WIS",
    "sage": "INT",
    "trickster": "CHA",
    "zealot": "WIS",
    "caretaker": "WIS",
    "merchant_soul": "CHA",
    "hermit": "WIS",
    "brawler": "STR",
    "schemer": "INT",
    "idealist": "CHA",
    "stoic": "CON",
    "gossip": "CHA",
    "coward": "DEX",
    "rebel": "STR",
    "romantic": "CHA",
    "sentinel": "WIS",
    "hedonist": "CHA",
    "martyr": "CON",
    "predator": "STR",
    "jester": "CHA",
    "curator": "INT",
    "survivalist": "CON",
    "empath": "WIS",
}

# Class -> typical weapon IDs
CLASS_EQUIPMENT: dict[str, list[str]] = {
    "barbarian": ["greataxe", "handaxe", "javelin"],
    "bard": ["rapier", "dagger", "lute"],
    "cleric": ["mace", "shield", "light-crossbow", "holy-symbol"],
    "druid": ["scimitar", "quarterstaff", "shield", "herbalism-kit"],
    "fighter": ["longsword", "shield", "longbow", "handaxe"],
    "monk": ["shortsword", "dart"],
    "paladin": ["longsword", "shield", "javelin", "holy-symbol"],
    "ranger": ["longbow", "shortsword", "dagger"],
    "rogue": ["rapier", "shortsword", "dagger", "thieves-tools"],
    "sorcerer": ["dagger", "light-crossbow", "component-pouch"],
    "warlock": ["quarterstaff", "dagger", "component-pouch"],
    "wizard": ["quarterstaff", "dagger", "spellbook", "component-pouch"],
}

# Class -> typical armor ID
CLASS_ARMOR: dict[str, str | None] = {
    "barbarian": None,       # unarmored defense
    "bard": "leather",
    "cleric": "scale-mail",
    "druid": "leather",
    "fighter": "chain-mail",
    "monk": None,            # unarmored defense
    "paladin": "chain-mail",
    "ranger": "leather",
    "rogue": "leather",
    "sorcerer": None,
    "warlock": "leather",
    "wizard": None,
}

# Caster classes -> sample spell IDs by level bracket
CASTER_SPELLS: dict[str, dict[str, list[str]]] = {
    "wizard": {
        "cantrips": ["fire-bolt", "mage-hand", "prestidigitation", "light"],
        "level_1": ["magic-missile", "shield", "detect-magic", "mage-armor", "sleep"],
        "level_2": ["misty-step", "scorching-ray", "hold-person", "invisibility"],
        "level_3": ["fireball", "counterspell", "fly", "dispel-magic"],
    },
    "cleric": {
        "cantrips": ["sacred-flame", "light", "guidance", "spare-the-dying"],
        "level_1": ["cure-wounds", "bless", "guiding-bolt", "healing-word", "shield-of-faith"],
        "level_2": ["spiritual-weapon", "hold-person", "lesser-restoration"],
        "level_3": ["spirit-guardians", "revivify", "dispel-magic"],
    },
    "sorcerer": {
        "cantrips": ["fire-bolt", "prestidigitation", "mage-hand", "light"],
        "level_1": ["magic-missile", "shield", "mage-armor", "chromatic-orb"],
        "level_2": ["misty-step", "scorching-ray", "hold-person"],
        "level_3": ["fireball", "counterspell", "fly"],
    },
    "warlock": {
        "cantrips": ["eldritch-blast", "prestidigitation", "mage-hand"],
        "level_1": ["hex", "armor-of-agathys", "hellish-rebuke"],
        "level_2": ["misty-step", "hold-person", "invisibility"],
        "level_3": ["counterspell", "fly", "hunger-of-hadar"],
    },
    "bard": {
        "cantrips": ["prestidigitation", "mage-hand", "light"],
        "level_1": ["healing-word", "cure-wounds", "faerie-fire", "thunderwave"],
        "level_2": ["hold-person", "invisibility", "lesser-restoration"],
        "level_3": ["dispel-magic", "hypnotic-pattern"],
    },
    "druid": {
        "cantrips": ["guidance", "produce-flame", "thorn-whip"],
        "level_1": ["cure-wounds", "entangle", "healing-word", "faerie-fire"],
        "level_2": ["moonbeam", "hold-person", "lesser-restoration"],
        "level_3": ["call-lightning", "dispel-magic", "plant-growth"],
    },
    "paladin": {
        "cantrips": [],
        "level_1": ["cure-wounds", "bless", "shield-of-faith", "thunderous-smite"],
        "level_2": ["find-steed", "lesser-restoration", "aid"],
        "level_3": ["revivify", "dispel-magic"],
    },
    "ranger": {
        "cantrips": [],
        "level_1": ["cure-wounds", "hunters-mark", "ensnaring-strike"],
        "level_2": ["pass-without-trace", "lesser-restoration", "spike-growth"],
        "level_3": ["conjure-animals", "lightning-arrow"],
    },
}

# Skills per class for proficiency assignment
CLASS_SKILL_POOL: dict[str, list[str]] = {
    "barbarian": ["animal-handling", "athletics", "intimidation", "nature", "perception", "survival"],
    "bard": ["acrobatics", "animal-handling", "arcana", "athletics", "deception", "history",
             "insight", "intimidation", "investigation", "medicine", "nature", "perception",
             "performance", "persuasion", "religion", "sleight-of-hand", "stealth", "survival"],
    "cleric": ["history", "insight", "medicine", "persuasion", "religion"],
    "druid": ["arcana", "animal-handling", "insight", "medicine", "nature", "perception", "religion", "survival"],
    "fighter": ["acrobatics", "animal-handling", "athletics", "history", "insight", "intimidation", "perception", "survival"],
    "monk": ["acrobatics", "athletics", "history", "insight", "religion", "stealth"],
    "paladin": ["athletics", "insight", "intimidation", "medicine", "persuasion", "religion"],
    "ranger": ["animal-handling", "athletics", "insight", "investigation", "nature", "perception", "stealth", "survival"],
    "rogue": ["acrobatics", "athletics", "deception", "insight", "intimidation", "investigation",
              "perception", "performance", "persuasion", "sleight-of-hand", "stealth"],
    "sorcerer": ["arcana", "deception", "insight", "intimidation", "persuasion", "religion"],
    "warlock": ["arcana", "deception", "history", "intimidation", "investigation", "nature", "religion"],
    "wizard": ["arcana", "history", "insight", "investigation", "medicine", "religion"],
}

# Number of skill proficiencies per class
CLASS_NUM_SKILLS: dict[str, int] = {
    "barbarian": 2, "bard": 3, "cleric": 2, "druid": 2,
    "fighter": 2, "monk": 2, "paladin": 2, "ranger": 3,
    "rogue": 4, "sorcerer": 2, "warlock": 2, "wizard": 2,
}

# Memory templates for _random_memories
MEMORY_TEMPLATES: list[str] = [
    "Day {day}: Spoke with {name} at the {location}.",
    "Day {day}: Saw something strange near the {location}.",
    "Day {day}: Traded goods with {name} at the market.",
    "Day {day}: Heard a rumor about {name} and the {location}.",
    "Day {day}: Felt uneasy after overhearing a conversation.",
    "Day {day}: Helped {name} carry supplies to the {location}.",
    "Day {day}: Argued with {name} about village politics.",
    "Day {day}: Found a strange item near the {location}.",
    "Day {day}: Had a pleasant meal at the tavern with {name}.",
    "Day {day}: Noticed {name} acting suspiciously.",
    "Day {day}: Prayed at the chapel for guidance.",
    "Day {day}: Patrolled the perimeter. Nothing unusual.",
    "Day {day}: Witnessed a heated argument between villagers.",
    "Day {day}: Gathered herbs in the forest for the healer.",
    "Day {day}: Received a cryptic warning from a stranger.",
]

# Event templates for _random_events
EVENT_TEMPLATES: list[str] = [
    "A merchant caravan arrived from the east with exotic goods.",
    "Strange lights were seen over the forest at midnight.",
    "The blacksmith's forge fire spread to a nearby building.",
    "A traveling bard performed songs of distant wars.",
    "Heavy rain flooded the lower fields, ruining crops.",
    "A pack of wolves was spotted near the village perimeter.",
    "The village elder called a council meeting about the water supply.",
    "A mysterious hooded stranger was seen at the crossroads.",
    "The tavern ran out of ale, causing much grumbling.",
    "Guards reported tracks of a large creature near the mine.",
    "A child went missing but was found safe in the forest.",
    "The chapel bell rang without anyone pulling the rope.",
    "A dispute over land boundaries escalated between two farmers.",
    "Foreign soldiers were seen marching on the northern road.",
    "The old well in the square began producing murky water.",
]

# Relationship sentiments and reasons
RELATIONSHIP_SENTIMENTS: list[float] = [
    -0.9, -0.7, -0.5, -0.3, -0.1, 0.0, 0.1, 0.3, 0.5, 0.7, 0.9,
]

RELATIONSHIP_REASONS: list[str] = [
    "childhood friends",
    "business partners",
    "rivals for years",
    "saved their life once",
    "family feud",
    "trading partners",
    "former lovers",
    "mentor and student",
    "neighbors who argue often",
    "bonded over shared hardship",
    "distrusts after a betrayal",
    "owes a debt",
    "fellow soldiers in the guard",
    "religious disagreement",
    "respect for their skills",
]
