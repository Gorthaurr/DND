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
