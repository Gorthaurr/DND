"""D&D 5e SRD spells — cantrips through 5th level."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Spell:
    id: str
    name: str
    level: int                              # 0 = cantrip
    school: str                             # abjuration / conjuration / divination / enchantment / evocation / illusion / necromancy / transmutation
    casting_time: str                       # "1 action", "1 bonus action", "1 reaction", "1 minute", etc.
    range_ft: int                           # 0 = self/touch, -1 = special
    components: list[str]                   # ["V"], ["V","S"], ["V","S","M"]
    duration: str                           # "Instantaneous", "1 round", "Concentration, up to 1 minute", etc.
    concentration: bool
    description: str
    classes: list[str]                      # class ids
    damage_dice: str | None = None          # "1d10", "8d6", etc.
    damage_type: str | None = None          # fire, cold, radiant, etc.
    healing_dice: str | None = None         # "1d8", "2d8+2", etc.
    save_ability: str | None = None         # "DEX", "WIS", etc.
    effect_type: str = "utility"            # damage / healing / buff / debuff / utility / control / summon
    area_type: str | None = None            # single / cone / sphere / cube / line / cylinder
    area_size: int | None = None            # ft
    conditions_applied: list[str] = field(default_factory=list)
    at_higher_levels: str | None = None


# ── Spell Registry ──

SPELLS: dict[str, Spell] = {}


def _sp(s: Spell) -> None:
    SPELLS[s.id] = s


# ═══════════════════════════════════════════════════════════════
#  CANTRIPS  (Level 0)
# ═══════════════════════════════════════════════════════════════

_sp(Spell(
    "fire-bolt", "Fire Bolt", 0, "evocation",
    "1 action", 120, ["V", "S"], "Instantaneous", False,
    "Hurl a mote of fire at a creature or object. Make a ranged spell attack. On hit deal fire damage. Damage increases at 5th, 11th, and 17th level.",
    ["sorcerer", "wizard"],
    damage_dice="1d10", damage_type="fire", effect_type="damage", area_type="single",
))

_sp(Spell(
    "sacred-flame", "Sacred Flame", 0, "evocation",
    "1 action", 60, ["V", "S"], "Instantaneous", False,
    "Flame-like radiance descends on a creature. Target must succeed on a DEX save or take radiant damage. No benefit from cover. Damage increases at 5th, 11th, and 17th level.",
    ["cleric"],
    damage_dice="1d8", damage_type="radiant", save_ability="DEX", effect_type="damage", area_type="single",
))

_sp(Spell(
    "eldritch-blast", "Eldritch Blast", 0, "evocation",
    "1 action", 120, ["V", "S"], "Instantaneous", False,
    "A beam of crackling energy streaks toward a creature. Make a ranged spell attack. On hit deal force damage. Additional beams at 5th, 11th, and 17th level.",
    ["warlock"],
    damage_dice="1d10", damage_type="force", effect_type="damage", area_type="single",
))

_sp(Spell(
    "mage-hand", "Mage Hand", 0, "conjuration",
    "1 action", 30, ["V", "S"], "1 minute", False,
    "A spectral floating hand appears. It can manipulate objects, open doors, pour out vials, etc. Cannot attack, activate magic items, or carry more than 10 lb.",
    ["bard", "sorcerer", "warlock", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "light", "Light", 0, "evocation",
    "1 action", 0, ["V", "M"], "1 hour", False,
    "Touch an object no larger than 10 feet in any dimension. It sheds bright light in a 20-foot radius and dim light for an additional 20 feet.",
    ["bard", "cleric", "sorcerer", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "prestidigitation", "Prestidigitation", 0, "transmutation",
    "1 action", 10, ["V", "S"], "Up to 1 hour", False,
    "A minor magical trick. Create sensory effects, light/snuff flames, clean/soil objects, warm/cool/flavor material, create small illusions or marks.",
    ["bard", "sorcerer", "warlock", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "thaumaturgy", "Thaumaturgy", 0, "transmutation",
    "1 action", 30, ["V"], "Up to 1 minute", False,
    "Manifest a minor wonder of divine power. Boom voice, cause flames to flicker, tremors, sounds, slam doors, alter eye appearance.",
    ["cleric"],
    effect_type="utility",
))

_sp(Spell(
    "guidance", "Guidance", 0, "divination",
    "1 action", 0, ["V", "S"], "Concentration, up to 1 minute", True,
    "Touch a willing creature. Once before the spell ends, the target can roll a d4 and add it to one ability check of its choice.",
    ["cleric", "druid"],
    effect_type="buff",
))

_sp(Spell(
    "minor-illusion", "Minor Illusion", 0, "illusion",
    "1 action", 30, ["S", "M"], "1 minute", False,
    "Create a sound or image of an object within range that lasts for the duration. The image cannot move. An INT (Investigation) check reveals it as illusion.",
    ["bard", "sorcerer", "warlock", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "spare-the-dying", "Spare the Dying", 0, "necromancy",
    "1 action", 0, ["V", "S"], "Instantaneous", False,
    "Touch a living creature that has 0 hit points. The creature becomes stable.",
    ["cleric"],
    effect_type="healing",
))

_sp(Spell(
    "vicious-mockery", "Vicious Mockery", 0, "enchantment",
    "1 action", 60, ["V"], "Instantaneous", False,
    "Unleash a string of insults laced with subtle enchantments. Target must succeed on a WIS save or take psychic damage and have disadvantage on its next attack roll.",
    ["bard"],
    damage_dice="1d4", damage_type="psychic", save_ability="WIS", effect_type="debuff", area_type="single",
))

_sp(Spell(
    "chill-touch", "Chill Touch", 0, "necromancy",
    "1 action", 120, ["V", "S"], "1 round", False,
    "A ghostly skeletal hand strikes a creature. Make a ranged spell attack. On hit deal necrotic damage and target cannot regain HP until start of your next turn.",
    ["sorcerer", "warlock", "wizard"],
    damage_dice="1d8", damage_type="necrotic", effect_type="damage", area_type="single",
))

_sp(Spell(
    "ray-of-frost", "Ray of Frost", 0, "evocation",
    "1 action", 60, ["V", "S"], "Instantaneous", False,
    "A frigid beam strikes a creature. Make a ranged spell attack. On hit deal cold damage and target speed is reduced by 10 ft until start of your next turn.",
    ["sorcerer", "wizard"],
    damage_dice="1d8", damage_type="cold", effect_type="damage", area_type="single",
))

_sp(Spell(
    "shocking-grasp", "Shocking Grasp", 0, "evocation",
    "1 action", 0, ["V", "S"], "Instantaneous", False,
    "Lightning springs from your hand. Make a melee spell attack (advantage if target wears metal). On hit deal lightning damage and target cannot take reactions until start of its next turn.",
    ["sorcerer", "wizard"],
    damage_dice="1d8", damage_type="lightning", effect_type="damage", area_type="single",
))

_sp(Spell(
    "druidcraft", "Druidcraft", 0, "transmutation",
    "1 action", 30, ["V", "S"], "Instantaneous", False,
    "Whispering to the spirits of nature, you create a tiny harmless sensory effect, predict weather, bloom a flower, or create a sensory effect.",
    ["druid"],
    effect_type="utility",
))

_sp(Spell(
    "produce-flame", "Produce Flame", 0, "conjuration",
    "1 action", 0, ["V", "S"], "10 minutes", False,
    "A flickering flame appears in your hand. It sheds bright light in a 10-foot radius. You can hurl the flame to make a ranged spell attack dealing fire damage.",
    ["druid"],
    damage_dice="1d8", damage_type="fire", effect_type="damage", area_type="single",
))

_sp(Spell(
    "shillelagh", "Shillelagh", 0, "transmutation",
    "1 bonus action", 0, ["V", "S", "M"], "1 minute", False,
    "The wood of a club or quarterstaff you hold is imbued with nature's power. It uses your spellcasting ability for attacks and deals 1d8 force damage.",
    ["druid"],
    effect_type="buff",
))

_sp(Spell(
    "blade-ward", "Blade Ward", 0, "abjuration",
    "1 action", 0, ["V", "S"], "1 round", False,
    "You gain resistance to bludgeoning, piercing, and slashing damage from weapon attacks until the end of your next turn.",
    ["bard", "sorcerer", "warlock", "wizard"],
    effect_type="buff",
))

_sp(Spell(
    "true-strike", "True Strike", 0, "divination",
    "1 action", 30, ["S"], "Concentration, up to 1 round", True,
    "You gain insight into the target's defenses. On your next turn, your first attack roll against the target has advantage.",
    ["bard", "sorcerer", "warlock", "wizard"],
    effect_type="buff",
))

_sp(Spell(
    "mending", "Mending", 0, "transmutation",
    "1 minute", 0, ["V", "S", "M"], "Instantaneous", False,
    "Repair a single break or tear in an object you touch. The break can be no larger than 1 foot in any dimension.",
    ["bard", "cleric", "druid", "sorcerer", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "message", "Message", 0, "transmutation",
    "1 action", 120, ["V", "S", "M"], "1 round", False,
    "Whisper a message to a target within range. The target and only the target hears the message and can reply in a whisper.",
    ["bard", "sorcerer", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "friends", "Friends", 0, "enchantment",
    "1 action", 0, ["S", "M"], "Concentration, up to 1 minute", True,
    "You have advantage on CHA checks directed at one creature of your choice that is not hostile. When the spell ends, the creature realizes you used magic on it.",
    ["bard", "sorcerer", "warlock", "wizard"],
    effect_type="buff",
))

_sp(Spell(
    "dancing-lights", "Dancing Lights", 0, "evocation",
    "1 action", 120, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "Create up to four torch-sized lights within range that shed dim light in a 10-foot radius. You can combine them into one glowing humanoid form.",
    ["bard", "sorcerer", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "poison-spray", "Poison Spray", 0, "conjuration",
    "1 action", 10, ["V", "S"], "Instantaneous", False,
    "You extend your hand and project a puff of noxious gas. Target creature must succeed on a CON save or take poison damage.",
    ["druid", "sorcerer", "warlock", "wizard"],
    damage_dice="1d12", damage_type="poison", save_ability="CON", effect_type="damage", area_type="single",
))

_sp(Spell(
    "toll-the-dead", "Toll the Dead", 0, "necromancy",
    "1 action", 60, ["V", "S"], "Instantaneous", False,
    "You point at one creature within range and the sound of a dolorous bell fills the air. Target must succeed on a WIS save or take 1d8 necrotic damage (1d12 if missing any HP).",
    ["cleric", "warlock", "wizard"],
    damage_dice="1d8", damage_type="necrotic", save_ability="WIS", effect_type="damage", area_type="single",
))

_sp(Spell(
    "word-of-radiance", "Word of Radiance", 0, "evocation",
    "1 action", 5, ["V", "M"], "Instantaneous", False,
    "You utter a divine word and burning radiance erupts from you. Each creature of your choice within range must succeed on a CON save or take radiant damage.",
    ["cleric"],
    damage_dice="1d6", damage_type="radiant", save_ability="CON", effect_type="damage", area_type="sphere", area_size=5,
))


# ═══════════════════════════════════════════════════════════════
#  LEVEL 1  SPELLS
# ═══════════════════════════════════════════════════════════════

_sp(Spell(
    "magic-missile", "Magic Missile", 1, "evocation",
    "1 action", 120, ["V", "S"], "Instantaneous", False,
    "Three glowing darts of magical force strike targets automatically. Each dart deals 1d4+1 force damage.",
    ["sorcerer", "wizard"],
    damage_dice="3d4+3", damage_type="force", effect_type="damage", area_type="single",
    at_higher_levels="One additional dart per slot level above 1st.",
))

_sp(Spell(
    "shield", "Shield", 1, "abjuration",
    "1 reaction", 0, ["V", "S"], "1 round", False,
    "An invisible barrier of magical force appears and protects you. Until the start of your next turn you get +5 to AC and take no damage from magic missile.",
    ["sorcerer", "wizard"],
    effect_type="buff",
))

_sp(Spell(
    "cure-wounds", "Cure Wounds", 1, "evocation",
    "1 action", 0, ["V", "S"], "Instantaneous", False,
    "A creature you touch regains hit points equal to 1d8 + your spellcasting ability modifier.",
    ["bard", "cleric", "druid", "paladin", "ranger"],
    healing_dice="1d8", effect_type="healing",
    at_higher_levels="Healing increases by 1d8 for each slot level above 1st.",
))

_sp(Spell(
    "healing-word", "Healing Word", 1, "evocation",
    "1 bonus action", 60, ["V"], "Instantaneous", False,
    "A creature of your choice that you can see within range regains hit points equal to 1d4 + your spellcasting ability modifier.",
    ["bard", "cleric", "druid"],
    healing_dice="1d4", effect_type="healing",
    at_higher_levels="Healing increases by 1d4 for each slot level above 1st.",
))

_sp(Spell(
    "thunderwave", "Thunderwave", 1, "evocation",
    "1 action", 0, ["V", "S"], "Instantaneous", False,
    "A wave of thunderous force sweeps out from you. Each creature in a 15-foot cube must make a CON save. On fail take 2d8 thunder damage and be pushed 10 ft. On success half damage, no push.",
    ["bard", "druid", "sorcerer", "wizard"],
    damage_dice="2d8", damage_type="thunder", save_ability="CON", effect_type="damage",
    area_type="cube", area_size=15,
    at_higher_levels="Damage increases by 1d8 for each slot level above 1st.",
))

_sp(Spell(
    "burning-hands", "Burning Hands", 1, "evocation",
    "1 action", 0, ["V", "S"], "Instantaneous", False,
    "A thin sheet of flames shoots forth from your fingertips. Each creature in a 15-foot cone must make a DEX save. On fail take 3d6 fire damage. On success half.",
    ["sorcerer", "wizard"],
    damage_dice="3d6", damage_type="fire", save_ability="DEX", effect_type="damage",
    area_type="cone", area_size=15,
    at_higher_levels="Damage increases by 1d6 for each slot level above 1st.",
))

_sp(Spell(
    "bless", "Bless", 1, "enchantment",
    "1 action", 30, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "You bless up to three creatures of your choice within range. Whenever a target makes an attack roll or saving throw before the spell ends, it can roll a d4 and add it.",
    ["cleric", "paladin"],
    effect_type="buff",
    at_higher_levels="One additional creature for each slot level above 1st.",
))

_sp(Spell(
    "bane", "Bane", 1, "enchantment",
    "1 action", 30, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "Up to three creatures within range must make CHA saves. On fail, whenever a target makes an attack roll or saving throw it must roll a d4 and subtract it.",
    ["bard", "cleric"],
    save_ability="CHA", effect_type="debuff",
    at_higher_levels="One additional creature for each slot level above 1st.",
))

_sp(Spell(
    "command", "Command", 1, "enchantment",
    "1 action", 60, ["V"], "1 round", False,
    "You speak a one-word command to a creature within range. Target must succeed on a WIS save or follow the command on its next turn. No effect on undead.",
    ["cleric", "paladin"],
    save_ability="WIS", effect_type="control",
    at_higher_levels="One additional creature for each slot level above 1st.",
))

_sp(Spell(
    "detect-magic", "Detect Magic", 1, "divination",
    "1 action", 0, ["V", "S"], "Concentration, up to 10 minutes", True,
    "For the duration you sense the presence of magic within 30 feet. You can also see a faint aura around any visible creature or object that bears magic and learn its school.",
    ["bard", "cleric", "druid", "paladin", "ranger", "sorcerer", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "mage-armor", "Mage Armor", 1, "abjuration",
    "1 action", 0, ["V", "S", "M"], "8 hours", False,
    "You touch a willing creature who is not wearing armor. Target's base AC becomes 13 + its DEX modifier. The spell ends if the target dons armor or you dismiss it.",
    ["sorcerer", "wizard"],
    effect_type="buff",
))

_sp(Spell(
    "sleep", "Sleep", 1, "enchantment",
    "1 action", 90, ["V", "S", "M"], "1 minute", False,
    "You send creatures in a 20-foot radius sphere into a magical slumber. Roll 5d8; starting from lowest current HP, creatures fall unconscious.",
    ["bard", "sorcerer", "wizard"],
    effect_type="control", area_type="sphere", area_size=20,
    conditions_applied=["unconscious"],
    at_higher_levels="Roll an additional 2d8 for each slot level above 1st.",
))

_sp(Spell(
    "charm-person", "Charm Person", 1, "enchantment",
    "1 action", 30, ["V", "S"], "1 hour", False,
    "You attempt to charm a humanoid you can see within range. It must make a WIS save (with advantage if you or your companions are fighting it). On fail it is charmed by you.",
    ["bard", "druid", "sorcerer", "warlock", "wizard"],
    save_ability="WIS", effect_type="control",
    conditions_applied=["charmed"],
    at_higher_levels="One additional creature for each slot level above 1st.",
))

_sp(Spell(
    "guiding-bolt", "Guiding Bolt", 1, "evocation",
    "1 action", 120, ["V", "S"], "1 round", False,
    "A flash of light streaks toward a creature within range. Make a ranged spell attack. On hit deal 4d6 radiant damage and the next attack roll against the target has advantage.",
    ["cleric"],
    damage_dice="4d6", damage_type="radiant", effect_type="damage", area_type="single",
    at_higher_levels="Damage increases by 1d6 for each slot level above 1st.",
))

_sp(Spell(
    "inflict-wounds", "Inflict Wounds", 1, "necromancy",
    "1 action", 0, ["V", "S"], "Instantaneous", False,
    "Make a melee spell attack. On hit the target takes 3d10 necrotic damage.",
    ["cleric"],
    damage_dice="3d10", damage_type="necrotic", effect_type="damage", area_type="single",
    at_higher_levels="Damage increases by 1d10 for each slot level above 1st.",
))

_sp(Spell(
    "sanctuary", "Sanctuary", 1, "abjuration",
    "1 bonus action", 30, ["V", "S", "M"], "1 minute", False,
    "You ward a creature within range. Any creature targeting the warded creature with an attack or harmful spell must first make a WIS save. On fail it must choose a new target or lose the attack/spell.",
    ["cleric"],
    save_ability="WIS", effect_type="buff",
))

_sp(Spell(
    "hex", "Hex", 1, "enchantment",
    "1 bonus action", 90, ["V", "S", "M"], "Concentration, up to 1 hour", True,
    "You place a curse on a creature. You deal an extra 1d6 necrotic damage whenever you hit it with an attack. Choose one ability; the target has disadvantage on checks with that ability.",
    ["warlock"],
    damage_dice="1d6", damage_type="necrotic", effect_type="debuff",
    at_higher_levels="Duration 8 hours at 3rd-4th level slot, 24 hours at 5th+ level slot.",
))

_sp(Spell(
    "hunters-mark", "Hunter's Mark", 1, "divination",
    "1 bonus action", 90, ["V"], "Concentration, up to 1 hour", True,
    "You choose a creature you can see within range and mystically mark it as your quarry. You deal an extra 1d6 damage whenever you hit it with a weapon attack. You have advantage on Perception and Survival checks to find it.",
    ["ranger"],
    damage_dice="1d6", effect_type="buff",
    at_higher_levels="Duration 8 hours at 3rd-4th level slot, 24 hours at 5th+ level slot.",
))

_sp(Spell(
    "faerie-fire", "Faerie Fire", 1, "evocation",
    "1 action", 60, ["V"], "Concentration, up to 1 minute", True,
    "Each object in a 20-foot cube within range is outlined in blue, green, or violet light. Any creature in the area when the spell is cast must succeed on a DEX save or be outlined too. Attack rolls against an affected creature or object have advantage.",
    ["bard", "druid"],
    save_ability="DEX", effect_type="debuff", area_type="cube", area_size=20,
))

_sp(Spell(
    "entangle", "Entangle", 1, "conjuration",
    "1 action", 90, ["V", "S"], "Concentration, up to 1 minute", True,
    "Grasping weeds and vines sprout from the ground in a 20-foot square within range. Creatures in the area must succeed on a STR save or be restrained. Difficult terrain.",
    ["druid"],
    save_ability="STR", effect_type="control", area_type="cube", area_size=20,
    conditions_applied=["restrained"],
))

_sp(Spell(
    "goodberry", "Goodberry", 1, "transmutation",
    "1 action", 0, ["V", "S", "M"], "Instantaneous", False,
    "Up to ten berries appear in your hand infused with magic. A creature can use its action to eat one berry, restoring 1 hit point. Berries provide enough nourishment for one day.",
    ["druid", "ranger"],
    healing_dice="1", effect_type="healing",
))

_sp(Spell(
    "fog-cloud", "Fog Cloud", 1, "conjuration",
    "1 action", 120, ["V", "S"], "Concentration, up to 1 hour", True,
    "You create a 20-foot-radius sphere of fog centered on a point within range. The sphere spreads around corners and its area is heavily obscured.",
    ["druid", "ranger", "sorcerer", "wizard"],
    effect_type="control", area_type="sphere", area_size=20,
    at_higher_levels="Radius increases by 20 ft for each slot level above 1st.",
))

_sp(Spell(
    "disguise-self", "Disguise Self", 1, "illusion",
    "1 action", 0, ["V", "S"], "1 hour", False,
    "You make yourself, your clothing, armor, weapons, and belongings look different until the spell ends or you dismiss it. You can seem up to 1 foot shorter or taller and thin, fat, or in between.",
    ["bard", "sorcerer", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "silent-image", "Silent Image", 1, "illusion",
    "1 action", 60, ["V", "S", "M"], "Concentration, up to 10 minutes", True,
    "You create the image of an object, creature, or visible phenomenon that is no larger than a 15-foot cube. It is purely visual—no sound, smell, or physical effect.",
    ["bard", "sorcerer", "wizard"],
    effect_type="utility", area_type="cube", area_size=15,
))

_sp(Spell(
    "chromatic-orb", "Chromatic Orb", 1, "evocation",
    "1 action", 90, ["V", "S", "M"], "Instantaneous", False,
    "You hurl a 4-inch-diameter sphere of energy at a creature you can see within range. Choose acid, cold, fire, lightning, poison, or thunder. Make a ranged spell attack. On hit deal 3d8 of the chosen type.",
    ["sorcerer", "wizard"],
    damage_dice="3d8", effect_type="damage", area_type="single",
    at_higher_levels="Damage increases by 1d8 for each slot level above 1st.",
))

_sp(Spell(
    "witch-bolt", "Witch Bolt", 1, "evocation",
    "1 action", 30, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "A beam of crackling blue energy lances toward a creature. Make a ranged spell attack. On hit deal 1d12 lightning damage. On subsequent turns you can use your action to deal 1d12 automatically.",
    ["sorcerer", "warlock", "wizard"],
    damage_dice="1d12", damage_type="lightning", effect_type="damage", area_type="single",
    at_higher_levels="Initial damage increases by 1d12 for each slot level above 1st.",
))

_sp(Spell(
    "armor-of-agathys", "Armor of Agathys", 1, "abjuration",
    "1 action", 0, ["V", "S", "M"], "1 hour", False,
    "A protective magical force surrounds you in a spectral frost. You gain 5 temporary HP for the duration. If a creature hits you with a melee attack while you have these HP, it takes 5 cold damage.",
    ["warlock"],
    damage_dice="5", damage_type="cold", effect_type="buff",
    at_higher_levels="Both temp HP and cold damage increase by 5 for each slot level above 1st.",
))

_sp(Spell(
    "hellish-rebuke", "Hellish Rebuke", 1, "evocation",
    "1 reaction", 60, ["V", "S"], "Instantaneous", False,
    "You point your finger at the creature that damaged you and it is momentarily surrounded by hellish flames. It must make a DEX save, taking 2d10 fire damage on a fail, or half on success.",
    ["warlock"],
    damage_dice="2d10", damage_type="fire", save_ability="DEX", effect_type="damage", area_type="single",
    at_higher_levels="Damage increases by 1d10 for each slot level above 1st.",
))

_sp(Spell(
    "expeditious-retreat", "Expeditious Retreat", 1, "transmutation",
    "1 bonus action", 0, ["V", "S"], "Concentration, up to 10 minutes", True,
    "You can take the Dash action as a bonus action on each of your turns for the duration.",
    ["sorcerer", "warlock", "wizard"],
    effect_type="buff",
))

_sp(Spell(
    "feather-fall", "Feather Fall", 1, "transmutation",
    "1 reaction", 60, ["V", "M"], "1 minute", False,
    "Choose up to five falling creatures within range. A falling creature's rate of descent slows to 60 feet per round. If it lands before the spell ends, it takes no falling damage.",
    ["bard", "sorcerer", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "find-familiar", "Find Familiar", 1, "conjuration",
    "1 hour", 10, ["V", "S", "M"], "Instantaneous", False,
    "You gain the service of a familiar—a spirit that takes an animal form you choose (bat, cat, hawk, lizard, octopus, owl, poisonous snake, fish, rat, raven, sea horse, spider, or weasel).",
    ["wizard"],
    effect_type="summon",
))

_sp(Spell(
    "identify", "Identify", 1, "divination",
    "1 minute", 0, ["V", "S", "M"], "Instantaneous", False,
    "You choose one object that you must touch throughout the casting. If it is a magic item or magical object, you learn its properties, how to use them, how many charges it has, and if attunement is required.",
    ["bard", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "comprehend-languages", "Comprehend Languages", 1, "divination",
    "1 action", 0, ["V", "S", "M"], "1 hour", False,
    "For the duration, you understand the literal meaning of any spoken language that you hear. You also understand any written language that you see, but you must be touching the surface it is written on.",
    ["bard", "sorcerer", "warlock", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "longstrider", "Longstrider", 1, "transmutation",
    "1 action", 0, ["V", "S", "M"], "1 hour", False,
    "Touch a creature. Target's speed increases by 10 feet until the spell ends.",
    ["bard", "druid", "ranger", "wizard"],
    effect_type="buff",
    at_higher_levels="One additional creature for each slot level above 1st.",
))

_sp(Spell(
    "jump", "Jump", 1, "transmutation",
    "1 action", 0, ["V", "S", "M"], "1 minute", False,
    "Touch a creature. Target's jump distance is tripled until the spell ends.",
    ["druid", "ranger", "sorcerer", "wizard"],
    effect_type="buff",
))

_sp(Spell(
    "speak-with-animals", "Speak with Animals", 1, "divination",
    "1 action", 0, ["V", "S"], "10 minutes", False,
    "You gain the ability to comprehend and verbally communicate with beasts for the duration.",
    ["bard", "druid", "ranger"],
    effect_type="utility",
))

_sp(Spell(
    "animal-friendship", "Animal Friendship", 1, "enchantment",
    "1 action", 30, ["V", "S", "M"], "24 hours", False,
    "This spell lets you convince a beast that you mean it no harm. A beast with INT 4 or higher is unaffected. The beast must succeed on a WIS save or be charmed for the duration.",
    ["bard", "druid", "ranger"],
    save_ability="WIS", effect_type="control",
    conditions_applied=["charmed"],
    at_higher_levels="One additional beast for each slot level above 1st.",
))

_sp(Spell(
    "create-or-destroy-water", "Create or Destroy Water", 1, "transmutation",
    "1 action", 30, ["V", "S", "M"], "Instantaneous", False,
    "You either create up to 10 gallons of clean water within range in an open container or destroy up to 10 gallons of water within range (fog/mist in a 30-foot cube).",
    ["cleric", "druid"],
    effect_type="utility",
    at_higher_levels="Create or destroy an additional 10 gallons for each slot level above 1st.",
))

_sp(Spell(
    "purify-food-and-drink", "Purify Food and Drink", 1, "transmutation",
    "1 action", 10, ["V", "S"], "Instantaneous", False,
    "All nonmagical food and drink within a 5-foot-radius sphere centered on a point of your choice within range is purified and rendered free of poison and disease.",
    ["cleric", "druid", "paladin"],
    effect_type="utility", area_type="sphere", area_size=5,
))

_sp(Spell(
    "protection-from-evil-and-good", "Protection from Evil and Good", 1, "abjuration",
    "1 action", 0, ["V", "S", "M"], "Concentration, up to 10 minutes", True,
    "Until the spell ends, one willing creature you touch is protected against aberrations, celestials, elementals, fey, fiends, and undead. They cannot charm, frighten, or possess the target.",
    ["cleric", "paladin", "warlock", "wizard"],
    effect_type="buff",
))

_sp(Spell(
    "detect-poison-and-disease", "Detect Poison and Disease", 1, "divination",
    "1 action", 0, ["V", "S", "M"], "Concentration, up to 10 minutes", True,
    "For the duration you can sense the presence and location of poisons, poisonous creatures, and diseases within 30 feet. You also identify the kind in each case.",
    ["cleric", "druid", "paladin", "ranger"],
    effect_type="utility",
))

_sp(Spell(
    "absorb-elements", "Absorb Elements", 1, "abjuration",
    "1 reaction", 0, ["S"], "1 round", False,
    "You capture some of the incoming energy. You have resistance to the triggering damage type until the start of your next turn. Your first melee attack on your next turn deals an extra 1d6 of that type.",
    ["druid", "ranger", "sorcerer", "wizard"],
    damage_dice="1d6", effect_type="buff",
    at_higher_levels="Extra damage increases by 1d6 for each slot level above 1st.",
))

_sp(Spell(
    "ice-knife", "Ice Knife", 1, "conjuration",
    "1 action", 60, ["S", "M"], "Instantaneous", False,
    "You create a shard of ice and fling it at one creature. Make a ranged spell attack dealing 1d10 piercing. Hit or miss it explodes: creatures within 5 ft must DEX save or take 2d6 cold.",
    ["druid", "sorcerer", "wizard"],
    damage_dice="1d10", damage_type="piercing", save_ability="DEX", effect_type="damage", area_type="single",
    at_higher_levels="Cold damage increases by 1d6 for each slot level above 1st.",
))

_sp(Spell(
    "catapult", "Catapult", 1, "transmutation",
    "1 action", 60, ["S"], "Instantaneous", False,
    "Choose one object weighing 1 to 5 pounds that is not worn or carried. The object flies in a straight line up to 90 feet. A creature in the path must DEX save or take 3d8 bludgeoning and the object stops.",
    ["sorcerer", "wizard"],
    damage_dice="3d8", damage_type="bludgeoning", save_ability="DEX", effect_type="damage", area_type="single",
    at_higher_levels="Max weight increases by 5 lbs and damage by 1d8 per slot level above 1st.",
))

_sp(Spell(
    "earth-tremor", "Earth Tremor", 1, "evocation",
    "1 action", 10, ["V", "S"], "Instantaneous", False,
    "You cause a tremor in the ground. Each creature other than you within 10 feet must make a DEX save. On fail take 1d6 bludgeoning and be knocked prone. Loose ground becomes difficult terrain.",
    ["bard", "druid", "sorcerer", "wizard"],
    damage_dice="1d6", damage_type="bludgeoning", save_ability="DEX", effect_type="damage",
    area_type="sphere", area_size=10,
    conditions_applied=["prone"],
    at_higher_levels="Damage increases by 1d6 for each slot level above 1st.",
))

_sp(Spell(
    "thunderous-smite", "Thunderous Smite", 1, "evocation",
    "1 bonus action", 0, ["V"], "Concentration, up to 1 minute", True,
    "The first time you hit with a melee weapon attack during this spell's duration, your weapon rings with thunder and deals an extra 2d6 thunder damage. Target must STR save or be pushed 10 ft and knocked prone.",
    ["paladin"],
    damage_dice="2d6", damage_type="thunder", save_ability="STR", effect_type="damage",
    conditions_applied=["prone"],
))

_sp(Spell(
    "wrathful-smite", "Wrathful Smite", 1, "evocation",
    "1 bonus action", 0, ["V"], "Concentration, up to 1 minute", True,
    "The next time you hit with a melee weapon attack during this spell's duration, your attack deals an extra 1d6 psychic damage. Target must WIS save or be frightened of you until the spell ends.",
    ["paladin"],
    damage_dice="1d6", damage_type="psychic", save_ability="WIS", effect_type="damage",
    conditions_applied=["frightened"],
))

_sp(Spell(
    "searing-smite", "Searing Smite", 1, "evocation",
    "1 bonus action", 0, ["V"], "Concentration, up to 1 minute", True,
    "The next time you hit a creature with a melee weapon attack, your weapon flares with white-hot intensity. The attack deals an extra 1d6 fire damage and sets the target on fire, dealing 1d6 fire damage at start of each of its turns until it or an ally uses an action to douse the flames.",
    ["paladin"],
    damage_dice="1d6", damage_type="fire", effect_type="damage",
    at_higher_levels="Initial extra damage increases by 1d6 for each slot level above 1st.",
))

_sp(Spell(
    "compelled-duel", "Compelled Duel", 1, "enchantment",
    "1 bonus action", 30, ["V"], "Concentration, up to 1 minute", True,
    "You attempt to compel a creature into a duel. Target must make a WIS save. On fail it has disadvantage on attacks against creatures other than you and must make a WIS save to move more than 30 ft from you.",
    ["paladin"],
    save_ability="WIS", effect_type="control",
))

_sp(Spell(
    "heroism", "Heroism", 1, "enchantment",
    "1 action", 0, ["V", "S"], "Concentration, up to 1 minute", True,
    "A willing creature you touch is imbued with bravery. Until the spell ends, the creature is immune to being frightened and gains temporary HP equal to your spellcasting ability modifier at the start of each of its turns.",
    ["bard", "paladin"],
    effect_type="buff",
    at_higher_levels="One additional creature for each slot level above 1st.",
))

_sp(Spell(
    "shield-of-faith", "Shield of Faith", 1, "abjuration",
    "1 bonus action", 60, ["V", "S", "M"], "Concentration, up to 10 minutes", True,
    "A shimmering field appears and surrounds a creature of your choice within range, granting it a +2 bonus to AC for the duration.",
    ["cleric", "paladin"],
    effect_type="buff",
))

_sp(Spell(
    "divine-favor", "Divine Favor", 1, "evocation",
    "1 bonus action", 0, ["V", "S"], "Concentration, up to 1 minute", True,
    "Your prayer empowers you with divine radiance. Until the spell ends, your weapon attacks deal an extra 1d4 radiant damage on a hit.",
    ["paladin"],
    damage_dice="1d4", damage_type="radiant", effect_type="buff",
))

_sp(Spell(
    "tashas-hideous-laughter", "Tasha's Hideous Laughter", 1, "enchantment",
    "1 action", 30, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "A creature of your choice must succeed on a WIS save or fall prone and become incapacitated, unable to stand up for the duration. Creatures with INT 4 or less are unaffected.",
    ["bard", "wizard"],
    save_ability="WIS", effect_type="control",
    conditions_applied=["prone", "incapacitated"],
))

_sp(Spell(
    "color-spray", "Color Spray", 1, "illusion",
    "1 action", 0, ["V", "S", "M"], "1 round", False,
    "A dazzling array of flashing, colored light springs from your hand. Roll 6d10; starting from lowest current HP, creatures in a 15-foot cone are blinded until the end of your next turn.",
    ["sorcerer", "wizard"],
    effect_type="control", area_type="cone", area_size=15,
    conditions_applied=["blinded"],
    at_higher_levels="Roll an additional 2d10 for each slot level above 1st.",
))

_sp(Spell(
    "grease", "Grease", 1, "conjuration",
    "1 action", 60, ["V", "S", "M"], "1 minute", False,
    "Slick grease covers the ground in a 10-foot square centered on a point within range. Each creature standing in the area must succeed on a DEX save or fall prone. It is difficult terrain.",
    ["wizard"],
    save_ability="DEX", effect_type="control", area_type="cube", area_size=10,
    conditions_applied=["prone"],
))

_sp(Spell(
    "snare", "Snare", 1, "abjuration",
    "1 minute", 0, ["S", "M"], "8 hours", False,
    "You create a magical trap using a length of rope. When triggered, the restrained creature must succeed on a DEX save or be yanked into the air, hanging upside down 3 feet above the ground.",
    ["druid", "ranger", "wizard"],
    save_ability="DEX", effect_type="control",
    conditions_applied=["restrained"],
))

_sp(Spell(
    "alarm", "Alarm", 1, "abjuration",
    "1 minute", 30, ["V", "S", "M"], "8 hours", False,
    "You set an alarm against unwanted intrusion. Choose a door, window, or area within range no larger than a 20-foot cube. An alarm alerts you when a Tiny or larger creature touches or enters the warded area.",
    ["ranger", "wizard"],
    effect_type="utility", area_type="cube", area_size=20,
))

_sp(Spell(
    "unseen-servant", "Unseen Servant", 1, "conjuration",
    "1 action", 60, ["V", "S", "M"], "1 hour", False,
    "This spell creates an invisible, mindless, shapeless force that performs simple tasks at your command. It has AC 10, 1 HP, STR 2. It can perform tasks such as fetching, cleaning, mending, and folding.",
    ["bard", "warlock", "wizard"],
    effect_type="summon",
))

_sp(Spell(
    "tensers-floating-disk", "Tenser's Floating Disk", 1, "conjuration",
    "1 action", 30, ["V", "S", "M"], "1 hour", False,
    "This spell creates a circular, horizontal plane of force 3 feet in diameter and 1 inch thick that floats 3 feet above the ground. It can hold up to 500 pounds.",
    ["wizard"],
    effect_type="utility",
))

_sp(Spell(
    "false-life", "False Life", 1, "necromancy",
    "1 action", 0, ["V", "S", "M"], "1 hour", False,
    "Bolstering yourself with a necromantic facsimile of life, you gain 1d4 + 4 temporary hit points for the duration.",
    ["sorcerer", "wizard"],
    effect_type="buff",
    at_higher_levels="You gain 5 additional temporary HP for each slot level above 1st.",
))

_sp(Spell(
    "ray-of-sickness", "Ray of Sickness", 1, "necromancy",
    "1 action", 60, ["V", "S"], "Instantaneous", False,
    "A ray of sickening greenish energy lashes out toward a creature within range. Make a ranged spell attack. On hit deal 2d8 poison damage and the target must make a CON save or also be poisoned until the end of your next turn.",
    ["sorcerer", "wizard"],
    damage_dice="2d8", damage_type="poison", save_ability="CON", effect_type="damage", area_type="single",
    conditions_applied=["poisoned"],
    at_higher_levels="Damage increases by 1d8 for each slot level above 1st.",
))


# ═══════════════════════════════════════════════════════════════
#  LEVEL 2  SPELLS
# ═══════════════════════════════════════════════════════════════

_sp(Spell(
    "scorching-ray", "Scorching Ray", 2, "evocation",
    "1 action", 120, ["V", "S"], "Instantaneous", False,
    "You create three rays of fire and hurl them at targets within range. Make a ranged spell attack for each ray. On hit deal 2d6 fire damage.",
    ["sorcerer", "wizard"],
    damage_dice="2d6", damage_type="fire", effect_type="damage", area_type="single",
    at_higher_levels="One additional ray for each slot level above 2nd.",
))

_sp(Spell(
    "hold-person", "Hold Person", 2, "enchantment",
    "1 action", 60, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "Choose a humanoid that you can see within range. The target must succeed on a WIS save or be paralyzed for the duration. It can repeat the save at the end of each of its turns.",
    ["bard", "cleric", "druid", "sorcerer", "warlock", "wizard"],
    save_ability="WIS", effect_type="control",
    conditions_applied=["paralyzed"],
    at_higher_levels="One additional humanoid for each slot level above 2nd.",
))

_sp(Spell(
    "spiritual-weapon", "Spiritual Weapon", 2, "evocation",
    "1 bonus action", 60, ["V", "S"], "1 minute", False,
    "You create a floating spectral weapon within range that lasts for the duration. When you cast the spell you can make a melee spell attack against a creature within 5 ft of the weapon dealing 1d8 + spellcasting modifier force damage. As a bonus action on your turn you can move the weapon and attack again.",
    ["cleric"],
    damage_dice="1d8", damage_type="force", effect_type="damage",
    at_higher_levels="Damage increases by 1d8 for every two slot levels above 2nd.",
))

_sp(Spell(
    "misty-step", "Misty Step", 2, "conjuration",
    "1 bonus action", 0, ["V"], "Instantaneous", False,
    "Briefly surrounded by silvery mist, you teleport up to 30 feet to an unoccupied space that you can see.",
    ["sorcerer", "warlock", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "shatter", "Shatter", 2, "evocation",
    "1 action", 60, ["V", "S", "M"], "Instantaneous", False,
    "A sudden loud ringing noise erupts from a point of your choice within range. Each creature in a 10-foot-radius sphere centered on that point must make a CON save. On fail take 3d8 thunder damage, half on success. Inorganic creatures have disadvantage.",
    ["bard", "sorcerer", "warlock", "wizard"],
    damage_dice="3d8", damage_type="thunder", save_ability="CON", effect_type="damage",
    area_type="sphere", area_size=10,
    at_higher_levels="Damage increases by 1d8 for each slot level above 2nd.",
))

_sp(Spell(
    "web", "Web", 2, "conjuration",
    "1 action", 60, ["V", "S", "M"], "Concentration, up to 1 hour", True,
    "You conjure a mass of thick, sticky webbing at a point of your choice within range in a 20-foot cube. The webs are difficult terrain and lightly obscure the area. Creatures starting turn in or entering must DEX save or be restrained.",
    ["sorcerer", "wizard"],
    save_ability="DEX", effect_type="control", area_type="cube", area_size=20,
    conditions_applied=["restrained"],
))

_sp(Spell(
    "mirror-image", "Mirror Image", 2, "illusion",
    "1 action", 0, ["V", "S"], "1 minute", False,
    "Three illusory duplicates of yourself appear. Each time a creature targets you with an attack, roll d20 to determine if the attack targets a duplicate instead (depends on number of duplicates remaining). A duplicate has AC 10 + DEX modifier and is destroyed if hit.",
    ["sorcerer", "warlock", "wizard"],
    effect_type="buff",
))

_sp(Spell(
    "invisibility", "Invisibility", 2, "illusion",
    "1 action", 0, ["V", "S", "M"], "Concentration, up to 1 hour", True,
    "A creature you touch becomes invisible until the spell ends. Anything the target is wearing or carrying is invisible as long as it is on the target's person. The spell ends for a target that attacks or casts a spell.",
    ["bard", "sorcerer", "warlock", "wizard"],
    effect_type="buff",
    conditions_applied=["invisible"],
    at_higher_levels="One additional creature for each slot level above 2nd.",
))

_sp(Spell(
    "suggestion", "Suggestion", 2, "enchantment",
    "1 action", 30, ["V", "M"], "Concentration, up to 8 hours", True,
    "You suggest a course of activity (limited to a sentence or two) to a creature within range. Target must WIS save. On fail it pursues the course of action you described to the best of its ability. The suggestion must be worded to sound reasonable.",
    ["bard", "sorcerer", "warlock", "wizard"],
    save_ability="WIS", effect_type="control",
))

_sp(Spell(
    "enhance-ability", "Enhance Ability", 2, "transmutation",
    "1 action", 0, ["V", "S", "M"], "Concentration, up to 1 hour", True,
    "You touch a creature and bestow upon it a magical enhancement. Choose one: Bear (advantage on STR checks, +2d6 carry capacity), Bull (advantage on STR checks), Cat (advantage on DEX checks, no fall damage from 20 ft or less), Eagle (advantage on CHA checks), Fox (advantage on INT checks), Owl (advantage on WIS checks).",
    ["bard", "cleric", "druid", "ranger", "sorcerer", "wizard"],
    effect_type="buff",
    at_higher_levels="One additional creature for each slot level above 2nd.",
))

_sp(Spell(
    "lesser-restoration", "Lesser Restoration", 2, "abjuration",
    "1 action", 0, ["V", "S"], "Instantaneous", False,
    "You touch a creature and can end either one disease or one condition afflicting it. The condition can be blinded, deafened, paralyzed, or poisoned.",
    ["bard", "cleric", "druid", "paladin", "ranger"],
    effect_type="healing",
))

_sp(Spell(
    "aid", "Aid", 2, "abjuration",
    "1 action", 30, ["V", "S", "M"], "8 hours", False,
    "Your spell bolsters your allies with toughness and resolve. Choose up to three creatures within range. Each target's hit point maximum and current hit points increase by 5 for the duration.",
    ["bard", "cleric", "paladin", "ranger"],
    effect_type="buff",
    at_higher_levels="Each target's HP increase rises by 5 for each slot level above 2nd.",
))

_sp(Spell(
    "blindness-deafness", "Blindness/Deafness", 2, "necromancy",
    "1 action", 30, ["V"], "1 minute", False,
    "You can blind or deafen a foe. Choose one creature. It must succeed on a CON save or be either blinded or deafened (your choice) for the duration. It can repeat the save at end of each turn.",
    ["bard", "cleric", "sorcerer", "wizard"],
    save_ability="CON", effect_type="debuff",
    conditions_applied=["blinded"],
    at_higher_levels="One additional creature for each slot level above 2nd.",
))

_sp(Spell(
    "silence", "Silence", 2, "illusion",
    "1 action", 120, ["V", "S"], "Concentration, up to 10 minutes", True,
    "For the duration, no sound can be created within or pass through a 20-foot-radius sphere centered on a point you choose within range. Creatures inside are immune to thunder damage. Verbal spell components impossible.",
    ["bard", "cleric", "ranger"],
    effect_type="control", area_type="sphere", area_size=20,
    conditions_applied=["deafened"],
))

_sp(Spell(
    "moonbeam", "Moonbeam", 2, "evocation",
    "1 action", 120, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "A silvery beam of pale light shines down in a 5-foot-radius, 40-foot-high cylinder centered on a point within range. A creature that enters or starts its turn there must make a CON save or take 2d10 radiant damage, half on success. Shapechangers have disadvantage.",
    ["druid"],
    damage_dice="2d10", damage_type="radiant", save_ability="CON", effect_type="damage",
    area_type="cylinder", area_size=5,
    at_higher_levels="Damage increases by 1d10 for each slot level above 2nd.",
))

_sp(Spell(
    "heat-metal", "Heat Metal", 2, "transmutation",
    "1 action", 60, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "Choose a manufactured metal object within range. It glows red-hot. A creature in contact takes 2d8 fire damage when you cast the spell. As a bonus action on subsequent turns you can cause the damage again. If holding, must CON save or drop it.",
    ["bard", "druid"],
    damage_dice="2d8", damage_type="fire", save_ability="CON", effect_type="damage",
    at_higher_levels="Damage increases by 1d8 for each slot level above 2nd.",
))

_sp(Spell(
    "spike-growth", "Spike Growth", 2, "transmutation",
    "1 action", 150, ["V", "S", "M"], "Concentration, up to 10 minutes", True,
    "The ground in a 20-foot radius centered on a point within range twists and sprouts hard spikes and thorns. The area becomes difficult terrain. When a creature moves through the area, it takes 2d4 piercing damage for every 5 feet it travels.",
    ["druid", "ranger"],
    damage_dice="2d4", damage_type="piercing", effect_type="control",
    area_type="sphere", area_size=20,
))

_sp(Spell(
    "flame-blade", "Flame Blade", 2, "evocation",
    "1 bonus action", 0, ["V", "S", "M"], "Concentration, up to 10 minutes", True,
    "You evoke a fiery blade in your free hand. The blade is similar in size and shape to a scimitar. You can use your action to make a melee spell attack dealing 3d6 fire damage on a hit. It sheds bright light in a 10-foot radius.",
    ["druid"],
    damage_dice="3d6", damage_type="fire", effect_type="damage",
    at_higher_levels="Damage increases by 1d6 for every two slot levels above 2nd.",
))

_sp(Spell(
    "pass-without-trace", "Pass Without Trace", 2, "abjuration",
    "1 action", 0, ["V", "S", "M"], "Concentration, up to 1 hour", True,
    "A veil of shadows and silence radiates from you, masking you and your companions from detection. Each creature you choose within 30 feet has a +10 bonus to DEX (Stealth) checks and can't be tracked except by magical means.",
    ["druid", "ranger"],
    effect_type="buff",
))

_sp(Spell(
    "darkvision", "Darkvision", 2, "transmutation",
    "1 action", 0, ["V", "S", "M"], "8 hours", False,
    "You touch a willing creature to grant it the ability to see in the dark. For the duration, that creature has darkvision out to a range of 60 feet.",
    ["druid", "ranger", "sorcerer", "wizard"],
    effect_type="buff",
))

_sp(Spell(
    "find-traps", "Find Traps", 2, "divination",
    "1 action", 120, ["V", "S"], "Instantaneous", False,
    "You sense the presence of any trap within range. You don't learn the location of each trap, but you do learn the general nature of the danger posed.",
    ["cleric", "druid", "ranger"],
    effect_type="utility",
))

_sp(Spell(
    "prayer-of-healing", "Prayer of Healing", 2, "evocation",
    "10 minutes", 30, ["V"], "Instantaneous", False,
    "Up to six creatures of your choice that you can see within range each regain hit points equal to 2d8 + your spellcasting ability modifier.",
    ["cleric", "paladin"],
    healing_dice="2d8", effect_type="healing",
    at_higher_levels="Healing increases by 1d8 for each slot level above 2nd.",
))

_sp(Spell(
    "calm-emotions", "Calm Emotions", 2, "enchantment",
    "1 action", 60, ["V", "S"], "Concentration, up to 1 minute", True,
    "You attempt to suppress strong emotions in a group of people. Each humanoid in a 20-foot-radius sphere must make a CHA save. On fail, you can suppress any effect causing a target to be charmed or frightened, or make a target indifferent about hostile creatures.",
    ["bard", "cleric"],
    save_ability="CHA", effect_type="control", area_type="sphere", area_size=20,
))

_sp(Spell(
    "detect-thoughts", "Detect Thoughts", 2, "divination",
    "1 action", 0, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "For the duration you can read the thoughts of certain creatures. You initially learn the surface thoughts of any creature within 30 feet. As an action you can probe deeper, requiring a WIS save.",
    ["bard", "sorcerer", "wizard"],
    save_ability="WIS", effect_type="utility",
))

_sp(Spell(
    "see-invisibility", "See Invisibility", 2, "divination",
    "1 action", 0, ["V", "S", "M"], "1 hour", False,
    "For the duration you see invisible creatures and objects as if they were visible, and you can see into the Ethereal Plane.",
    ["bard", "sorcerer", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "locate-object", "Locate Object", 2, "divination",
    "1 action", 0, ["V", "S", "M"], "Concentration, up to 10 minutes", True,
    "Describe or name an object that is familiar to you. You sense the direction to the object's location, as long as that object is within 1,000 feet of you.",
    ["bard", "cleric", "druid", "paladin", "ranger", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "arcane-lock", "Arcane Lock", 2, "abjuration",
    "1 action", 0, ["V", "S", "M"], "Until dispelled", False,
    "You touch a closed door, window, gate, chest, or other entryway. It becomes locked for the duration. You and creatures you designate can open the object normally. DC to break or pick the lock increases by 10.",
    ["wizard"],
    effect_type="utility",
))

_sp(Spell(
    "knock", "Knock", 2, "transmutation",
    "1 action", 60, ["V"], "Instantaneous", False,
    "Choose an object that you can see within range. The object can be a door, box, chest, shackles, padlock, or other object with a mundane or magical means that prevents access. A target held shut by a mundane lock or stuck/barred becomes unlocked, unstuck, or unbarred.",
    ["bard", "sorcerer", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "levitate", "Levitate", 2, "transmutation",
    "1 action", 60, ["V", "S", "M"], "Concentration, up to 10 minutes", True,
    "One creature or loose object of your choice that you can see within range rises vertically up to 20 feet and remains suspended. An unwilling creature must succeed on a CON save.",
    ["sorcerer", "wizard"],
    save_ability="CON", effect_type="control",
))

_sp(Spell(
    "alter-self", "Alter Self", 2, "transmutation",
    "1 action", 0, ["V", "S"], "Concentration, up to 1 hour", True,
    "You assume a different form. Choose: Aquatic Adaptation (gills, swim speed), Change Appearance (alter form), or Natural Weapons (claws/fangs/horns dealing 1d6+STR).",
    ["sorcerer", "wizard"],
    effect_type="buff",
))

_sp(Spell(
    "blur", "Blur", 2, "illusion",
    "1 action", 0, ["V"], "Concentration, up to 1 minute", True,
    "Your body becomes blurred, shifting and wavering to all who can see you. For the duration, any creature has disadvantage on attack rolls against you. Creatures that don't rely on sight or can see through illusions are unaffected.",
    ["sorcerer", "wizard"],
    effect_type="buff",
))

_sp(Spell(
    "crown-of-madness", "Crown of Madness", 2, "enchantment",
    "1 action", 120, ["V", "S"], "Concentration, up to 1 minute", True,
    "One humanoid of your choice must succeed on a WIS save or become charmed by you for the duration. The charmed target must use its action before moving on each of its turns to make a melee attack against a creature other than itself that you mentally choose.",
    ["bard", "sorcerer", "warlock", "wizard"],
    save_ability="WIS", effect_type="control",
    conditions_applied=["charmed"],
))

_sp(Spell(
    "phantasmal-force", "Phantasmal Force", 2, "illusion",
    "1 action", 60, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "You craft an illusion that takes root in the mind of a creature that you can see within range. Target must make an INT save. On fail, you create a phantasmal object, creature, or other visible phenomenon no larger than a 10-foot cube. The target treats the phantasm as real and takes 1d6 psychic damage each turn.",
    ["bard", "sorcerer", "wizard"],
    damage_dice="1d6", damage_type="psychic", save_ability="INT", effect_type="damage",
    area_type="cube", area_size=10,
))

_sp(Spell(
    "enlarge-reduce", "Enlarge/Reduce", 2, "transmutation",
    "1 action", 30, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "You cause a creature or an object you can see within range to grow larger or smaller for the duration. An unwilling creature can make a CON save. Enlarge: advantage on STR checks/saves, +1d4 weapon damage. Reduce: disadvantage on STR checks/saves, -1d4 weapon damage.",
    ["sorcerer", "wizard"],
    save_ability="CON", effect_type="buff",
))

_sp(Spell(
    "flaming-sphere", "Flaming Sphere", 2, "conjuration",
    "1 action", 60, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "A 5-foot-diameter sphere of fire appears in an unoccupied space within range and lasts for the duration. Any creature that ends its turn within 5 feet of the sphere must make a DEX save, taking 2d6 fire damage on a fail, or half on success. As a bonus action you can move the sphere up to 30 feet.",
    ["druid", "wizard"],
    damage_dice="2d6", damage_type="fire", save_ability="DEX", effect_type="damage",
    area_type="sphere", area_size=5,
    at_higher_levels="Damage increases by 1d6 for each slot level above 2nd.",
))

_sp(Spell(
    "gust-of-wind", "Gust of Wind", 2, "evocation",
    "1 action", 0, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "A line of strong wind 60 feet long and 10 feet wide blasts from you in a direction you choose for the spell's duration. Each creature that starts its turn in the line must succeed on a STR save or be pushed 15 feet away from you. Moving toward you in the line costs double movement.",
    ["druid", "sorcerer", "wizard"],
    save_ability="STR", effect_type="control", area_type="line", area_size=60,
))

_sp(Spell(
    "magic-weapon", "Magic Weapon", 2, "transmutation",
    "1 bonus action", 0, ["V", "S"], "Concentration, up to 1 hour", True,
    "You touch a nonmagical weapon. Until the spell ends, that weapon becomes a magic weapon with a +1 bonus to attack rolls and damage rolls.",
    ["paladin", "wizard"],
    effect_type="buff",
    at_higher_levels="+2 bonus at 4th level slot, +3 at 6th level slot.",
))

_sp(Spell(
    "cloud-of-daggers", "Cloud of Daggers", 2, "conjuration",
    "1 action", 60, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "You fill the air with spinning daggers in a 5-foot cube you choose within range. A creature takes 4d4 slashing damage when it enters the area for the first time on a turn or starts its turn there.",
    ["bard", "sorcerer", "warlock", "wizard"],
    damage_dice="4d4", damage_type="slashing", effect_type="damage",
    area_type="cube", area_size=5,
    at_higher_levels="Damage increases by 2d4 for each slot level above 2nd.",
))

_sp(Spell(
    "melfs-acid-arrow", "Melf's Acid Arrow", 2, "evocation",
    "1 action", 90, ["V", "S", "M"], "Instantaneous", False,
    "A shimmering green arrow streaks toward a target within range. Make a ranged spell attack. On hit deal 4d4 acid damage immediately and 2d4 at the end of its next turn. On miss deal half initial damage and no ongoing damage.",
    ["wizard"],
    damage_dice="4d4", damage_type="acid", effect_type="damage", area_type="single",
    at_higher_levels="Both initial and ongoing damage increase by 1d4 for each slot level above 2nd.",
))

_sp(Spell(
    "rope-trick", "Rope Trick", 2, "transmutation",
    "1 action", 0, ["V", "S", "M"], "1 hour", False,
    "You touch a length of rope up to 60 feet long. One end rises into the air until the whole rope hangs perpendicular to the ground. At the upper end, an invisible entrance opens to an extradimensional space that can hold up to eight Medium or smaller creatures.",
    ["wizard"],
    effect_type="utility",
))

_sp(Spell(
    "gentle-repose", "Gentle Repose", 2, "necromancy",
    "1 action", 0, ["V", "S", "M"], "10 days", False,
    "You touch a corpse or other remains. For the duration, the target is protected from decay and can't become undead. The spell also extends the time limit on raising the target from the dead.",
    ["cleric", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "warding-bond", "Warding Bond", 2, "abjuration",
    "1 action", 0, ["V", "S", "M"], "1 hour", False,
    "This spell wards a willing creature you touch and creates a mystic connection. The target gets +1 to AC and saving throws, and has resistance to all damage. Each time the target takes damage, you take the same amount.",
    ["cleric"],
    effect_type="buff",
))

_sp(Spell(
    "zone-of-truth", "Zone of Truth", 2, "enchantment",
    "1 action", 60, ["V", "S"], "10 minutes", False,
    "You create a magical zone that guards against deception in a 15-foot-radius sphere centered on a point. A creature that enters the area must make a CHA save. On fail it cannot deliberately lie while in the area.",
    ["bard", "cleric", "paladin"],
    save_ability="CHA", effect_type="control", area_type="sphere", area_size=15,
))

_sp(Spell(
    "branding-smite", "Branding Smite", 2, "evocation",
    "1 bonus action", 0, ["V"], "Concentration, up to 1 minute", True,
    "The next time you hit a creature with a weapon attack before this spell ends, the weapon gleams with astral radiance as you strike. The attack deals an extra 2d6 radiant damage. The target becomes visible if it's invisible.",
    ["paladin"],
    damage_dice="2d6", damage_type="radiant", effect_type="damage",
    at_higher_levels="Damage increases by 1d6 for each slot level above 2nd.",
))

_sp(Spell(
    "find-steed", "Find Steed", 2, "conjuration",
    "10 minutes", 30, ["V", "S"], "Instantaneous", False,
    "You summon a spirit that assumes the form of an unusually intelligent, strong, and loyal steed, establishing a lasting bond with it. The steed takes the form you choose: warhorse, pony, camel, elk, or mastiff.",
    ["paladin"],
    effect_type="summon",
))

_sp(Spell(
    "magic-mouth", "Magic Mouth", 2, "illusion",
    "1 minute", 30, ["V", "S", "M"], "Until dispelled", False,
    "You implant a message within an object. The message is spoken whenever a trigger condition is met. The mouth can't cast spells or activate magic items. Up to 25 words over 10 minutes.",
    ["bard", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "nystuls-magic-aura", "Nystul's Magic Aura", 2, "illusion",
    "1 action", 0, ["V", "S", "M"], "24 hours", False,
    "You place an illusion on a creature or an object you touch so that divination spells reveal false information about it. You can change how the target appears to spells and magical effects that detect creature types or the school of magic.",
    ["wizard"],
    effect_type="utility",
))

_sp(Spell(
    "ray-of-enfeeblement", "Ray of Enfeeblement", 2, "necromancy",
    "1 action", 60, ["V", "S"], "Concentration, up to 1 minute", True,
    "A black beam of enervating energy springs from your finger toward a creature within range. Make a ranged spell attack. On hit, the target deals only half damage with weapon attacks that use STR. Target can make a CON save at the end of each of its turns to end the effect.",
    ["warlock", "wizard"],
    effect_type="debuff",
))

_sp(Spell(
    "dragons-breath", "Dragon's Breath", 2, "transmutation",
    "1 bonus action", 0, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "You touch one willing creature and imbue it with the power to spew magical energy from its mouth. Choose acid, cold, fire, lightning, or poison. The creature can use an action to exhale energy in a 15-foot cone. Each creature in the area must make a DEX save, taking 3d6 damage on a fail, half on success.",
    ["sorcerer", "wizard"],
    damage_dice="3d6", save_ability="DEX", effect_type="buff", area_type="cone", area_size=15,
    at_higher_levels="Damage increases by 1d6 for each slot level above 2nd.",
))

_sp(Spell(
    "shadow-blade", "Shadow Blade", 2, "illusion",
    "1 bonus action", 0, ["V", "S"], "Concentration, up to 1 minute", True,
    "You weave together threads of shadow to create a sword of solidified gloom in your hand. This magic sword has finesse, light, and thrown (range 20/60) properties. It deals 2d8 psychic damage on a hit. You have advantage on attack rolls with it in dim light or darkness.",
    ["sorcerer", "warlock", "wizard"],
    damage_dice="2d8", damage_type="psychic", effect_type="damage",
    at_higher_levels="Damage increases by 1d8 for every two slot levels above 2nd.",
))

_sp(Spell(
    "mind-spike", "Mind Spike", 2, "divination",
    "1 action", 60, ["S"], "Concentration, up to 1 hour", True,
    "You reach into the mind of one creature you can see within range. The target must make a WIS save, taking 3d8 psychic damage on a fail, or half on success. On a failed save, you always know the target's location while the spell lasts.",
    ["sorcerer", "warlock", "wizard"],
    damage_dice="3d8", damage_type="psychic", save_ability="WIS", effect_type="damage", area_type="single",
    at_higher_levels="Damage increases by 1d8 for each slot level above 2nd.",
))


# ═══════════════════════════════════════════════════════════════
#  LEVEL 3  SPELLS
# ═══════════════════════════════════════════════════════════════

_sp(Spell(
    "fireball", "Fireball", 3, "evocation",
    "1 action", 150, ["V", "S", "M"], "Instantaneous", False,
    "A bright streak flashes from your pointing finger to a point within range and then blossoms with a low roar into an explosion of flame. Each creature in a 20-foot-radius sphere must make a DEX save. On fail take 8d6 fire damage, half on success. Ignites flammable objects not being worn or carried.",
    ["sorcerer", "wizard"],
    damage_dice="8d6", damage_type="fire", save_ability="DEX", effect_type="damage",
    area_type="sphere", area_size=20,
    at_higher_levels="Damage increases by 1d6 for each slot level above 3rd.",
))

_sp(Spell(
    "lightning-bolt", "Lightning Bolt", 3, "evocation",
    "1 action", 0, ["V", "S", "M"], "Instantaneous", False,
    "A stroke of lightning forming a line 100 feet long and 5 feet wide blasts out from you. Each creature in the line must make a DEX save. On fail take 8d6 lightning damage, half on success.",
    ["sorcerer", "wizard"],
    damage_dice="8d6", damage_type="lightning", save_ability="DEX", effect_type="damage",
    area_type="line", area_size=100,
    at_higher_levels="Damage increases by 1d6 for each slot level above 3rd.",
))

_sp(Spell(
    "counterspell", "Counterspell", 3, "abjuration",
    "1 reaction", 60, ["S"], "Instantaneous", False,
    "You attempt to interrupt a creature in the process of casting a spell. If the creature is casting a spell of 3rd level or lower, its spell fails. If it is casting a spell of 4th level or higher, make an ability check using your spellcasting ability (DC 10 + the spell's level).",
    ["sorcerer", "warlock", "wizard"],
    effect_type="utility",
    at_higher_levels="Spell automatically countered if its level is equal to or less than the slot used.",
))

_sp(Spell(
    "dispel-magic", "Dispel Magic", 3, "abjuration",
    "1 action", 120, ["V", "S"], "Instantaneous", False,
    "Choose one creature, object, or magical effect within range. Any spell of 3rd level or lower on the target ends. For each spell of 4th level or higher, make an ability check using your spellcasting ability (DC 10 + the spell's level). On success the spell ends.",
    ["bard", "cleric", "druid", "paladin", "sorcerer", "warlock", "wizard"],
    effect_type="utility",
    at_higher_levels="Automatically ends effects of the slot level used or lower.",
))

_sp(Spell(
    "fly", "Fly", 3, "transmutation",
    "1 action", 0, ["V", "S", "M"], "Concentration, up to 10 minutes", True,
    "You touch a willing creature. The target gains a flying speed of 60 feet for the duration. When the spell ends, the target falls if it is still aloft.",
    ["sorcerer", "warlock", "wizard"],
    effect_type="buff",
    at_higher_levels="One additional creature for each slot level above 3rd.",
))

_sp(Spell(
    "haste", "Haste", 3, "transmutation",
    "1 action", 30, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "Choose a willing creature that you can see within range. Until the spell ends, the target's speed is doubled, it gains a +2 bonus to AC, it has advantage on DEX saves, and it gains an additional action on each of its turns (Attack (one weapon attack only), Dash, Disengage, Hide, or Use an Object). When the spell ends, the target can't move or take actions until after its next turn.",
    ["sorcerer", "wizard"],
    effect_type="buff",
))

_sp(Spell(
    "spirit-guardians", "Spirit Guardians", 3, "conjuration",
    "1 action", 0, ["V", "S", "M"], "Concentration, up to 10 minutes", True,
    "You call forth spirits to protect you. They flit around you to a distance of 15 feet for the duration. Any hostile creature that enters the area or starts its turn there must make a WIS save or take 3d8 radiant (or necrotic if you are evil) damage, half on success. Affected area is difficult terrain.",
    ["cleric"],
    damage_dice="3d8", damage_type="radiant", save_ability="WIS", effect_type="damage",
    area_type="sphere", area_size=15,
    at_higher_levels="Damage increases by 1d8 for each slot level above 3rd.",
))

_sp(Spell(
    "revivify", "Revivify", 3, "necromancy",
    "1 action", 0, ["V", "S", "M"], "Instantaneous", False,
    "You touch a creature that has died within the last minute. That creature returns to life with 1 hit point. This spell can't return to life a creature that has died of old age, nor can it restore any missing body parts.",
    ["cleric", "paladin", "druid", "ranger"],
    effect_type="healing",
))

_sp(Spell(
    "mass-healing-word", "Mass Healing Word", 3, "evocation",
    "1 bonus action", 60, ["V"], "Instantaneous", False,
    "As you call out words of restoration, up to six creatures of your choice that you can see within range regain hit points equal to 1d4 + your spellcasting ability modifier.",
    ["cleric", "bard"],
    healing_dice="1d4", effect_type="healing",
    at_higher_levels="Healing increases by 1d4 for each slot level above 3rd.",
))

_sp(Spell(
    "beacon-of-hope", "Beacon of Hope", 3, "abjuration",
    "1 action", 30, ["V", "S"], "Concentration, up to 1 minute", True,
    "This spell bestows hope and vitality. Choose any number of creatures within range. For the duration, each target has advantage on WIS saves and death saving throws, and regains the maximum number of hit points possible from any healing.",
    ["cleric"],
    effect_type="buff",
))

_sp(Spell(
    "bestow-curse", "Bestow Curse", 3, "necromancy",
    "1 action", 0, ["V", "S"], "Concentration, up to 1 minute", True,
    "You touch a creature, and that creature must succeed on a WIS save or become cursed for the duration. You choose the nature of the curse from options such as disadvantage on an ability's checks and saves, disadvantage on attacks against you, WIS save each turn or waste action, or extra 1d8 necrotic on your attacks.",
    ["bard", "cleric", "wizard"],
    save_ability="WIS", effect_type="debuff",
    at_higher_levels="Duration increases: 10 min at 4th, 8 hours at 5th, 24 hours at 7th, until dispelled at 9th.",
))

_sp(Spell(
    "animate-dead", "Animate Dead", 3, "necromancy",
    "1 minute", 10, ["V", "S", "M"], "Instantaneous", False,
    "This spell creates an undead servant. Choose a pile of bones or a corpse of a Medium or Small humanoid within range. Your spell imbues the target with a foul mimicry of life, raising it as an undead creature (skeleton if bones, zombie if corpse).",
    ["cleric", "wizard"],
    effect_type="summon",
    at_higher_levels="Animate or reassert control over two additional undead for each slot level above 3rd.",
))

_sp(Spell(
    "fear", "Fear", 3, "illusion",
    "1 action", 0, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "You project a phantasmal image of a creature's worst fears. Each creature in a 30-foot cone must succeed on a WIS save or drop whatever it is holding and become frightened for the duration. While frightened, the creature must take the Dash action and move away from you on each of its turns.",
    ["bard", "sorcerer", "warlock", "wizard"],
    save_ability="WIS", effect_type="control", area_type="cone", area_size=30,
    conditions_applied=["frightened"],
))

_sp(Spell(
    "hypnotic-pattern", "Hypnotic Pattern", 3, "illusion",
    "1 action", 120, ["S", "M"], "Concentration, up to 1 minute", True,
    "You create a twisting pattern of colors that weaves through the air inside a 30-foot cube within range. Each creature in the area that sees the pattern must make a WIS save. On fail, the creature becomes charmed and incapacitated, and its speed becomes 0.",
    ["bard", "sorcerer", "warlock", "wizard"],
    save_ability="WIS", effect_type="control", area_type="cube", area_size=30,
    conditions_applied=["charmed", "incapacitated"],
))

_sp(Spell(
    "major-image", "Major Image", 3, "illusion",
    "1 action", 120, ["V", "S", "M"], "Concentration, up to 10 minutes", True,
    "You create the image of an object, a creature, or some other visible phenomenon that is no larger than a 20-foot cube. It seems completely real, including sounds, smells, and temperature. Physical interaction reveals it as an illusion.",
    ["bard", "sorcerer", "warlock", "wizard"],
    effect_type="utility", area_type="cube", area_size=20,
    at_higher_levels="At 6th level or higher, the spell lasts until dispelled without concentration.",
))

_sp(Spell(
    "slow", "Slow", 3, "transmutation",
    "1 action", 120, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "You alter time around up to six creatures of your choice in a 40-foot cube. Each target must succeed on a WIS save. On fail, target's speed is halved, takes -2 to AC and DEX saves, and can't use reactions. On its turn it can use either an action or a bonus action, not both.",
    ["sorcerer", "wizard"],
    save_ability="WIS", effect_type="debuff", area_type="cube", area_size=40,
))

_sp(Spell(
    "call-lightning", "Call Lightning", 3, "conjuration",
    "1 action", 120, ["V", "S"], "Concentration, up to 10 minutes", True,
    "A storm cloud appears in the shape of a cylinder that is 10 feet tall with a 60-foot radius. When you cast the spell and as an action each round, you call a bolt of lightning from the cloud. Each creature within 5 feet of the point must make a DEX save or take 3d10 lightning damage, half on success.",
    ["druid"],
    damage_dice="3d10", damage_type="lightning", save_ability="DEX", effect_type="damage",
    area_type="cylinder", area_size=60,
    at_higher_levels="Damage increases by 1d10 for each slot level above 3rd.",
))

_sp(Spell(
    "conjure-animals", "Conjure Animals", 3, "conjuration",
    "1 action", 60, ["V", "S"], "Concentration, up to 1 hour", True,
    "You summon fey spirits that take the form of beasts. Choose one of: one beast of CR 2 or lower, two beasts of CR 1 or lower, four beasts of CR 1/2 or lower, or eight beasts of CR 1/4 or lower.",
    ["druid", "ranger"],
    effect_type="summon",
    at_higher_levels="Summon twice as many beasts at 5th level, three times at 7th, four times at 9th.",
))

_sp(Spell(
    "plant-growth", "Plant Growth", 3, "transmutation",
    "1 action", 150, ["V", "S"], "Instantaneous", False,
    "This spell channels vitality into plants. Choose either rapid growth (100-foot radius, plants become thick, a creature must spend 4 feet of movement for every 1 foot it moves) or enrichment (half-mile radius, plants yield double harvest for 1 year).",
    ["bard", "druid", "ranger"],
    effect_type="control", area_type="sphere", area_size=100,
))

_sp(Spell(
    "speak-with-dead", "Speak with Dead", 3, "necromancy",
    "1 action", 10, ["V", "S", "M"], "10 minutes", False,
    "You grant the semblance of life and intelligence to a corpse of your choice within range, allowing it to answer up to five questions. The corpse knows only what it knew in life.",
    ["bard", "cleric"],
    effect_type="utility",
))

_sp(Spell(
    "clairvoyance", "Clairvoyance", 3, "divination",
    "10 minutes", -1, ["V", "S", "M"], "Concentration, up to 10 minutes", True,
    "You create an invisible sensor within 1 mile of you in a location familiar to you or in an obvious location. For the duration, you can see or hear (your choice when you cast) through the sensor.",
    ["bard", "cleric", "sorcerer", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "sending", "Sending", 3, "evocation",
    "1 action", -1, ["V", "S", "M"], "1 round", False,
    "You send a short message of twenty-five words or less to a creature with which you are familiar. The creature hears the message in its mind, recognizes you as the sender if it knows you, and can answer in a like manner immediately.",
    ["bard", "cleric", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "water-breathing", "Water Breathing", 3, "transmutation",
    "1 action", 30, ["V", "S", "M"], "24 hours", False,
    "This spell grants up to ten willing creatures you can see within range the ability to breathe underwater until the spell ends. Affected creatures also retain their normal mode of respiration.",
    ["druid", "ranger", "sorcerer", "wizard"],
    effect_type="buff",
))

_sp(Spell(
    "tongues", "Tongues", 3, "divination",
    "1 action", 0, ["V", "M"], "1 hour", False,
    "This spell grants the creature you touch the ability to understand any spoken language it hears. Moreover, when the target speaks, any creature that knows at least one language and can hear the target understands what it says.",
    ["bard", "cleric", "sorcerer", "warlock", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "remove-curse", "Remove Curse", 3, "abjuration",
    "1 action", 0, ["V", "S"], "Instantaneous", False,
    "At your touch, all curses affecting one creature or object end. If the object is a cursed magic item, its curse remains, but the spell breaks its owner's attunement to the object so it can be removed or discarded.",
    ["cleric", "paladin", "warlock", "wizard"],
    effect_type="healing",
))

_sp(Spell(
    "protection-from-energy", "Protection from Energy", 3, "abjuration",
    "1 action", 0, ["V", "S"], "Concentration, up to 1 hour", True,
    "For the duration, the willing creature you touch has resistance to one damage type of your choice: acid, cold, fire, lightning, or thunder.",
    ["cleric", "druid", "ranger", "sorcerer", "wizard"],
    effect_type="buff",
))

_sp(Spell(
    "daylight", "Daylight", 3, "evocation",
    "1 action", 60, ["V", "S"], "1 hour", False,
    "A 60-foot-radius sphere of light spreads out from a point you choose within range. The sphere is bright light and sheds dim light for an additional 60 feet. If the point is on an object, the light moves with it.",
    ["cleric", "druid", "paladin", "ranger", "sorcerer"],
    effect_type="utility", area_type="sphere", area_size=60,
))

_sp(Spell(
    "create-food-and-water", "Create Food and Water", 3, "conjuration",
    "1 action", 30, ["V", "S"], "Instantaneous", False,
    "You create 45 pounds of food and 30 gallons of water on the ground or in containers within range, enough to sustain up to fifteen humanoids or five steeds for 24 hours.",
    ["cleric", "paladin"],
    effect_type="utility",
))

_sp(Spell(
    "glyph-of-warding", "Glyph of Warding", 3, "abjuration",
    "1 hour", 0, ["V", "S", "M"], "Until dispelled or triggered", False,
    "When you cast this spell, you inscribe a glyph that later unleashes a magical effect. You can store a prepared spell of 3rd level or lower in the glyph (Spell Glyph) or create an explosive runes effect (5d8 acid, cold, fire, lightning, or thunder in 20-ft radius, DEX save for half).",
    ["bard", "cleric", "wizard"],
    damage_dice="5d8", save_ability="DEX", effect_type="damage", area_type="sphere", area_size=20,
    at_higher_levels="Damage increases by 1d8 for each slot level above 3rd. Store spells of the same level or lower.",
))

_sp(Spell(
    "leomunds-tiny-hut", "Leomund's Tiny Hut", 3, "evocation",
    "1 minute", 0, ["V", "S", "M"], "8 hours", False,
    "A 10-foot-radius immobile dome of force springs into existence around and above you. Nine creatures of Medium size or smaller can fit inside. The atmosphere inside is comfortable and dry. No missiles, spells, or effects can cross the barrier.",
    ["bard", "wizard"],
    effect_type="utility", area_type="sphere", area_size=10,
))

_sp(Spell(
    "vampiric-touch", "Vampiric Touch", 3, "necromancy",
    "1 action", 0, ["V", "S"], "Concentration, up to 1 minute", True,
    "The touch of your shadow-wreathed hand siphons life force from others. Make a melee spell attack. On hit deal 3d6 necrotic damage and you regain HP equal to half the necrotic damage dealt.",
    ["warlock", "wizard"],
    damage_dice="3d6", damage_type="necrotic", effect_type="damage", area_type="single",
    at_higher_levels="Damage increases by 1d6 for each slot level above 3rd.",
))

_sp(Spell(
    "stinking-cloud", "Stinking Cloud", 3, "conjuration",
    "1 action", 90, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "You create a 20-foot-radius sphere of yellow, nauseating gas centered on a point within range. Each creature that is completely within the cloud at the start of its turn must make a CON save against poison. On fail, the creature spends its action that turn retching and reeling.",
    ["bard", "sorcerer", "wizard"],
    save_ability="CON", effect_type="control", area_type="sphere", area_size=20,
    conditions_applied=["poisoned"],
))

_sp(Spell(
    "sleet-storm", "Sleet Storm", 3, "conjuration",
    "1 action", 150, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "Until the spell ends, freezing rain and sleet fall in a 20-foot-tall cylinder with a 40-foot radius centered on a point you choose within range. The area is heavily obscured and is difficult terrain. When a creature enters the area for the first time on a turn or starts its turn there, it must make a DEX save or fall prone. Concentration is broken on a failed save.",
    ["druid", "sorcerer", "wizard"],
    save_ability="DEX", effect_type="control", area_type="cylinder", area_size=40,
    conditions_applied=["prone"],
))

_sp(Spell(
    "wind-wall", "Wind Wall", 3, "evocation",
    "1 action", 120, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "A wall of strong wind rises from the ground at a point you choose within range. The wall is up to 50 feet long, 15 feet high, and 1 foot thick. Each creature in the area when the wall appears must make a STR save or take 3d8 bludgeoning damage, half on success. Ranged weapon attacks crossing the wall automatically miss.",
    ["druid", "ranger"],
    damage_dice="3d8", damage_type="bludgeoning", save_ability="STR", effect_type="control",
    area_type="line", area_size=50,
))

_sp(Spell(
    "spirit-shroud", "Spirit Shroud", 3, "necromancy",
    "1 bonus action", 0, ["V", "S"], "Concentration, up to 1 minute", True,
    "You call forth spirits of the dead, which flit around you for the spell's duration. When you deal damage on your turn, a target within 10 feet takes an extra 1d8 radiant, necrotic, or cold damage (your choice when you cast). Any creature within 10 feet of you has its speed reduced by 10 feet.",
    ["cleric", "paladin", "warlock", "wizard"],
    damage_dice="1d8", effect_type="damage",
    at_higher_levels="Damage increases by 1d8 for every two slot levels above 3rd.",
))

_sp(Spell(
    "thunder-step", "Thunder Step", 3, "conjuration",
    "1 action", 90, ["V"], "Instantaneous", False,
    "You teleport yourself to an unoccupied space you can see within range. Immediately after you disappear, a thunderous boom sounds, and each creature within 10 feet of the space you left must make a CON save, taking 3d10 thunder damage on a fail, or half on success.",
    ["sorcerer", "warlock", "wizard"],
    damage_dice="3d10", damage_type="thunder", save_ability="CON", effect_type="damage",
    area_type="sphere", area_size=10,
    at_higher_levels="Damage increases by 1d10 for each slot level above 3rd.",
))

_sp(Spell(
    "erupting-earth", "Erupting Earth", 3, "transmutation",
    "1 action", 120, ["V", "S", "M"], "Instantaneous", False,
    "Choose a point you can see on the ground within range. A fountain of churned earth and stone erupts in a 20-foot cube centered on that point. Each creature in the area must make a DEX save. On fail take 3d12 bludgeoning damage, half on success. The area becomes difficult terrain.",
    ["druid", "sorcerer", "wizard"],
    damage_dice="3d12", damage_type="bludgeoning", save_ability="DEX", effect_type="damage",
    area_type="cube", area_size=20,
    at_higher_levels="Damage increases by 1d12 for each slot level above 3rd.",
))

_sp(Spell(
    "tidal-wave", "Tidal Wave", 3, "conjuration",
    "1 action", 120, ["V", "S", "M"], "Instantaneous", False,
    "You conjure up a wave of water that crashes down on an area within range. The area can be up to 30 feet long, up to 10 feet wide, and up to 10 feet tall. Each creature in the area must make a DEX save. On fail take 4d8 bludgeoning damage and be knocked prone, half damage on success.",
    ["druid", "sorcerer", "wizard"],
    damage_dice="4d8", damage_type="bludgeoning", save_ability="DEX", effect_type="damage",
    area_type="line", area_size=30,
    conditions_applied=["prone"],
))

_sp(Spell(
    "enemies-abound", "Enemies Abound", 3, "enchantment",
    "1 action", 120, ["V", "S"], "Concentration, up to 1 minute", True,
    "You reach into the mind of one creature you can see and force it to make an INT save. On a fail, the target loses the ability to distinguish friend from foe, regarding all creatures it can see as enemies until the spell ends.",
    ["bard", "sorcerer", "warlock", "wizard"],
    save_ability="INT", effect_type="control",
))

_sp(Spell(
    "catnap", "Catnap", 3, "enchantment",
    "1 action", 30, ["S", "M"], "10 minutes", False,
    "You make a calming gesture, and up to three willing creatures of your choice that you can see within range fall unconscious for the spell's duration. The spell ends on a target early if it takes damage or someone uses an action to shake or slap it awake. If a target remains unconscious for the full duration, that target gains the benefit of a short rest.",
    ["bard", "sorcerer", "wizard"],
    effect_type="utility",
    at_higher_levels="One additional creature for each slot level above 3rd.",
))

_sp(Spell(
    "summon-fey", "Summon Fey", 3, "conjuration",
    "1 action", 90, ["V", "S", "M"], "Concentration, up to 1 hour", True,
    "You call forth a fey spirit. It manifests in an unoccupied space that you can see within range. It is friendly to you and your companions and obeys your commands. Choose a mood: Fuming, Mirthful, or Tricksy.",
    ["druid", "ranger", "warlock", "wizard"],
    effect_type="summon",
    at_higher_levels="The creature gains additional HP and damage when using a higher level slot.",
))

_sp(Spell(
    "summon-shadowspawn", "Summon Shadowspawn", 3, "conjuration",
    "1 action", 90, ["V", "S", "M"], "Concentration, up to 1 hour", True,
    "You call forth a shadowy spirit. It manifests in an unoccupied space that you can see within range. Choose a type: Fury, Despair, or Fear.",
    ["warlock", "wizard"],
    effect_type="summon",
    at_higher_levels="The creature gains additional HP and damage when using a higher level slot.",
))

_sp(Spell(
    "summon-undead", "Summon Undead", 3, "necromancy",
    "1 action", 90, ["V", "S", "M"], "Concentration, up to 1 hour", True,
    "You call forth an undead spirit. It manifests in an unoccupied space that you can see within range. Choose a form: Ghostly, Putrid, or Skeletal.",
    ["warlock", "wizard"],
    effect_type="summon",
    at_higher_levels="The creature gains additional HP and damage when using a higher level slot.",
))

_sp(Spell(
    "crusaders-mantle", "Crusader's Mantle", 3, "evocation",
    "1 action", 0, ["V"], "Concentration, up to 1 minute", True,
    "Holy power radiates from you in an aura with a 30-foot radius, awakening boldness in friendly creatures. Until the spell ends, each nonhostile creature in the aura (including you) deals an extra 1d4 radiant damage when it hits with a weapon attack.",
    ["paladin"],
    damage_dice="1d4", damage_type="radiant", effect_type="buff",
    area_type="sphere", area_size=30,
))

_sp(Spell(
    "aura-of-vitality", "Aura of Vitality", 3, "evocation",
    "1 action", 0, ["V"], "Concentration, up to 1 minute", True,
    "Healing energy radiates from you in an aura with a 30-foot radius. Until the spell ends, the aura moves with you, centered on you. You can use a bonus action to cause one creature in the aura to regain 2d6 hit points.",
    ["cleric", "druid", "paladin"],
    healing_dice="2d6", effect_type="healing",
    area_type="sphere", area_size=30,
))

_sp(Spell(
    "blinding-smite", "Blinding Smite", 3, "evocation",
    "1 bonus action", 0, ["V"], "Concentration, up to 1 minute", True,
    "The next time you hit a creature with a melee weapon attack during this spell's duration, your weapon flares with a bright light, and the attack deals an extra 3d8 radiant damage. Additionally, the target must succeed on a CON save or be blinded until the spell ends.",
    ["paladin"],
    damage_dice="3d8", damage_type="radiant", save_ability="CON", effect_type="damage",
    conditions_applied=["blinded"],
))

_sp(Spell(
    "elemental-weapon", "Elemental Weapon", 3, "transmutation",
    "1 action", 0, ["V", "S"], "Concentration, up to 1 hour", True,
    "A nonmagical weapon you touch becomes a magic weapon. Choose one of the following damage types: acid, cold, fire, lightning, or thunder. For the duration, the weapon has a +1 bonus to attack rolls and deals an extra 1d4 damage of the chosen type when it hits.",
    ["paladin", "druid", "ranger"],
    damage_dice="1d4", effect_type="buff",
    at_higher_levels="+2 bonus and 2d4 at 5th-6th level slot, +3 and 3d4 at 7th+ level slot.",
))

_sp(Spell(
    "magic-circle", "Magic Circle", 3, "abjuration",
    "1 minute", 10, ["V", "S", "M"], "1 hour", False,
    "You create a 10-foot-radius, 20-foot-tall cylinder of magical energy centered on a point on the ground within range. Choose one or more of: celestials, elementals, fey, fiends, or undead. The chosen creatures can't willingly enter the cylinder, have disadvantage on attacks against targets within, and targets can't be charmed, frightened, or possessed by them.",
    ["cleric", "paladin", "warlock", "wizard"],
    effect_type="control", area_type="cylinder", area_size=10,
    at_higher_levels="Duration increases by 1 hour for each slot level above 3rd.",
))


# ═══════════════════════════════════════════════════════════════
#  LEVEL 4  SPELLS
# ═══════════════════════════════════════════════════════════════

_sp(Spell(
    "banishment", "Banishment", 4, "abjuration",
    "1 action", 60, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "You attempt to send one creature that you can see within range to another plane of existence. The target must succeed on a CHA save or be banished. If native to the current plane, target goes to a harmless demiplane and is incapacitated. Otherwise, it returns to its home plane.",
    ["cleric", "paladin", "sorcerer", "warlock", "wizard"],
    save_ability="CHA", effect_type="control",
    conditions_applied=["incapacitated"],
    at_higher_levels="One additional creature for each slot level above 4th.",
))

_sp(Spell(
    "dimension-door", "Dimension Door", 4, "conjuration",
    "1 action", 500, ["V"], "Instantaneous", False,
    "You teleport yourself from your current location to any other spot within range. You arrive at exactly the spot desired. You can bring along objects as long as their weight doesn't exceed what you can carry. You can also bring one willing creature of your size or smaller.",
    ["bard", "sorcerer", "warlock", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "greater-invisibility", "Greater Invisibility", 4, "illusion",
    "1 action", 0, ["V", "S"], "Concentration, up to 1 minute", True,
    "You or a creature you touch becomes invisible until the spell ends. Anything the target is wearing or carrying is invisible as long as it is on the target's person. The target does not become visible when it attacks or casts a spell.",
    ["bard", "sorcerer", "wizard"],
    effect_type="buff",
    conditions_applied=["invisible"],
))

_sp(Spell(
    "polymorph", "Polymorph", 4, "transmutation",
    "1 action", 60, ["V", "S", "M"], "Concentration, up to 1 hour", True,
    "This spell transforms a creature that you can see within range into a new form. An unwilling creature must make a WIS save. The target's game statistics are replaced by the statistics of the chosen beast. It retains its alignment and personality. The target assumes the HP of its new form.",
    ["bard", "druid", "sorcerer", "wizard"],
    save_ability="WIS", effect_type="buff",
))

_sp(Spell(
    "ice-storm", "Ice Storm", 4, "evocation",
    "1 action", 300, ["V", "S", "M"], "Instantaneous", False,
    "A hail of rock-hard ice pounds to the ground in a 20-foot-radius, 40-foot-high cylinder centered on a point within range. Each creature in the cylinder must make a DEX save. On fail take 2d8 bludgeoning + 4d6 cold damage, half on success. Ground becomes difficult terrain until end of your next turn.",
    ["druid", "sorcerer", "wizard"],
    damage_dice="2d8+4d6", damage_type="cold", save_ability="DEX", effect_type="damage",
    area_type="cylinder", area_size=20,
    at_higher_levels="Bludgeoning damage increases by 1d8 for each slot level above 4th.",
))

_sp(Spell(
    "wall-of-fire", "Wall of Fire", 4, "evocation",
    "1 action", 120, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "You create a wall of fire on a solid surface within range. You can make the wall up to 60 feet long, 20 feet high, and 1 foot thick, or a ringed wall up to 20 feet in diameter, 20 feet high, and 1 foot thick. When the wall appears, each creature within its area must make a DEX save or take 5d8 fire damage, half on success. One side of the wall (chosen at casting) deals 5d8 fire damage to each creature that ends its turn within 10 feet of that side.",
    ["druid", "sorcerer", "wizard"],
    damage_dice="5d8", damage_type="fire", save_ability="DEX", effect_type="damage",
    area_type="line", area_size=60,
    at_higher_levels="Damage increases by 1d8 for each slot level above 4th.",
))

_sp(Spell(
    "blight", "Blight", 4, "necromancy",
    "1 action", 30, ["V", "S"], "Instantaneous", False,
    "Necromantic energy washes over a creature of your choice within range, draining moisture and vitality from it. The target must make a CON save, taking 8d8 necrotic damage on a fail, or half on success. This spell has no effect on undead or constructs. Plant creatures and magical plants make this saving throw with disadvantage.",
    ["druid", "sorcerer", "warlock", "wizard"],
    damage_dice="8d8", damage_type="necrotic", save_ability="CON", effect_type="damage", area_type="single",
    at_higher_levels="Damage increases by 1d8 for each slot level above 4th.",
))

_sp(Spell(
    "death-ward", "Death Ward", 4, "abjuration",
    "1 action", 0, ["V", "S"], "8 hours", False,
    "You touch a creature and grant it a measure of protection from death. The first time the target would drop to 0 hit points as a result of taking damage, the target instead drops to 1 hit point, and the spell ends.",
    ["cleric", "paladin"],
    effect_type="buff",
))

_sp(Spell(
    "freedom-of-movement", "Freedom of Movement", 4, "abjuration",
    "1 action", 0, ["V", "S", "M"], "1 hour", False,
    "You touch a willing creature. For the duration, the target's movement is unaffected by difficult terrain. Spells and other magical effects can't reduce the target's speed or cause it to be paralyzed or restrained.",
    ["bard", "cleric", "druid", "ranger"],
    effect_type="buff",
))

_sp(Spell(
    "guardian-of-faith", "Guardian of Faith", 4, "conjuration",
    "1 action", 30, ["V"], "8 hours", False,
    "A Large spectral guardian appears in an unoccupied space of your choice within range. Any hostile creature that moves to a space within 10 feet of the guardian for the first time on a turn must succeed on a DEX save. On fail take 20 radiant damage, half on success. The guardian vanishes when it has dealt a total of 60 damage.",
    ["cleric"],
    damage_dice="20", damage_type="radiant", save_ability="DEX", effect_type="damage",
    area_type="sphere", area_size=10,
))

_sp(Spell(
    "stone-shape", "Stone Shape", 4, "transmutation",
    "1 action", 0, ["V", "S", "M"], "Instantaneous", False,
    "You touch a stone object of Medium size or smaller or a section of stone no more than 5 feet in any dimension and form it into any shape that suits your purpose.",
    ["cleric", "druid", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "stoneskin", "Stoneskin", 4, "abjuration",
    "1 action", 0, ["V", "S", "M"], "Concentration, up to 1 hour", True,
    "This spell turns the flesh of a willing creature you touch as hard as stone. Until the spell ends, the target has resistance to nonmagical bludgeoning, piercing, and slashing damage.",
    ["druid", "ranger", "sorcerer", "wizard"],
    effect_type="buff",
))

_sp(Spell(
    "conjure-minor-elementals", "Conjure Minor Elementals", 4, "conjuration",
    "1 minute", 90, ["V", "S"], "Concentration, up to 1 hour", True,
    "You summon elementals that appear in unoccupied spaces that you can see within range. Choose one of: one elemental of CR 2 or lower, two elementals of CR 1 or lower, four elementals of CR 1/2 or lower, or eight elementals of CR 1/4 or lower.",
    ["druid", "wizard"],
    effect_type="summon",
    at_higher_levels="Summon twice as many elementals at 6th level, three times at 8th.",
))

_sp(Spell(
    "giant-insect", "Giant Insect", 4, "transmutation",
    "1 action", 30, ["V", "S"], "Concentration, up to 10 minutes", True,
    "You transform up to ten centipedes, three spiders, five wasps, or one scorpion within range into giant versions of their natural forms for the duration.",
    ["druid"],
    effect_type="summon",
))

_sp(Spell(
    "locate-creature", "Locate Creature", 4, "divination",
    "1 action", 0, ["V", "S", "M"], "Concentration, up to 1 hour", True,
    "Describe or name a creature that is familiar to you. You sense the direction to the creature's location, as long as that creature is within 1,000 feet of you.",
    ["bard", "cleric", "druid", "paladin", "ranger", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "phantasmal-killer", "Phantasmal Killer", 4, "illusion",
    "1 action", 120, ["V", "S"], "Concentration, up to 1 minute", True,
    "You tap into the nightmares of a creature you can see within range. The target must make a WIS save. On fail it becomes frightened for the duration. At the end of each of the target's turns, it must succeed on a WIS save or take 4d10 psychic damage. On success the spell ends.",
    ["wizard"],
    damage_dice="4d10", damage_type="psychic", save_ability="WIS", effect_type="damage", area_type="single",
    conditions_applied=["frightened"],
    at_higher_levels="Damage increases by 1d10 for each slot level above 4th.",
))

_sp(Spell(
    "confusion", "Confusion", 4, "enchantment",
    "1 action", 90, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "This spell assaults and twists creatures' minds, spawning delusions and provoking uncontrolled action. Each creature in a 10-foot-radius sphere centered on a point you choose within range must succeed on a WIS save or be affected. A target rolls d10 at the start of each of its turns to determine its behavior.",
    ["bard", "druid", "sorcerer", "wizard"],
    save_ability="WIS", effect_type="control", area_type="sphere", area_size=10,
    at_higher_levels="Radius of the sphere increases by 5 feet for each slot level above 4th.",
))

_sp(Spell(
    "arcane-eye", "Arcane Eye", 4, "divination",
    "1 action", 30, ["V", "S", "M"], "Concentration, up to 1 hour", True,
    "You create an invisible, magical eye within range that hovers in the air for the duration. You mentally receive visual information from the eye, which has normal vision and darkvision out to 30 feet. The eye can move up to 30 feet per round in any direction.",
    ["wizard"],
    effect_type="utility",
))

_sp(Spell(
    "fabricate", "Fabricate", 4, "transmutation",
    "10 minutes", 120, ["V", "S"], "Instantaneous", False,
    "You convert raw materials into products of the same material. A Medium or smaller object can be crafted this way. If you are working with mineral materials (stone, crystal, or metal), the fabricated object can be no larger than Medium.",
    ["wizard"],
    effect_type="utility",
))

_sp(Spell(
    "fire-shield", "Fire Shield", 4, "evocation",
    "1 action", 0, ["V", "S", "M"], "10 minutes", False,
    "Thin and wispy flames wreathe your body for the duration, shedding bright light in a 10-foot radius. Choose warm shield (resistance to cold, 2d8 fire damage to melee attackers) or chill shield (resistance to fire, 2d8 cold damage to melee attackers).",
    ["wizard"],
    damage_dice="2d8", effect_type="buff",
))

_sp(Spell(
    "otilukes-resilient-sphere", "Otiluke's Resilient Sphere", 4, "evocation",
    "1 action", 30, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "A sphere of shimmering force encloses a creature or object of Large size or smaller within range. An unwilling creature must make a DEX save. On fail, the creature is enclosed. Nothing can pass through the barrier. The creature inside can breathe, cannot be damaged, and cannot damage anything outside.",
    ["wizard"],
    save_ability="DEX", effect_type="control",
))

_sp(Spell(
    "evards-black-tentacles", "Evard's Black Tentacles", 4, "conjuration",
    "1 action", 90, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "Squirming, ebony tentacles fill a 20-foot square on ground that you can see within range. The area is difficult terrain. When a creature enters the area for the first time or starts its turn there, it must succeed on a DEX save or take 3d6 bludgeoning damage and be restrained.",
    ["wizard"],
    damage_dice="3d6", damage_type="bludgeoning", save_ability="DEX", effect_type="control",
    area_type="cube", area_size=20,
    conditions_applied=["restrained"],
))

_sp(Spell(
    "dominate-beast", "Dominate Beast", 4, "enchantment",
    "1 action", 60, ["V", "S"], "Concentration, up to 1 minute", True,
    "You attempt to beguile a beast that you can see within range. It must succeed on a WIS save or be charmed by you for the duration. While the beast is charmed, you have a telepathic link with it and can issue commands telepathically.",
    ["druid", "ranger", "sorcerer"],
    save_ability="WIS", effect_type="control",
    conditions_applied=["charmed"],
    at_higher_levels="Duration 10 minutes at 5th, 1 hour at 6th, 8 hours at 7th+.",
))

_sp(Spell(
    "compulsion", "Compulsion", 4, "enchantment",
    "1 action", 30, ["V", "S"], "Concentration, up to 1 minute", True,
    "Creatures of your choice that you can see within range and that can hear you must make a WIS save. A target automatically succeeds on this save if it can't be charmed. On a failed save, a target is affected. Until the spell ends, you can use a bonus action on each of your turns to designate a direction. Each affected target must use as much of its movement as possible to move in that direction on its next turn.",
    ["bard"],
    save_ability="WIS", effect_type="control",
))

_sp(Spell(
    "staggering-smite", "Staggering Smite", 4, "evocation",
    "1 bonus action", 0, ["V"], "Concentration, up to 1 minute", True,
    "The next time you hit a creature with a melee weapon attack during this spell's duration, your weapon pierces both body and mind, and the attack deals an extra 4d6 psychic damage. The target must make a WIS save. On fail it has disadvantage on attack rolls and ability checks, and can't take reactions, until the end of its next turn.",
    ["paladin"],
    damage_dice="4d6", damage_type="psychic", save_ability="WIS", effect_type="damage",
    conditions_applied=["stunned"],
))

_sp(Spell(
    "aura-of-purity", "Aura of Purity", 4, "abjuration",
    "1 action", 0, ["V"], "Concentration, up to 10 minutes", True,
    "Purifying energy radiates from you in a 30-foot radius. Nonhostile creatures in the aura can't become diseased, have resistance to poison damage, and have advantage on saves against blinded, charmed, deafened, frightened, paralyzed, poisoned, and stunned conditions.",
    ["paladin"],
    effect_type="buff", area_type="sphere", area_size=30,
))

_sp(Spell(
    "aura-of-life", "Aura of Life", 4, "abjuration",
    "1 action", 0, ["V"], "Concentration, up to 10 minutes", True,
    "Life-preserving energy radiates from you in a 30-foot radius. Nonhostile creatures in the aura have resistance to necrotic damage, and their hit point maximum can't be reduced. If a nonhostile creature starts its turn in the aura with 0 HP, it regains 1 HP.",
    ["paladin"],
    effect_type="buff", area_type="sphere", area_size=30,
))

_sp(Spell(
    "find-greater-steed", "Find Greater Steed", 4, "conjuration",
    "10 minutes", 30, ["V", "S"], "Instantaneous", False,
    "You summon a spirit that assumes the form of a loyal, majestic mount. The steed takes a form you choose: griffon, pegasus, peryton, dire wolf, rhinoceros, or saber-toothed tiger.",
    ["paladin"],
    effect_type="summon",
))

_sp(Spell(
    "sickening-radiance", "Sickening Radiance", 4, "evocation",
    "1 action", 120, ["V", "S"], "Concentration, up to 10 minutes", True,
    "Dim, greenish light spreads within a 30-foot-radius sphere centered on a point you choose within range. Creatures in the sphere when you cast or that enter it must succeed on a CON save or take 4d10 radiant damage, and suffer one level of exhaustion. Creatures can't become invisible in the area.",
    ["sorcerer", "warlock", "wizard"],
    damage_dice="4d10", damage_type="radiant", save_ability="CON", effect_type="damage",
    area_type="sphere", area_size=30,
    conditions_applied=["exhaustion"],
))

_sp(Spell(
    "shadow-of-moil", "Shadow of Moil", 4, "necromancy",
    "1 action", 0, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "Flame-like shadows wreathe your body until the spell ends. You gain the following benefits: you are heavily obscured to others; you have resistance to radiant damage; whenever a creature within 10 feet of you hits you with an attack, the shadows lash out at that creature, dealing it 2d8 necrotic damage.",
    ["warlock"],
    damage_dice="2d8", damage_type="necrotic", effect_type="buff",
))

_sp(Spell(
    "summon-elemental", "Summon Elemental", 4, "conjuration",
    "1 action", 90, ["V", "S", "M"], "Concentration, up to 1 hour", True,
    "You call forth an elemental spirit. It manifests in an unoccupied space within range. Choose an element: Air, Earth, Fire, or Water.",
    ["druid", "ranger", "wizard"],
    effect_type="summon",
    at_higher_levels="The creature gains additional HP and damage when using a higher level slot.",
))

_sp(Spell(
    "summon-aberration", "Summon Aberration", 4, "conjuration",
    "1 action", 90, ["V", "S", "M"], "Concentration, up to 1 hour", True,
    "You call forth an aberrant spirit. It manifests in an unoccupied space within range. Choose a type: Beholderkin, Slaad, or Star Spawn.",
    ["warlock", "wizard"],
    effect_type="summon",
    at_higher_levels="The creature gains additional HP and damage when using a higher level slot.",
))

_sp(Spell(
    "summon-construct", "Summon Construct", 4, "conjuration",
    "1 action", 90, ["V", "S", "M"], "Concentration, up to 1 hour", True,
    "You call forth the spirit of a construct. It manifests in an unoccupied space within range. Choose a type: Clay, Metal, or Stone.",
    ["wizard"],
    effect_type="summon",
    at_higher_levels="The creature gains additional HP and damage when using a higher level slot.",
))


# ═══════════════════════════════════════════════════════════════
#  LEVEL 5  SPELLS
# ═══════════════════════════════════════════════════════════════

_sp(Spell(
    "cone-of-cold", "Cone of Cold", 5, "evocation",
    "1 action", 0, ["V", "S", "M"], "Instantaneous", False,
    "A blast of cold air erupts from your hands. Each creature in a 60-foot cone must make a CON save. On fail take 8d8 cold damage, half on success. A creature killed by this spell becomes a frozen statue.",
    ["sorcerer", "wizard"],
    damage_dice="8d8", damage_type="cold", save_ability="CON", effect_type="damage",
    area_type="cone", area_size=60,
    at_higher_levels="Damage increases by 1d8 for each slot level above 5th.",
))

_sp(Spell(
    "hold-monster", "Hold Monster", 5, "enchantment",
    "1 action", 90, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "Choose a creature that you can see within range. The target must succeed on a WIS save or be paralyzed for the duration. This spell has no creature type restrictions (unlike Hold Person). Target can repeat the save at end of each of its turns.",
    ["bard", "sorcerer", "warlock", "wizard"],
    save_ability="WIS", effect_type="control",
    conditions_applied=["paralyzed"],
    at_higher_levels="One additional creature for each slot level above 5th.",
))

_sp(Spell(
    "wall-of-force", "Wall of Force", 5, "evocation",
    "1 action", 120, ["V", "S", "M"], "Concentration, up to 10 minutes", True,
    "An invisible wall of force springs into existence at a point you choose within range. The wall can be a flat surface made up of ten 10-foot-by-10-foot panels, or it can be formed into a hemisphere or a sphere. Nothing can physically pass through the wall. It is immune to all damage and can't be dispelled by Dispel Magic.",
    ["wizard"],
    effect_type="control",
))

_sp(Spell(
    "animate-objects", "Animate Objects", 5, "transmutation",
    "1 action", 120, ["V", "S"], "Concentration, up to 1 minute", True,
    "Objects come to life at your command. Choose up to ten nonmagical objects within range that are not being worn or carried. Medium targets count as two objects, Large targets count as four objects, Huge targets count as eight objects.",
    ["bard", "sorcerer", "wizard"],
    effect_type="summon",
    at_higher_levels="You can animate two additional objects for each slot level above 5th.",
))

_sp(Spell(
    "telekinesis", "Telekinesis", 5, "transmutation",
    "1 action", 60, ["V", "S"], "Concentration, up to 10 minutes", True,
    "You gain the ability to move or manipulate creatures or objects by thought. You can exert fine motor control on objects, or try to move a Huge or smaller creature. An unwilling creature can make a STR check contested by your spellcasting ability check. You can move the target up to 30 feet in any direction.",
    ["sorcerer", "wizard"],
    effect_type="control",
))

_sp(Spell(
    "flame-strike", "Flame Strike", 5, "evocation",
    "1 action", 60, ["V", "S", "M"], "Instantaneous", False,
    "A vertical column of divine fire roars down from the heavens in a location you specify. Each creature in a 10-foot-radius, 40-foot-high cylinder centered on a point within range must make a DEX save. On fail take 4d6 fire damage and 4d6 radiant damage, half on success.",
    ["cleric"],
    damage_dice="4d6+4d6", damage_type="fire", save_ability="DEX", effect_type="damage",
    area_type="cylinder", area_size=10,
    at_higher_levels="Fire damage or radiant damage (your choice) increases by 1d6 for each slot level above 5th.",
))

_sp(Spell(
    "mass-cure-wounds", "Mass Cure Wounds", 5, "evocation",
    "1 action", 60, ["V", "S"], "Instantaneous", False,
    "A wave of healing energy washes out from a point of your choice within range. Choose up to six creatures in a 30-foot-radius sphere centered on that point. Each target regains hit points equal to 3d8 + your spellcasting ability modifier. This spell has no effect on undead or constructs.",
    ["bard", "cleric", "druid"],
    healing_dice="3d8", effect_type="healing", area_type="sphere", area_size=30,
    at_higher_levels="Healing increases by 1d8 for each slot level above 5th.",
))

_sp(Spell(
    "greater-restoration", "Greater Restoration", 5, "abjuration",
    "1 action", 0, ["V", "S", "M"], "Instantaneous", False,
    "You imbue a creature you touch with positive energy to undo a debilitating effect. You can reduce the target's exhaustion level by one, or end one of the following effects: one effect that charmed or petrified the target, one curse, any reduction to one ability score, one effect reducing the target's HP maximum.",
    ["bard", "cleric", "druid"],
    effect_type="healing",
))

_sp(Spell(
    "raise-dead", "Raise Dead", 5, "necromancy",
    "1 hour", 0, ["V", "S", "M"], "Instantaneous", False,
    "You return a dead creature you touch to life, provided that it has been dead no longer than 10 days. The creature returns to life with 1 hit point. This spell neutralizes any poisons and cures nonmagical diseases. It doesn't, however, remove magical diseases, curses, or similar effects.",
    ["bard", "cleric", "paladin"],
    effect_type="healing",
))

_sp(Spell(
    "commune", "Commune", 5, "divination",
    "1 minute", 0, ["V", "S", "M"], "1 minute", False,
    "You contact your deity or a divine proxy and ask up to three questions that can be answered with a yes or no. You receive a correct answer for each question. Divine beings aren't necessarily omniscient, so you might receive 'unclear' as an answer if a question pertains to information beyond the deity's knowledge.",
    ["cleric"],
    effect_type="utility",
))

_sp(Spell(
    "scrying", "Scrying", 5, "divination",
    "10 minutes", 0, ["V", "S", "M"], "Concentration, up to 10 minutes", True,
    "You can see and hear a particular creature you choose that is on the same plane of existence as you. The target must make a WIS save, which is modified by how well you know the target and the sort of physical connection you have to it.",
    ["bard", "cleric", "druid", "warlock", "wizard"],
    save_ability="WIS", effect_type="utility",
))

_sp(Spell(
    "contact-other-plane", "Contact Other Plane", 5, "divination",
    "1 minute", 0, ["V"], "1 minute", False,
    "You mentally contact a demigod, the spirit of a long-dead sage, or some other mysterious entity from another plane. You can ask the entity up to five questions. You must succeed on a DC 15 INT save or take 6d6 psychic damage and be insane until you finish a long rest.",
    ["warlock", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "modify-memory", "Modify Memory", 5, "enchantment",
    "1 action", 30, ["V", "S"], "Concentration, up to 1 minute", True,
    "You attempt to reshape another creature's memories. The creature must make a WIS save. On fail it becomes charmed by you for the duration. While charmed, you can alter the target's memory of an event that it experienced within the last 24 hours and that lasted no more than 10 minutes.",
    ["bard", "wizard"],
    save_ability="WIS", effect_type="control",
    conditions_applied=["charmed"],
    at_higher_levels="Can target memories up to 7 days (6th), 30 days (7th), 1 year (8th), or any time (9th) old.",
))

_sp(Spell(
    "dominate-person", "Dominate Person", 5, "enchantment",
    "1 action", 60, ["V", "S"], "Concentration, up to 1 minute", True,
    "You attempt to beguile a humanoid that you can see within range. It must succeed on a WIS save or be charmed by you for the duration. While the target is charmed, you have a telepathic link with it. You can use this telepathic link to issue commands to the creature while you are conscious.",
    ["bard", "sorcerer", "wizard"],
    save_ability="WIS", effect_type="control",
    conditions_applied=["charmed"],
    at_higher_levels="Duration 10 minutes at 6th, 1 hour at 7th, 8 hours at 8th+.",
))

_sp(Spell(
    "geas", "Geas", 5, "enchantment",
    "1 minute", 60, ["V"], "30 days", False,
    "You place a magical command on a creature that you can see within range, forcing it to carry out some service or refrain from some action or course of activity as you decide. Target must WIS save. On fail, it becomes charmed by you for the duration. While charmed, the creature takes 5d10 psychic damage each time it acts in a manner directly counter to your instructions.",
    ["bard", "cleric", "druid", "paladin", "wizard"],
    damage_dice="5d10", damage_type="psychic", save_ability="WIS", effect_type="control",
    conditions_applied=["charmed"],
    at_higher_levels="Duration 1 year at 7th-8th, permanent at 9th.",
))

_sp(Spell(
    "cloudkill", "Cloudkill", 5, "conjuration",
    "1 action", 120, ["V", "S"], "Concentration, up to 10 minutes", True,
    "You create a 20-foot-radius sphere of poisonous, yellow-green fog centered on a point you choose within range. The fog spreads around corners. Each creature that starts its turn in the fog or enters it must make a CON save. On fail take 5d8 poison damage, half on success. The fog moves 10 feet away from you at the start of each of your turns.",
    ["sorcerer", "wizard"],
    damage_dice="5d8", damage_type="poison", save_ability="CON", effect_type="damage",
    area_type="sphere", area_size=20,
    conditions_applied=["poisoned"],
    at_higher_levels="Damage increases by 1d8 for each slot level above 5th.",
))

_sp(Spell(
    "insect-plague", "Insect Plague", 5, "conjuration",
    "1 action", 300, ["V", "S", "M"], "Concentration, up to 10 minutes", True,
    "Swarming, biting locusts fill a 20-foot-radius sphere centered on a point you choose within range. The sphere spreads around corners. Each creature in the area when it appears, and each creature that enters it or starts its turn there, must make a CON save, taking 4d10 piercing damage on a fail, or half on success. Difficult terrain and lightly obscured.",
    ["cleric", "druid", "sorcerer"],
    damage_dice="4d10", damage_type="piercing", save_ability="CON", effect_type="damage",
    area_type="sphere", area_size=20,
    at_higher_levels="Damage increases by 1d10 for each slot level above 5th.",
))

_sp(Spell(
    "contagion", "Contagion", 5, "necromancy",
    "1 action", 0, ["V", "S"], "7 days", False,
    "Your touch inflicts disease. Make a melee spell attack. On hit, you afflict the creature with a disease of your choice. The target must make three CON saves (one at end of each of its turns). After three failed saves the disease effects last for the duration; after three successes the creature recovers.",
    ["cleric", "druid"],
    effect_type="debuff",
    conditions_applied=["poisoned"],
))

_sp(Spell(
    "destructive-wave", "Destructive Wave", 5, "evocation",
    "1 action", 0, ["V"], "Instantaneous", False,
    "You strike the ground, creating a burst of divine energy that ripples outward from you. Each creature you choose within 30 feet must succeed on a CON save or take 5d6 thunder damage + 5d6 radiant or necrotic damage (your choice) and be knocked prone. On success half damage and no prone.",
    ["paladin"],
    damage_dice="5d6+5d6", damage_type="thunder", save_ability="CON", effect_type="damage",
    area_type="sphere", area_size=30,
    conditions_applied=["prone"],
))

_sp(Spell(
    "antilife-shell", "Antilife Shell", 5, "abjuration",
    "1 action", 0, ["V", "S"], "Concentration, up to 1 hour", True,
    "A shimmering barrier extends out from you in a 10-foot radius and moves with you, remaining centered on you and hedging out creatures other than undead and constructs. The barrier prevents affected creatures from passing or reaching through.",
    ["druid"],
    effect_type="control", area_type="sphere", area_size=10,
))

_sp(Spell(
    "wall-of-stone", "Wall of Stone", 5, "evocation",
    "1 action", 120, ["V", "S", "M"], "Concentration, up to 10 minutes", True,
    "A nonmagical wall of solid stone springs into existence at a point you choose within range. The wall is 6 inches thick and is composed of ten 10-foot-by-10-foot panels. Each panel must be contiguous with at least one other panel.",
    ["druid", "sorcerer", "wizard"],
    effect_type="control",
))

_sp(Spell(
    "passwall", "Passwall", 5, "transmutation",
    "1 action", 30, ["V", "S", "M"], "1 hour", False,
    "A passage appears at a point of your choice that you can see on a wooden, plaster, or stone surface (such as a wall, a ceiling, or a floor) within range, and lasts for the duration. You choose the opening's dimensions: up to 5 feet wide, 8 feet tall, and 20 feet deep.",
    ["wizard"],
    effect_type="utility",
))

_sp(Spell(
    "teleportation-circle", "Teleportation Circle", 5, "conjuration",
    "1 minute", 10, ["V", "M"], "1 round", False,
    "As you cast the spell, you draw a 10-foot-diameter circle on the ground inscribed with sigils that link your location to a permanent teleportation circle of your choice whose sigil sequence you know.",
    ["bard", "sorcerer", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "bigbys-hand", "Bigby's Hand", 5, "evocation",
    "1 action", 120, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "You create a Large hand of shimmering, translucent force in an unoccupied space that you can see within range. The hand is an object that has AC 20 and HP equal to your HP maximum. It has STR 26 (+8) and DEX 10 (+0). It can punch, push, grasp, or block.",
    ["wizard"],
    damage_dice="4d8", damage_type="force", effect_type="summon",
    at_higher_levels="Damage of Clenched Fist and Grasping Hand increase by 2d8 and 2d6 respectively for each slot level above 5th.",
))

_sp(Spell(
    "planar-binding", "Planar Binding", 5, "abjuration",
    "1 hour", 60, ["V", "S", "M"], "24 hours", False,
    "With this spell, you attempt to bind a celestial, an elemental, a fey, or a fiend to your service. The creature must make a CHA save. On a failure, it is bound to serve you for the duration. A bound creature must follow your instructions to the best of its ability.",
    ["bard", "cleric", "druid", "wizard"],
    save_ability="CHA", effect_type="control",
    at_higher_levels="Duration 10 days at 6th, 30 days at 7th, 180 days at 8th, a year and a day at 9th.",
))

_sp(Spell(
    "reincarnate", "Reincarnate", 5, "transmutation",
    "1 hour", 0, ["V", "S", "M"], "Instantaneous", False,
    "You touch a dead humanoid or a piece of a dead humanoid. Provided that the creature has been dead no longer than 10 days, the spell forms a new adult body for it and then calls the soul to enter that body. The DM rolls on a table to determine the new race.",
    ["druid"],
    effect_type="healing",
))

_sp(Spell(
    "awaken", "Awaken", 5, "transmutation",
    "8 hours", 0, ["V", "S", "M"], "Instantaneous", False,
    "After spending the casting time tracing magical pathways within a precious gemstone, you touch a Huge or smaller beast or plant. The target gains an Intelligence of 10. A plant gains the ability to move its limbs, roots, vines, creepers, and so forth. The target is charmed by you for 30 days.",
    ["bard", "druid"],
    effect_type="utility",
    conditions_applied=["charmed"],
))

_sp(Spell(
    "dream", "Dream", 5, "illusion",
    "1 minute", -1, ["V", "S", "M"], "8 hours", False,
    "This spell shapes a creature's dreams. Choose a creature known to you as the target of this spell. You or a willing creature you touch enters a trance state, acting as a messenger. The messenger can appear in the target's dreams and converse with the target.",
    ["bard", "warlock", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "legend-lore", "Legend Lore", 5, "divination",
    "10 minutes", 0, ["V", "S", "M"], "Instantaneous", False,
    "Name or describe a person, place, or object. The spell brings to your mind a brief summary of the significant lore about the thing you named. If the thing you named isn't of legendary importance, you gain no information.",
    ["bard", "cleric", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "creation", "Creation", 5, "illusion",
    "1 minute", 30, ["V", "S", "M"], "Special", False,
    "You pull wisps of shadow material from the Shadowfell to create a nonliving object of vegetable matter—soft goods, rope, wood, or something similar. You can also use this spell to create mineral objects such as stone, crystal, or metal. Duration depends on material.",
    ["sorcerer", "wizard"],
    effect_type="utility",
    at_higher_levels="Cube size increases by 5 feet for each slot level above 5th.",
))

_sp(Spell(
    "dawn", "Dawn", 5, "evocation",
    "1 action", 60, ["V", "S", "M"], "Concentration, up to 1 minute", True,
    "The light of dawn shines down on a location you specify within range. Until the spell ends, a 30-foot-radius, 40-foot-high cylinder of bright light glimmers there. Each creature in the cylinder when it appears must make a CON save, taking 4d10 radiant damage on a fail, or half on success. A creature must also make the save when it enters the cylinder or ends its turn there.",
    ["cleric", "wizard"],
    damage_dice="4d10", damage_type="radiant", save_ability="CON", effect_type="damage",
    area_type="cylinder", area_size=30,
))

_sp(Spell(
    "holy-weapon", "Holy Weapon", 5, "evocation",
    "1 bonus action", 0, ["V", "S"], "Concentration, up to 1 hour", True,
    "You imbue a weapon you touch with holy power. Until the spell ends, the weapon emits bright light in a 30-foot radius and dim light for an additional 30 feet. In addition, weapon attacks made with it deal an extra 2d8 radiant damage on a hit. If the weapon is not already magical, it becomes magical for the duration. As a bonus action you can dismiss the spell causing a burst dealing 4d8 radiant (DEX save for half) and blinding creatures in 30 feet.",
    ["cleric", "paladin"],
    damage_dice="2d8", damage_type="radiant", effect_type="buff",
))

_sp(Spell(
    "steel-wind-strike", "Steel Wind Strike", 5, "conjuration",
    "1 action", 30, ["S", "M"], "Instantaneous", False,
    "You flourish the weapon used in the casting and then vanish to strike like the wind. Choose up to five creatures you can see within range. Make a melee spell attack against each target. On a hit, a target takes 6d10 force damage. You can then teleport to an unoccupied space you can see within 5 feet of one of the targets you hit or missed.",
    ["ranger", "wizard"],
    damage_dice="6d10", damage_type="force", effect_type="damage", area_type="single",
))

_sp(Spell(
    "synaptic-static", "Synaptic Static", 5, "enchantment",
    "1 action", 120, ["V", "S"], "Instantaneous", False,
    "You choose a point within range and cause psychic energy to explode there. Each creature in a 20-foot-radius sphere centered on that point must make an INT save. On a fail, a target takes 8d6 psychic damage and must subtract 1d6 from all attack rolls, ability checks, and concentration saves for 1 minute. On success half damage and no other effect.",
    ["bard", "sorcerer", "warlock", "wizard"],
    damage_dice="8d6", damage_type="psychic", save_ability="INT", effect_type="damage",
    area_type="sphere", area_size=20,
))

_sp(Spell(
    "danse-macabre", "Danse Macabre", 5, "necromancy",
    "1 action", 60, ["V", "S"], "Concentration, up to 1 hour", True,
    "Threads of dark power leap from your fingers to pierce up to five Small or Medium corpses you can see within range. Each corpse immediately stands up and becomes undead. You choose whether it is a zombie or skeleton. They obey your mental commands and add your spellcasting modifier to attacks and damage.",
    ["warlock", "wizard"],
    effect_type="summon",
    at_higher_levels="Animate up to two additional corpses for each slot level above 5th.",
))

_sp(Spell(
    "negative-energy-flood", "Negative Energy Flood", 5, "necromancy",
    "1 action", 60, ["V", "M"], "Instantaneous", False,
    "You send ribbons of negative energy at one creature you can see within range. The target must make a CON save, taking 5d12 necrotic damage on fail, or half on success. A target killed by this damage rises up as a zombie at the start of your next turn. The zombie pursues whatever creature is closest to it.",
    ["warlock", "wizard"],
    damage_dice="5d12", damage_type="necrotic", save_ability="CON", effect_type="damage", area_type="single",
))

_sp(Spell(
    "skill-empowerment", "Skill Empowerment", 5, "transmutation",
    "1 action", 0, ["V", "S"], "Concentration, up to 1 hour", True,
    "Your magic deepens a creature's understanding of its own talent. You touch one willing creature and give it expertise in one skill of your choice; the creature's proficiency bonus is doubled for any ability check it makes that uses the chosen skill. You must choose a skill in which the target is already proficient.",
    ["bard", "sorcerer", "wizard"],
    effect_type="buff",
))

_sp(Spell(
    "far-step", "Far Step", 5, "conjuration",
    "1 bonus action", 0, ["V"], "Concentration, up to 1 minute", True,
    "You teleport up to 60 feet to an unoccupied space you can see. On each of your turns before the spell ends, you can use a bonus action to teleport in this way again.",
    ["sorcerer", "warlock", "wizard"],
    effect_type="utility",
))

_sp(Spell(
    "infernal-calling", "Infernal Calling", 5, "conjuration",
    "1 minute", 90, ["V", "S", "M"], "Concentration, up to 1 hour", True,
    "Uttering a dark incantation, you summon a devil from the Nine Hells. You choose the devil's type, which must be one of challenge rating 6 or lower. The devil is unfriendly toward you and your companions. Roll Charisma checks to command it.",
    ["warlock", "wizard"],
    effect_type="summon",
    at_higher_levels="Challenge rating of the devil increases by 1 for each slot level above 5th.",
))

_sp(Spell(
    "summon-celestial", "Summon Celestial", 5, "conjuration",
    "1 action", 90, ["V", "S", "M"], "Concentration, up to 1 hour", True,
    "You call forth a celestial spirit. It manifests in an angelic form in an unoccupied space that you can see within range. Choose a type: Avenger or Defender.",
    ["cleric", "paladin"],
    effect_type="summon",
    at_higher_levels="The creature gains additional HP and damage when using a higher level slot.",
))

_sp(Spell(
    "summon-draconic-spirit", "Summon Draconic Spirit", 5, "conjuration",
    "1 action", 60, ["V", "S", "M"], "Concentration, up to 1 hour", True,
    "You call forth a draconic spirit. It manifests in an unoccupied space that you can see within range. Choose a family of dragon: Chromatic, Gem, or Metallic. The spirit takes the form of a dragon and shares the resistance associated with its family.",
    ["druid", "sorcerer", "wizard"],
    effect_type="summon",
    at_higher_levels="The creature gains additional HP and damage when using a higher level slot.",
))


# ═══════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_spell(spell_id: str) -> Spell | None:
    """Return a spell by its id, or None if not found."""
    return SPELLS.get(spell_id)


def list_spells() -> list[Spell]:
    """Return all registered spells."""
    return list(SPELLS.values())


def get_spells_for_class(class_id: str, max_level: int = 9) -> list[Spell]:
    """Return all spells available to a class up to max_level."""
    return [s for s in SPELLS.values() if class_id in s.classes and s.level <= max_level]


def get_cantrips_for_class(class_id: str) -> list[Spell]:
    """Return all cantrips (level 0) available to a class."""
    return [s for s in SPELLS.values() if class_id in s.classes and s.level == 0]


def get_spells_by_school(school: str) -> list[Spell]:
    """Return all spells of a given school (e.g. 'evocation')."""
    return [s for s in SPELLS.values() if s.school == school]


def get_spells_by_level(level: int) -> list[Spell]:
    """Return all spells of a given level (0 = cantrips)."""
    return [s for s in SPELLS.values() if s.level == level]
