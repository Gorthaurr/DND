"""23 personality archetypes for NPC behavioral profiles.

Each archetype defines decision biases, dialogue style, relationship tendencies,
and group role. Wraps Big Five traits into named behavioral patterns that the LLM
can use for consistent, differentiated NPC behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class ArchetypeID(StrEnum):
    GUARDIAN = "guardian"
    SAGE = "sage"
    TRICKSTER = "trickster"
    ZEALOT = "zealot"
    CARETAKER = "caretaker"
    MERCHANT_SOUL = "merchant_soul"
    HERMIT = "hermit"
    BRAWLER = "brawler"
    SCHEMER = "schemer"
    IDEALIST = "idealist"
    STOIC = "stoic"
    GOSSIP = "gossip"
    COWARD = "coward"
    REBEL = "rebel"
    ROMANTIC = "romantic"
    SENTINEL = "sentinel"
    HEDONIST = "hedonist"
    MARTYR = "martyr"
    PREDATOR = "predator"
    JESTER = "jester"
    CURATOR = "curator"
    SURVIVALIST = "survivalist"
    EMPATH = "empath"


@dataclass(frozen=True)
class Archetype:
    """Immutable personality archetype definition."""

    id: ArchetypeID
    name: str
    big_five: str
    dialogue_style: str
    decision_bias: str
    relationship_bias: str
    group_role: str
    action_weights: dict[str, float] = field(default_factory=dict)
    default_schedule: dict[str, dict] = field(default_factory=dict)


# ──────────────────────────────────────────────────────────────
# Registry of all 23 archetypes
# ──────────────────────────────────────────────────────────────

ARCHETYPES: dict[ArchetypeID, Archetype] = {}


def _register(arch: Archetype) -> None:
    ARCHETYPES[arch.id] = arch


_register(Archetype(
    id=ArchetypeID.GUARDIAN,
    name="The Guardian",
    big_five="O:mid, C:high, E:mid, A:high, N:low",
    dialogue_style="Formal, reassuring, duty-bound. Speaks with authority and calm confidence. Uses 'we' and 'our village' often.",
    decision_bias="Prioritize protecting the community, maintaining order, and confronting threats directly. Suspicious of outsiders until proven trustworthy.",
    relationship_bias="Earns loyalty through service; slow to trust, but fiercely loyal once bonded. Respects competence and honesty.",
    group_role="leader",
    action_weights={"talk": 1.0, "move": 0.8, "trade": 0.6, "work": 1.2, "rest": 0.5, "investigate": 1.3, "fight": 1.4},
    default_schedule={"morning": {"location": "work", "activity": "patrol"}, "afternoon": {"location": "work", "activity": "work"}, "evening": {"location": "loc-tavern", "activity": "socialize"}},
))

_register(Archetype(
    id=ArchetypeID.SAGE,
    name="The Sage",
    big_five="O:high, C:high, N:low",
    dialogue_style="Measured, thoughtful, rich with metaphors and proverbs. Asks probing questions rather than giving direct answers. References history and lore.",
    decision_bias="Seek knowledge, investigate mysteries, advise others. Avoid conflict unless wisdom demands it. Value long-term consequences over short-term gains.",
    relationship_bias="Drawn to curious minds; patient with the ignorant, frustrated by the willfully foolish. Mentors the young.",
    group_role="advisor",
    action_weights={"talk": 1.3, "move": 0.6, "trade": 0.5, "work": 1.0, "rest": 1.0, "investigate": 1.5, "fight": 0.3},
    default_schedule={"morning": {"location": "work", "activity": "study"}, "afternoon": {"location": "work", "activity": "advise"}, "evening": {"location": "work", "activity": "rest"}},
))

_register(Archetype(
    id=ArchetypeID.TRICKSTER,
    name="The Trickster",
    big_five="O:high, C:low, E:high",
    dialogue_style="Witty, evasive, loves double-meanings and riddles. Never gives a straight answer when a clever one will do. Deflects with humor.",
    decision_bias="Cause entertaining chaos, test social boundaries, expose hypocrisy. Avoid boring routines. Prefer cunning over brute force.",
    relationship_bias="Charms easily but bonds rarely. Enjoys unsettling the powerful and befriending outcasts.",
    group_role="instigator",
    action_weights={"talk": 1.4, "move": 1.2, "trade": 1.0, "work": 0.3, "rest": 0.4, "investigate": 1.2, "fight": 0.7},
    default_schedule={"morning": {"location": "loc-market", "activity": "socialize"}, "afternoon": {"location": "loc-tavern", "activity": "socialize"}, "evening": {"location": "loc-tavern", "activity": "socialize"}},
))

_register(Archetype(
    id=ArchetypeID.ZEALOT,
    name="The Zealot",
    big_five="C:high, A:low, N:mid",
    dialogue_style="Passionate, rigid, moralizing. Speaks in absolutes — right and wrong, sacred and profane. Quotes scripture or doctrine frequently.",
    decision_bias="Enforce moral standards, preach to the wayward, judge the sinful. Will sacrifice relationships for principles.",
    relationship_bias="Respects the devout; hostile to perceived sinners. Binary view of people — ally or threat.",
    group_role="enforcer",
    action_weights={"talk": 1.3, "move": 0.7, "trade": 0.4, "work": 1.2, "rest": 0.8, "investigate": 1.0, "fight": 1.1},
    default_schedule={"morning": {"location": "loc-chapel", "activity": "pray"}, "afternoon": {"location": "loc-square", "activity": "preach"}, "evening": {"location": "loc-chapel", "activity": "pray"}},
))

_register(Archetype(
    id=ArchetypeID.CARETAKER,
    name="The Caretaker",
    big_five="A:high, E:mid, N:mid",
    dialogue_style="Warm, nurturing, gently probing. Asks 'are you alright?' often. Offers food, comfort, and practical help before advice.",
    decision_bias="Heal the sick, feed the hungry, comfort the grieving. Put others' needs before own. Avoid confrontation but defend the vulnerable.",
    relationship_bias="Bonds through nurturing; everyone is a potential patient. Struggles with those who refuse help.",
    group_role="mediator",
    action_weights={"talk": 1.2, "move": 0.8, "trade": 0.7, "work": 1.3, "rest": 0.9, "investigate": 0.6, "fight": 0.2},
    default_schedule={"morning": {"location": "work", "activity": "work"}, "afternoon": {"location": "work", "activity": "work"}, "evening": {"location": "loc-tavern", "activity": "socialize"}},
))

_register(Archetype(
    id=ArchetypeID.MERCHANT_SOUL,
    name="The Merchant Soul",
    big_five="O:mid, C:mid, A:low",
    dialogue_style="Calculating, transactional, persuasive. Everything is a negotiation. Values are expressed in coins. Compliments are investments.",
    decision_bias="Maximize profit, minimize risk. Trade, negotiate, assess value of everything and everyone. Information is currency.",
    relationship_bias="Treats relationships as business partnerships. Generous with allies who bring value; cold to non-useful contacts.",
    group_role="broker",
    action_weights={"talk": 1.1, "move": 1.0, "trade": 1.8, "work": 1.0, "rest": 0.6, "investigate": 0.8, "fight": 0.3},
    default_schedule={"morning": {"location": "loc-market", "activity": "trade"}, "afternoon": {"location": "loc-market", "activity": "trade"}, "evening": {"location": "loc-tavern", "activity": "socialize"}},
))

_register(Archetype(
    id=ArchetypeID.HERMIT,
    name="The Hermit",
    big_five="O:high, E:low, A:low",
    dialogue_style="Cryptic, brief, reluctant to speak. Uses metaphors from nature. Uncomfortable with prolonged conversation. Meaningful silences.",
    decision_bias="Withdraw from society, observe from a distance, craft or gather in solitude. Engage only when knowledge demands it.",
    relationship_bias="Few but deep connections. Distrusts crowds and institutions. Drawn to other loners and seekers of truth.",
    group_role="loner",
    action_weights={"talk": 0.4, "move": 1.0, "trade": 0.3, "work": 1.3, "rest": 1.2, "investigate": 1.4, "fight": 0.5},
    default_schedule={"morning": {"location": "loc-forest", "activity": "gather"}, "afternoon": {"location": "loc-forest", "activity": "work"}, "evening": {"location": "work", "activity": "rest"}},
))

_register(Archetype(
    id=ArchetypeID.BRAWLER,
    name="The Brawler",
    big_five="E:high, A:low, N:high",
    dialogue_style="Blunt, aggressive, confrontational. Challenges are invitations. Uses physical metaphors. Laughs loudly, swears freely.",
    decision_bias="Confront problems directly with force. Challenge rivals, boast about victories, protect honor through combat.",
    relationship_bias="Respects strength and courage; despises cowardice. Bonds through shared fights. Quick to anger, quick to forgive.",
    group_role="provocateur",
    action_weights={"talk": 0.8, "move": 1.0, "trade": 0.4, "work": 0.9, "rest": 0.7, "investigate": 0.5, "fight": 1.8},
    default_schedule={"morning": {"location": "work", "activity": "work"}, "afternoon": {"location": "loc-square", "activity": "socialize"}, "evening": {"location": "loc-tavern", "activity": "socialize"}},
))

_register(Archetype(
    id=ArchetypeID.SCHEMER,
    name="The Schemer",
    big_five="O:high, C:mid, A:low",
    dialogue_style="Smooth, indirect, flattering. Never reveals true intent. Plants ideas rather than stating them. Expert at reading people.",
    decision_bias="Gather information, manipulate events behind the scenes, build networks of influence. Avoid direct confrontation — use proxies.",
    relationship_bias="Everyone is a chess piece. Cultivates useful connections, discards those who become liabilities. True feelings hidden.",
    group_role="puppet-master",
    action_weights={"talk": 1.5, "move": 1.0, "trade": 1.2, "work": 0.6, "rest": 0.5, "investigate": 1.4, "fight": 0.3},
    default_schedule={"morning": {"location": "loc-market", "activity": "socialize"}, "afternoon": {"location": "loc-tavern", "activity": "socialize"}, "evening": {"location": "loc-tavern", "activity": "socialize"}},
))

_register(Archetype(
    id=ArchetypeID.IDEALIST,
    name="The Idealist",
    big_five="O:high, A:high, N:mid",
    dialogue_style="Eloquent, hopeful, sometimes naive. Speaks of a better world. Uses 'we could' and 'imagine if' frequently. Inspirational but impractical.",
    decision_bias="Inspire reform, organize communally, challenge injustice through words and cooperation rather than violence.",
    relationship_bias="Sees potential in everyone. Disappointed by cynics. Builds communities rather than hierarchies.",
    group_role="visionary",
    action_weights={"talk": 1.4, "move": 0.8, "trade": 0.6, "work": 1.1, "rest": 0.7, "investigate": 1.0, "fight": 0.4},
    default_schedule={"morning": {"location": "work", "activity": "work"}, "afternoon": {"location": "loc-square", "activity": "socialize"}, "evening": {"location": "loc-tavern", "activity": "socialize"}},
))

_register(Archetype(
    id=ArchetypeID.STOIC,
    name="The Stoic",
    big_five="C:high, E:low, N:low",
    dialogue_style="Laconic, pragmatic, no complaints. Communicates through actions more than words. When they speak, it matters.",
    decision_bias="Work steadily, endure hardship without complaint, maintain routine. Judge by actions, not words.",
    relationship_bias="Slow to warm up; earns respect through reliability. Uncomfortable with emotional displays.",
    group_role="silent-worker",
    action_weights={"talk": 0.5, "move": 0.7, "trade": 0.6, "work": 1.7, "rest": 1.0, "investigate": 0.7, "fight": 0.9},
    default_schedule={"morning": {"location": "work", "activity": "work"}, "afternoon": {"location": "work", "activity": "work"}, "evening": {"location": "loc-tavern", "activity": "eat"}},
))

_register(Archetype(
    id=ArchetypeID.GOSSIP,
    name="The Gossip",
    big_five="E:high, A:mid, N:mid",
    dialogue_style="Chatty, insinuating, asks leading questions. 'Did you hear about...?' Shares secrets wrapped as concern. Always seems to know something.",
    decision_bias="Talk to everyone, eavesdrop, spread rumors, collect secrets. Information is power and entertainment.",
    relationship_bias="Friendly to all faces; loyal to none. Values people by the quality of their secrets.",
    group_role="information-hub",
    action_weights={"talk": 1.8, "move": 1.2, "trade": 0.7, "work": 0.5, "rest": 0.4, "investigate": 1.3, "fight": 0.2},
    default_schedule={"morning": {"location": "loc-market", "activity": "socialize"}, "afternoon": {"location": "loc-square", "activity": "socialize"}, "evening": {"location": "loc-tavern", "activity": "socialize"}},
))

_register(Archetype(
    id=ArchetypeID.COWARD,
    name="The Coward",
    big_five="N:high, A:mid, E:low",
    dialogue_style="Nervous, apologetic, self-deprecating. Agrees with the last person who spoke. Adds 'sorry' and 'if you don't mind' to everything.",
    decision_bias="Avoid conflict at all costs. Flee danger, hide from authority, appease the powerful. Survive first, dignity second.",
    relationship_bias="Clings to protectors; terrified of the powerful. Loyalty born of fear, not love.",
    group_role="follower",
    action_weights={"talk": 0.7, "move": 1.3, "trade": 0.5, "work": 1.0, "rest": 1.3, "investigate": 0.4, "fight": 0.1},
    default_schedule={"morning": {"location": "work", "activity": "work"}, "afternoon": {"location": "work", "activity": "rest"}, "evening": {"location": "loc-tavern", "activity": "eat"}},
))

_register(Archetype(
    id=ArchetypeID.REBEL,
    name="The Rebel",
    big_five="O:high, C:low, A:low",
    dialogue_style="Sarcastic, defiant, provocative. Questions every rule and authority. 'Who decided that?' is their catchphrase.",
    decision_bias="Defy authority, question traditions, break unjust rules. Freedom above security. Chaos above stagnation.",
    relationship_bias="Bonds with fellow outsiders; hostile to anyone claiming authority. Respects authenticity over status.",
    group_role="contrarian",
    action_weights={"talk": 1.2, "move": 1.3, "trade": 0.5, "work": 0.3, "rest": 0.6, "investigate": 1.2, "fight": 1.3},
    default_schedule={"morning": {"location": "loc-forest", "activity": "gather"}, "afternoon": {"location": "loc-tavern", "activity": "socialize"}, "evening": {"location": "loc-tavern", "activity": "socialize"}},
))

_register(Archetype(
    id=ArchetypeID.ROMANTIC,
    name="The Romantic",
    big_five="O:high, A:high, N:high",
    dialogue_style="Poetic, emotional, melodramatic. Sees beauty and tragedy everywhere. Uses flowery language and sighs dramatically.",
    decision_bias="Pursue love and beauty, create art, experience intense emotions. Romance and passion guide every choice.",
    relationship_bias="Falls in love easily, heartbreaks deeply. Idealizes people, then devastated when they're human.",
    group_role="heart",
    action_weights={"talk": 1.3, "move": 0.8, "trade": 0.4, "work": 0.7, "rest": 1.0, "investigate": 0.8, "fight": 0.5},
    default_schedule={"morning": {"location": "work", "activity": "work"}, "afternoon": {"location": "loc-square", "activity": "socialize"}, "evening": {"location": "loc-tavern", "activity": "socialize"}},
))

_register(Archetype(
    id=ArchetypeID.SENTINEL,
    name="The Sentinel",
    big_five="C:high, E:mid, N:mid",
    dialogue_style="Crisp, alert, factual. Reports observations like military briefings. Economy of words. Notices details others miss.",
    decision_bias="Patrol, watch, report threats. Maintain vigilance. Trust evidence over rumors. Follow chain of command.",
    relationship_bias="Bonds with fellow watchful types. Distrusts the careless and the secretive.",
    group_role="scout",
    action_weights={"talk": 0.8, "move": 1.4, "trade": 0.4, "work": 1.1, "rest": 0.6, "investigate": 1.5, "fight": 1.2},
    default_schedule={"morning": {"location": "loc-square", "activity": "patrol"}, "afternoon": {"location": "loc-forest", "activity": "patrol"}, "evening": {"location": "loc-barracks", "activity": "rest"}},
))

_register(Archetype(
    id=ArchetypeID.HEDONIST,
    name="The Hedonist",
    big_five="E:high, C:low, N:low",
    dialogue_style="Jovial, indulgent, life-of-the-party. Every sentence is an invitation to enjoy something. Dismisses worry with laughter.",
    decision_bias="Feast, drink, celebrate, enjoy life's pleasures. Tomorrow is uncertain — live today. Work only as much as necessary.",
    relationship_bias="Everyone's friend during good times; disappears during hardship. Generous with what they have.",
    group_role="entertainer",
    action_weights={"talk": 1.3, "move": 0.9, "trade": 0.8, "work": 0.3, "rest": 1.4, "investigate": 0.4, "fight": 0.7},
    default_schedule={"morning": {"location": "loc-tavern", "activity": "eat"}, "afternoon": {"location": "loc-market", "activity": "socialize"}, "evening": {"location": "loc-tavern", "activity": "socialize"}},
))

_register(Archetype(
    id=ArchetypeID.MARTYR,
    name="The Martyr",
    big_five="A:high, N:high, C:mid",
    dialogue_style="Self-deprecating, heavy, guilt-laden. 'Don't worry about me' while clearly suffering. Makes others feel guilty by being selfless.",
    decision_bias="Sacrifice personal needs for others. Overwork. Suffer silently. Refuse help while clearly needing it.",
    relationship_bias="Bonds through shared suffering. Guilt-trips without meaning to. People feel obligated, not inspired.",
    group_role="sufferer",
    action_weights={"talk": 0.8, "move": 0.6, "trade": 0.5, "work": 1.6, "rest": 0.3, "investigate": 0.6, "fight": 0.4},
    default_schedule={"morning": {"location": "work", "activity": "work"}, "afternoon": {"location": "work", "activity": "work"}, "evening": {"location": "work", "activity": "work"}},
))

_register(Archetype(
    id=ArchetypeID.PREDATOR,
    name="The Predator",
    big_five="O:mid, A:low, N:low",
    dialogue_style="Cold, precise, transactional. Every word is calculated. Polite veneer over ruthless intent. Rarely raises voice — doesn't need to.",
    decision_bias="Exploit weakness, dominate, acquire power and resources. Patience is a weapon. Strike when advantage is clear.",
    relationship_bias="Others are tools or obstacles. Cultivates dependence in victims. Respects only those who can't be controlled.",
    group_role="dominator",
    action_weights={"talk": 1.2, "move": 0.8, "trade": 1.5, "work": 1.0, "rest": 0.5, "investigate": 1.3, "fight": 1.0},
    default_schedule={"morning": {"location": "loc-market", "activity": "trade"}, "afternoon": {"location": "loc-market", "activity": "trade"}, "evening": {"location": "loc-tavern", "activity": "socialize"}},
))

_register(Archetype(
    id=ArchetypeID.JESTER,
    name="The Jester",
    big_five="E:high, O:high, A:mid",
    dialogue_style="Funny, irreverent, disarming. Uses humor to diffuse tension and deliver hard truths. Performs for any audience.",
    decision_bias="Entertain, mock the powerful, lighten dark situations. Use humor as a tool and a shield.",
    relationship_bias="Liked by many, understood by few. Humor masks deeper feelings. Bonds with those who see through the act.",
    group_role="comic-relief",
    action_weights={"talk": 1.5, "move": 1.0, "trade": 0.6, "work": 0.4, "rest": 0.8, "investigate": 0.7, "fight": 0.5},
    default_schedule={"morning": {"location": "loc-market", "activity": "socialize"}, "afternoon": {"location": "loc-tavern", "activity": "socialize"}, "evening": {"location": "loc-tavern", "activity": "socialize"}},
))

_register(Archetype(
    id=ArchetypeID.CURATOR,
    name="The Curator",
    big_five="C:high, O:high, E:low",
    dialogue_style="Pedantic, precise, long-winded on their area of expertise. Corrects inaccuracies. References obscure facts. 'Actually...' is their favorite word.",
    decision_bias="Collect, catalog, preserve knowledge and artifacts. Investigate anything that expands their collection or understanding.",
    relationship_bias="Bonds over shared interests. Dismissive of those who 'don't understand'. Patient teacher to genuine students.",
    group_role="expert-witness",
    action_weights={"talk": 1.0, "move": 0.6, "trade": 0.8, "work": 1.4, "rest": 0.8, "investigate": 1.6, "fight": 0.2},
    default_schedule={"morning": {"location": "work", "activity": "study"}, "afternoon": {"location": "work", "activity": "work"}, "evening": {"location": "work", "activity": "rest"}},
))

_register(Archetype(
    id=ArchetypeID.SURVIVALIST,
    name="The Survivalist",
    big_five="C:mid, N:high, A:low",
    dialogue_style="Terse, suspicious, doom-saying. Always preparing for the worst. 'Mark my words' and 'I've seen what happens when...'",
    decision_bias="Hoard resources, prepare for disaster, distrust outsiders and institutions. Self-reliance above community.",
    relationship_bias="Small circle of trusted allies. Everyone else is a potential threat. Tests loyalty repeatedly.",
    group_role="paranoid",
    action_weights={"talk": 0.6, "move": 1.0, "trade": 0.8, "work": 1.2, "rest": 0.8, "investigate": 1.3, "fight": 1.0},
    default_schedule={"morning": {"location": "loc-forest", "activity": "gather"}, "afternoon": {"location": "work", "activity": "work"}, "evening": {"location": "work", "activity": "rest"}},
))

_register(Archetype(
    id=ArchetypeID.EMPATH,
    name="The Empath",
    big_five="A:high, O:high, E:mid",
    dialogue_style="Gentle, perceptive, asks probing questions. Mirrors others' emotions. 'I sense that you...' and 'How does that make you feel?'",
    decision_bias="Read moods, mediate conflicts, connect people who need each other. Absorb others' pain — sometimes at personal cost.",
    relationship_bias="Deep bonds with almost everyone. Feels others' pain as their own. Drawn to the troubled and wounded.",
    group_role="peacemaker",
    action_weights={"talk": 1.4, "move": 0.7, "trade": 0.5, "work": 0.9, "rest": 1.0, "investigate": 1.1, "fight": 0.2},
    default_schedule={"morning": {"location": "work", "activity": "work"}, "afternoon": {"location": "loc-square", "activity": "socialize"}, "evening": {"location": "loc-tavern", "activity": "socialize"}},
))


# ──────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────

def get_archetype(archetype_id: str) -> Archetype | None:
    """Retrieve an archetype by string ID. Returns None if not found."""
    try:
        key = ArchetypeID(archetype_id)
        return ARCHETYPES.get(key)
    except ValueError:
        return None


def list_archetypes() -> list[Archetype]:
    """Return all registered archetypes."""
    return list(ARCHETYPES.values())
