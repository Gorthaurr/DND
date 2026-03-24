"""D&D 5e SRD weapons, armor, and adventuring gear."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Weapon:
    id: str
    name: str
    damage_dice: str      # "1d8", "2d6"
    damage_type: str      # slashing, piercing, bludgeoning
    weapon_type: str      # "simple_melee", "simple_ranged", "martial_melee", "martial_ranged"
    properties: list[str] = field(default_factory=list)
    range_normal: int = 0   # 0 = melee only
    range_long: int = 0
    cost_gp: float = 0
    weight: float = 0


@dataclass(frozen=True)
class Armor:
    id: str
    name: str
    ac_base: int
    armor_type: str       # "light", "medium", "heavy", "shield"
    max_dex_bonus: int | None = None  # None = unlimited, 0 = no DEX, 2 = max +2
    stealth_disadvantage: bool = False
    str_requirement: int = 0
    cost_gp: float = 0
    weight: float = 0


@dataclass(frozen=True)
class Item:
    id: str
    name: str
    item_type: str        # "gear", "tool", "consumable", "treasure"
    description: str = ""
    cost_gp: float = 0
    weight: float = 0


# ── WEAPONS ──

WEAPONS: dict[str, Weapon] = {}


def _w(w: Weapon) -> None:
    WEAPONS[w.id] = w


# Simple Melee
_w(Weapon("club", "Club", "1d4", "bludgeoning", "simple_melee", ["light"], cost_gp=0.1, weight=2))
_w(Weapon("dagger", "Dagger", "1d4", "piercing", "simple_melee", ["finesse", "light", "thrown"], 20, 60, 2, 1))
_w(Weapon("greatclub", "Greatclub", "1d8", "bludgeoning", "simple_melee", ["two-handed"], cost_gp=0.2, weight=10))
_w(Weapon("handaxe", "Handaxe", "1d6", "slashing", "simple_melee", ["light", "thrown"], 20, 60, 5, 2))
_w(Weapon("javelin", "Javelin", "1d6", "piercing", "simple_melee", ["thrown"], 30, 120, 0.5, 2))
_w(Weapon("light-hammer", "Light Hammer", "1d4", "bludgeoning", "simple_melee", ["light", "thrown"], 20, 60, 2, 2))
_w(Weapon("mace", "Mace", "1d6", "bludgeoning", "simple_melee", cost_gp=5, weight=4))
_w(Weapon("quarterstaff", "Quarterstaff", "1d6", "bludgeoning", "simple_melee", ["versatile"], cost_gp=0.2, weight=4))
_w(Weapon("sickle", "Sickle", "1d4", "slashing", "simple_melee", ["light"], cost_gp=1, weight=2))
_w(Weapon("spear", "Spear", "1d6", "piercing", "simple_melee", ["thrown", "versatile"], 20, 60, 1, 3))

# Simple Ranged
_w(Weapon("light-crossbow", "Light Crossbow", "1d8", "piercing", "simple_ranged", ["ammunition", "loading", "two-handed"], 80, 320, 25, 5))
_w(Weapon("dart", "Dart", "1d4", "piercing", "simple_ranged", ["finesse", "thrown"], 20, 60, 0.05, 0.25))
_w(Weapon("shortbow", "Shortbow", "1d6", "piercing", "simple_ranged", ["ammunition", "two-handed"], 80, 320, 25, 2))
_w(Weapon("sling", "Sling", "1d4", "bludgeoning", "simple_ranged", ["ammunition"], 30, 120, 0.1, 0))

# Martial Melee
_w(Weapon("battleaxe", "Battleaxe", "1d8", "slashing", "martial_melee", ["versatile"], cost_gp=10, weight=4))
_w(Weapon("flail", "Flail", "1d8", "bludgeoning", "martial_melee", cost_gp=10, weight=2))
_w(Weapon("glaive", "Glaive", "1d10", "slashing", "martial_melee", ["heavy", "reach", "two-handed"], cost_gp=20, weight=6))
_w(Weapon("greataxe", "Greataxe", "1d12", "slashing", "martial_melee", ["heavy", "two-handed"], cost_gp=30, weight=7))
_w(Weapon("greatsword", "Greatsword", "2d6", "slashing", "martial_melee", ["heavy", "two-handed"], cost_gp=50, weight=6))
_w(Weapon("halberd", "Halberd", "1d10", "slashing", "martial_melee", ["heavy", "reach", "two-handed"], cost_gp=20, weight=6))
_w(Weapon("longsword", "Longsword", "1d8", "slashing", "martial_melee", ["versatile"], cost_gp=15, weight=3))
_w(Weapon("maul", "Maul", "2d6", "bludgeoning", "martial_melee", ["heavy", "two-handed"], cost_gp=10, weight=10))
_w(Weapon("morningstar", "Morningstar", "1d8", "piercing", "martial_melee", cost_gp=15, weight=4))
_w(Weapon("rapier", "Rapier", "1d8", "piercing", "martial_melee", ["finesse"], cost_gp=25, weight=2))
_w(Weapon("scimitar", "Scimitar", "1d6", "slashing", "martial_melee", ["finesse", "light"], cost_gp=25, weight=3))
_w(Weapon("shortsword", "Shortsword", "1d6", "piercing", "martial_melee", ["finesse", "light"], cost_gp=10, weight=2))
_w(Weapon("warhammer", "Warhammer", "1d8", "bludgeoning", "martial_melee", ["versatile"], cost_gp=15, weight=2))

# Martial Ranged
_w(Weapon("hand-crossbow", "Hand Crossbow", "1d6", "piercing", "martial_ranged", ["ammunition", "light", "loading"], 30, 120, 75, 3))
_w(Weapon("heavy-crossbow", "Heavy Crossbow", "1d10", "piercing", "martial_ranged", ["ammunition", "heavy", "loading", "two-handed"], 100, 400, 50, 18))
_w(Weapon("longbow", "Longbow", "1d8", "piercing", "martial_ranged", ["ammunition", "heavy", "two-handed"], 150, 600, 50, 2))


# ── ARMOR ──

ARMORS: dict[str, Armor] = {}


def _a(a: Armor) -> None:
    ARMORS[a.id] = a


# Light
_a(Armor("padded", "Padded Armor", 11, "light", None, True, 0, 5, 8))
_a(Armor("leather", "Leather Armor", 11, "light", None, False, 0, 10, 10))
_a(Armor("studded-leather", "Studded Leather", 12, "light", None, False, 0, 45, 13))

# Medium
_a(Armor("hide", "Hide Armor", 12, "medium", 2, False, 0, 10, 12))
_a(Armor("chain-shirt", "Chain Shirt", 13, "medium", 2, False, 0, 50, 20))
_a(Armor("scale-mail", "Scale Mail", 14, "medium", 2, True, 0, 50, 45))
_a(Armor("breastplate", "Breastplate", 14, "medium", 2, False, 0, 400, 20))
_a(Armor("half-plate", "Half Plate", 15, "medium", 2, True, 0, 750, 40))

# Heavy
_a(Armor("ring-mail", "Ring Mail", 14, "heavy", 0, True, 0, 30, 40))
_a(Armor("chain-mail", "Chain Mail", 16, "heavy", 0, True, 13, 75, 55))
_a(Armor("splint", "Splint Armor", 17, "heavy", 0, True, 15, 200, 60))
_a(Armor("plate", "Plate Armor", 18, "heavy", 0, True, 15, 1500, 65))

# Shield
_a(Armor("shield", "Shield", 2, "shield", None, False, 0, 10, 6))


# ── COMMON GEAR ──

ITEMS: dict[str, Item] = {}


def _i(item: Item) -> None:
    ITEMS[item.id] = item


_i(Item("torch", "Torch", "gear", "Bright light 20ft, dim 20ft more. Burns 1 hour.", 0.01, 1))
_i(Item("rope-50", "Rope (50 ft)", "gear", "Hemp, 50 feet.", 1, 10))
_i(Item("rations-1", "Rations (1 day)", "consumable", "Dried food for one day.", 0.5, 2))
_i(Item("waterskin", "Waterskin", "gear", "Holds 4 pints of liquid.", 0.2, 5))
_i(Item("backpack", "Backpack", "gear", "Holds 30 pounds of gear.", 2, 5))
_i(Item("bedroll", "Bedroll", "gear", "Sleeping roll for camping.", 1, 7))
_i(Item("tinderbox", "Tinderbox", "gear", "Flint, fire steel, and tinder.", 0.5, 1))
_i(Item("healers-kit", "Healer's Kit", "gear", "10 uses. Stabilize a creature at 0 HP.", 5, 3))
_i(Item("health-potion", "Potion of Healing", "consumable", "Restores 2d4+2 hit points.", 50, 0.5))
_i(Item("thieves-tools", "Thieves' Tools", "tool", "Lockpicks and small tools for disarming traps.", 25, 1))
_i(Item("holy-symbol", "Holy Symbol", "gear", "A sacred symbol used as a spellcasting focus.", 5, 1))
_i(Item("component-pouch", "Component Pouch", "gear", "A belt pouch containing spell components.", 25, 2))
_i(Item("spellbook", "Spellbook", "gear", "A leather-bound book with 100 blank pages.", 50, 3))

# ── MORE CONSUMABLES (potions, scrolls) ──

_i(Item("greater-healing-potion", "Greater Healing Potion", "consumable", "Restores 4d4+4 hit points.", 100, 0.5))
_i(Item("superior-healing-potion", "Superior Healing Potion", "consumable", "Restores 8d4+8 hit points.", 500, 0.5))
_i(Item("supreme-healing-potion", "Supreme Healing Potion", "consumable", "Restores 10d4+20 hit points.", 5000, 0.5))
_i(Item("potion-fire-resistance", "Potion of Fire Resistance", "consumable", "Gain resistance to fire damage for 1 hour.", 300, 0.5))
_i(Item("potion-invisibility", "Potion of Invisibility", "consumable", "Become invisible for 1 hour. Effect ends if you attack or cast a spell.", 5000, 0.5))
_i(Item("potion-speed", "Potion of Speed", "consumable", "Gain effects of Haste spell for 1 minute (no concentration).", 400, 0.5))
_i(Item("potion-heroism", "Potion of Heroism", "consumable", "Gain 10 temp HP and Bless effect for 1 hour.", 180, 0.5))
_i(Item("potion-hill-giant-strength", "Potion of Hill Giant Strength", "consumable", "STR becomes 21 for 1 hour.", 500, 0.5))
_i(Item("potion-frost-giant-strength", "Potion of Frost Giant Strength", "consumable", "STR becomes 23 for 1 hour.", 1500, 0.5))
_i(Item("antitoxin", "Antitoxin", "consumable", "Advantage on saves vs. poison for 1 hour.", 50, 0))
_i(Item("scroll-identify", "Scroll of Identify", "consumable", "Single-use scroll: cast Identify (1st level).", 25, 0))
_i(Item("scroll-fireball", "Scroll of Fireball", "consumable", "Single-use scroll: cast Fireball (3rd level).", 200, 0))
_i(Item("scroll-revivify", "Scroll of Revivify", "consumable", "Single-use scroll: cast Revivify (3rd level).", 300, 0))

# ── TOOLS & KITS ──

_i(Item("smiths-tools", "Smith's Tools", "tool", "Tools for metalworking and smithing.", 20, 8))
_i(Item("brewers-supplies", "Brewer's Supplies", "tool", "Equipment for brewing ales and other beverages.", 20, 9))
_i(Item("masons-tools", "Mason's Tools", "tool", "Tools for stonecutting and masonry work.", 10, 8))
_i(Item("carpenters-tools", "Carpenter's Tools", "tool", "Tools for woodworking and carpentry.", 8, 6))
_i(Item("cooks-utensils", "Cook's Utensils", "tool", "Pots, pans, and utensils for preparing meals.", 1, 8))
_i(Item("herbalism-kit", "Herbalism Kit", "tool", "Tools for identifying and applying herbs. Create antitoxin and potions of healing.", 5, 3))
_i(Item("poisoners-kit", "Poisoner's Kit", "tool", "Vials, chemicals, and tools for crafting poisons.", 50, 2))
_i(Item("alchemists-supplies", "Alchemist's Supplies", "tool", "Beakers, chemicals, and tools for alchemical experiments.", 50, 8))
_i(Item("disguise-kit", "Disguise Kit", "tool", "Cosmetics, hair dye, props for creating disguises.", 25, 3))
_i(Item("forgery-kit", "Forgery Kit", "tool", "Inks, parchment, quills, seals, and gold/silver leaf for forging documents.", 15, 5))
_i(Item("navigators-tools", "Navigator's Tools", "tool", "Sextant, compass, calipers, ruler, parchment, ink, and quill.", 25, 2))
_i(Item("lute", "Musical Instrument - Lute", "tool", "A stringed musical instrument.", 35, 2))
_i(Item("flute", "Musical Instrument - Flute", "tool", "A wind musical instrument.", 2, 1))
_i(Item("drum", "Musical Instrument - Drum", "tool", "A percussion musical instrument.", 6, 3))

# ── MORE ADVENTURING GEAR ──

_i(Item("caltrops", "Caltrops", "gear", "Bag of 20. Covers 5ft area; creature entering must save or stop and take 1 piercing.", 1, 2))
_i(Item("ball-bearings", "Ball Bearings", "gear", "Bag of 1000. Covers 10ft area; creature entering must DEX save or fall prone.", 1, 2))
_i(Item("grappling-hook", "Grappling Hook", "gear", "Iron hook for climbing. Attach to rope.", 2, 4))
_i(Item("hammer", "Hammer", "gear", "Standard hammer for driving pitons and nails.", 1, 3))
_i(Item("piton", "Piton", "gear", "Iron spike for climbing.", 0.05, 0.25))
_i(Item("hunting-trap", "Hunting Trap", "gear", "Steel jaws snap shut when stepped on. DC 13 DEX save or 1d4 piercing and restrained.", 5, 25))
_i(Item("lantern-hooded", "Lantern, Hooded", "gear", "Bright light 30ft, dim 30ft more. Burns 6 hours on 1 pint of oil. Can dim to 5ft.", 5, 2))
_i(Item("lantern-bullseye", "Lantern, Bullseye", "gear", "Bright 60ft cone, dim 60ft more. Burns 6 hours on 1 pint of oil.", 10, 2))
_i(Item("oil-flask", "Oil (Flask)", "gear", "1 pint. Splash on creature or 5ft area; if ignited, 5 fire damage for 2 rounds.", 0.1, 1))
_i(Item("manacles", "Manacles", "gear", "Iron restraints. DC 20 STR to break, DC 15 DEX to escape with thieves' tools.", 2, 6))
_i(Item("mirror-steel", "Mirror, Steel", "gear", "A small polished steel mirror.", 5, 0.5))
_i(Item("crowbar", "Crowbar", "gear", "Advantage on STR checks where leverage can be applied.", 2, 5))
_i(Item("chain-10ft", "Chain (10 ft)", "gear", "Iron chain. AC 19, 10 HP. Can be burst with DC 20 STR check.", 5, 10))
_i(Item("tent-two-person", "Tent, Two-Person", "gear", "A simple canvas shelter for two.", 2, 20))
_i(Item("climbers-kit", "Climber's Kit", "gear", "Pitons, boot tips, gloves, harness. Anchor yourself; can't fall more than 25ft.", 25, 12))
_i(Item("hourglass", "Hourglass", "gear", "A small glass timer.", 25, 1))
_i(Item("ink-bottle", "Ink Bottle", "gear", "1 ounce bottle of black ink.", 10, 0))
_i(Item("paper-sheet", "Paper (Sheet)", "gear", "A single sheet of paper.", 0.2, 0))
_i(Item("parchment-sheet", "Parchment (Sheet)", "gear", "A single sheet of parchment.", 0.1, 0))
_i(Item("sealing-wax", "Sealing Wax", "gear", "A stick of sealing wax.", 0.5, 0))
_i(Item("signet-ring", "Signet Ring", "gear", "A ring engraved with a personal seal.", 5, 0))
_i(Item("vial", "Vial", "gear", "A small glass vial that holds 4 ounces of liquid.", 1, 0))
_i(Item("holy-water", "Holy Water", "consumable", "Splash on fiend/undead as ranged attack for 2d6 radiant damage.", 25, 1))
_i(Item("acid-vial", "Acid (Vial)", "consumable", "Ranged attack splash for 2d6 acid damage.", 25, 1))
_i(Item("alchemists-fire", "Alchemist's Fire", "consumable", "Ranged attack: target takes 1d4 fire at start of each turn. DC 10 DEX to extinguish.", 50, 1))


# ── MAGIC ITEMS ──

@dataclass(frozen=True)
class MagicItem:
    id: str
    name: str
    item_type: str  # "weapon", "armor", "wondrous", "ring", "wand", "potion", "scroll"
    rarity: str     # "common", "uncommon", "rare", "very_rare", "legendary"
    requires_attunement: bool = False
    description: str = ""
    bonus: int = 0  # +1, +2, +3 for weapons/armor
    properties: list[str] = field(default_factory=list)


MAGIC_ITEMS: dict[str, MagicItem] = {}


def _m(item: MagicItem) -> None:
    MAGIC_ITEMS[item.id] = item


# Wondrous Items
_m(MagicItem("bag-of-holding", "Bag of Holding", "wondrous", "uncommon", False,
             "Interior is 64 cubic feet. Weighs 15 lb regardless of contents. Max 500 lb."))
_m(MagicItem("cloak-of-protection", "Cloak of Protection", "wondrous", "uncommon", True,
             "+1 bonus to AC and saving throws.", 1))
_m(MagicItem("boots-of-elvenkind", "Boots of Elvenkind", "wondrous", "uncommon", False,
             "Your steps make no sound. Advantage on Stealth checks that rely on moving silently.",
             properties=["advantage_stealth"]))
_m(MagicItem("cloak-of-elvenkind", "Cloak of Elvenkind", "wondrous", "uncommon", True,
             "Advantage on Stealth checks to hide. Creatures have disadvantage on Perception checks to spot you.",
             properties=["advantage_stealth", "disadvantage_to_spot"]))
_m(MagicItem("gauntlets-of-ogre-power", "Gauntlets of Ogre Power", "wondrous", "uncommon", True,
             "Your Strength score is 19 while wearing these gauntlets.",
             properties=["set_str_19"]))
_m(MagicItem("headband-of-intellect", "Headband of Intellect", "wondrous", "uncommon", True,
             "Your Intelligence score is 19 while wearing this headband.",
             properties=["set_int_19"]))
_m(MagicItem("amulet-of-health", "Amulet of Health", "wondrous", "rare", True,
             "Your Constitution score is 19 while wearing this amulet.",
             properties=["set_con_19"]))
_m(MagicItem("bracers-of-defense", "Bracers of Defense", "wondrous", "rare", True,
             "+2 bonus to AC while wearing no armor and not using a shield.", 2,
             ["no_armor_required"]))
_m(MagicItem("pearl-of-power", "Pearl of Power", "wondrous", "uncommon", True,
             "Recover one expended spell slot of 3rd level or lower as an action. Recharges at dawn.",
             properties=["recover_spell_slot"]))
_m(MagicItem("immovable-rod", "Immovable Rod", "wondrous", "uncommon", False,
             "Press button to fix in place. Holds up to 8000 lb. DC 30 STR to move."))
_m(MagicItem("rope-of-climbing", "Rope of Climbing", "wondrous", "uncommon", False,
             "60 ft rope. Command to animate: knot/unknot, move 10 ft/round, climb with advantage."))
_m(MagicItem("decanter-of-endless-water", "Decanter of Endless Water", "wondrous", "uncommon", False,
             "Produce 1-30 gallons of water per round on command."))
_m(MagicItem("periapt-of-wound-closure", "Periapt of Wound Closure", "wondrous", "uncommon", True,
             "Stabilize automatically at 0 HP. When you roll Hit Dice to regain HP, double the number of HP restored.",
             properties=["auto_stabilize", "double_healing_dice"]))

# Ring
_m(MagicItem("ring-of-protection", "Ring of Protection", "ring", "rare", True,
             "+1 bonus to AC and saving throws.", 1))

# Weapons (magic)
_m(MagicItem("plus-1-weapon", "+1 Weapon", "weapon", "uncommon", False,
             "+1 bonus to attack and damage rolls.", 1))
_m(MagicItem("plus-2-weapon", "+2 Weapon", "weapon", "rare", False,
             "+2 bonus to attack and damage rolls.", 2))
_m(MagicItem("flame-tongue", "Flame Tongue", "weapon", "rare", True,
             "Command word to ignite. While ablaze, deals extra 2d6 fire damage on hit. Bright light 40 ft, dim 40 ft.", 0,
             ["2d6_fire_on_hit"]))
_m(MagicItem("frost-brand", "Frost Brand", "weapon", "very_rare", True,
             "Deals extra 1d6 cold damage on hit. Resistance to fire damage. In freezing temps, bright light 10 ft, dim 10 ft.", 0,
             ["1d6_cold_on_hit", "fire_resistance"]))
_m(MagicItem("staff-of-power", "Staff of Power", "weapon", "very_rare", True,
             "+2 to attack/damage, +2 to AC/saves/spell attack. 20 charges for various spells. Retributive strike on break.", 2,
             ["spellcasting_focus", "20_charges"]))

# Armor (magic)
_m(MagicItem("plus-1-armor", "+1 Armor", "armor", "uncommon", False,
             "+1 bonus to AC beyond the armor's normal AC bonus.", 1))
_m(MagicItem("plus-2-armor", "+2 Armor", "armor", "rare", False,
             "+2 bonus to AC beyond the armor's normal AC bonus.", 2))
_m(MagicItem("plus-1-shield", "+1 Shield", "armor", "uncommon", False,
             "+1 bonus to AC beyond the shield's normal AC bonus.", 1))

# Wands
_m(MagicItem("wand-of-magic-missiles", "Wand of Magic Missiles", "wand", "uncommon", False,
             "7 charges. Expend 1+ charges to cast Magic Missile (1 charge per level above 1st). Regains 1d6+1 charges at dawn.",
             properties=["7_charges"]))
_m(MagicItem("wand-of-fireballs", "Wand of Fireballs", "wand", "rare", True,
             "7 charges. Expend 1+ charges to cast Fireball (1 charge per level above 3rd). Regains 1d6+1 charges at dawn.",
             properties=["7_charges"]))


def get_weapon(weapon_id: str) -> Weapon | None:
    return WEAPONS.get(weapon_id)


def get_armor(armor_id: str) -> Armor | None:
    return ARMORS.get(armor_id)


def get_item(item_id: str) -> Item | None:
    return ITEMS.get(item_id)


def list_weapons() -> list[Weapon]:
    return list(WEAPONS.values())


def list_armors() -> list[Armor]:
    return list(ARMORS.values())


def list_items() -> list[Item]:
    return list(ITEMS.values())


def get_magic_item(item_id: str) -> MagicItem | None:
    return MAGIC_ITEMS.get(item_id)


def list_magic_items(
    rarity: str | None = None,
    item_type: str | None = None,
) -> list[MagicItem]:
    """Return magic items, optionally filtered by rarity and/or item_type."""
    items = list(MAGIC_ITEMS.values())
    if rarity:
        items = [i for i in items if i.rarity == rarity]
    if item_type:
        items = [i for i in items if i.item_type == item_type]
    return items
