"""REST API endpoints."""

import json as _json
import time
from pathlib import Path

from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import StreamingResponse

from app.agents.dm_agent import dm_agent
from app.agents.npc_agent import npc_agent
from app.api.schemas import (
    ActionRequest,
    ActionResponse,
    DialogueInterjection,
    DialogueRequest,
    DialogueResponse,
    LookResponse,
    NPCObserveResponse,
    TickResponse,
    WorldLogResponse,
    WorldMapResponse,
    WorldStateResponse,
)
from app.config import settings
from app.graph.connection import get_driver
from app.graph.queries import GraphQueries
from app.graph.seed import seed_world
from app.models.memory import (
    add_memory,
    clear_all_memories,
    get_memory_count,
    get_recent_memories,
    init_memory_db,
    search_memories,
)
from app.models.npc import NPCContext, NPCRelationship
from app.simulation.ticker import run_world_tick
from app.utils.logger import get_logger

log = get_logger("api")
router = APIRouter()

PLAYER_ID = "player-1"

# World log storage (in-memory, persists across requests)
_world_log: list[dict] = []

# ── Autosave persistence ─────────────────────────────────────────────────
AUTOSAVE_PATH = Path("worlds/saves/autosave.json")
WORLD_LOG_PATH = Path("worlds/world_log.json")

def _save_world_log():
    """Persist world log to disk."""
    try:
        WORLD_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        WORLD_LOG_PATH.write_text(_json.dumps(_world_log[-50:], default=str, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

def _load_world_log():
    """Load world log from disk on startup."""
    global _world_log
    if WORLD_LOG_PATH.exists():
        try:
            _world_log = _json.loads(WORLD_LOG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass

# Load on import
_load_world_log()

# ── Chat log persistence ─────────────────────────────────────────────────
CHAT_LOG_PATH = Path("worlds/chat_log.json")


def _load_chat_log() -> list[dict]:
    if CHAT_LOG_PATH.exists():
        try:
            return _json.loads(CHAT_LOG_PATH.read_text(encoding="utf-8"))[-100:]
        except Exception:
            return []
    return []


def _save_chat_entry(entry: dict):
    log = _load_chat_log()
    log.append(entry)
    log = log[-100:]
    CHAT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CHAT_LOG_PATH.write_text(_json.dumps(log, ensure_ascii=False), encoding="utf-8")


def _gq() -> GraphQueries:
    return GraphQueries(get_driver())


# ── Chat History ──────────────────────────────────────────────────────────


@router.get("/chat/history")
async def get_chat_history():
    """Return recent chat messages."""
    return {"messages": _load_chat_log()}


# ── Actions ──────────────────────────────────────────────────────────────


@router.post("/action", response_model=ActionResponse)
async def player_action(req: ActionRequest):
    """Process a player action through the DM."""
    gq = _gq()

    player = await gq.get_player(PLAYER_ID)
    if not player:
        raise HTTPException(404, "Player not found")

    location = await gq.get_player_location(PLAYER_ID)
    if not location:
        raise HTTPException(400, "Player has no location")

    present_npcs = await gq.get_npcs_at_location(location["id"])
    recent_events = await gq.get_recent_events(max(1, player.get("day", 1) - 3))
    player_items = await gq.get_player_items(PLAYER_ID)

    # Check for movement
    action_lower = req.action.lower()
    moved = False
    if action_lower.startswith("go ") or action_lower.startswith("move "):
        target = req.action.split(" ", 1)[1] if " " in req.action else ""
        # Strip common prepositions
        for prefix in ("to ", "the ", "to the "):
            if target.lower().startswith(prefix):
                target = target[len(prefix):]
        connected = await gq.get_connected_locations(location["id"])
        for loc in connected:
            if target.lower() in loc["name"].lower():
                await gq.set_player_location(PLAYER_ID, loc["id"])
                location = loc
                present_npcs = await gq.get_npcs_at_location(loc["id"])
                moved = True
                break

        if moved:
            npc_names = [n["name"] for n in present_npcs]
            narration = f"You make your way to {location['name']}. {location['description']}"
            if npc_names:
                narration += f" You notice {', '.join(npc_names)} here."
            _save_chat_entry({"type": "system", "content": f"Moved to {location['name']}. {narration}", "timestamp": int(time.time() * 1000)})
            return ActionResponse(
                narration=narration,
                npcs_involved=[],
                location=dict(location),
                items_changed=[],
            )
        else:
            # Location not found — still call DM
            pass

    # ── COMBAT PATH: detect combat intent and resolve with D&D mechanics ──
    from app.agents.combat_agent import combat_agent as _combat_agent
    combat_keywords = ["attack", "fight", "strike", "stab", "slash", "shoot", "kill", "punch", "hit",
                       "атакую", "бью", "убиваю", "дерусь", "ударяю", "стреляю", "режу"]
    might_be_combat = any(kw in action_lower for kw in combat_keywords)

    if might_be_combat and present_npcs:
        intent = await _combat_agent.parse_combat_intent(
            player_action=req.action,
            present_npcs=present_npcs,
            player=player,
        )

        if intent.get("is_combat") and intent.get("targets"):
            # Gather target NPC full data
            target_npcs = []
            for t in intent["targets"]:
                npc_data = await gq.get_npc(t["npc_id"])
                if npc_data and npc_data.get("alive", True):
                    target_npcs.append(npc_data)

            # Gather hostile allies who join the fight
            hostile_npcs = []
            for npc_id in intent.get("npcs_join_fight", []):
                npc_data = await gq.get_npc(npc_id)
                if npc_data and npc_data.get("alive", True):
                    hostile_npcs.append(npc_data)

            if target_npcs:
                # DETERMINISTIC COMBAT via D&D dice
                encounter = _combat_agent.resolve_combat(
                    player_data=player,
                    target_npcs=target_npcs,
                    hostile_npcs=hostile_npcs if hostile_npcs else None,
                )

                # DM narrates the structured results
                narration = await dm_agent.narrate_combat(
                    combat_log=encounter.combat_log,
                    initiative_order=encounter.initiative_order,
                    player_hp_change=encounter.player_hp_change,
                    player_killed=encounter.player_killed,
                    npcs_killed=encounter.npcs_killed,
                    location_name=location["name"],
                    present_npcs=present_npcs,
                    lang=req.lang,
                )

                # Apply NPC damage via deterministic results
                from app.models.memory import init_memory_db, add_memory
                init_memory_db()
                actual_killed = []
                for npc_id, total_dmg in encounter.npcs_damaged.items():
                    updated = await gq.damage_npc(npc_id, total_dmg)
                    if updated and not updated.get("alive", True):
                        actual_killed.append(npc_id)

                # Apply player HP change
                player_hp_change = encounter.player_hp_change
                if player_hp_change != 0:
                    current_hp = player.get("current_hp", player.get("max_hp", 10))
                    max_hp = player.get("max_hp", 10)
                    new_hp = max(0, min(max_hp, current_hp + player_hp_change))
                    async with gq._session() as s:
                        await s.run("MATCH (p:Player {id: $id}) SET p.current_hp = $hp",
                                    id=PLAYER_ID, hp=new_hp)

                if encounter.player_killed:
                    async with gq._session() as s:
                        await s.run("MATCH (p:Player {id: $id}) SET p.current_hp = 0", id=PLAYER_ID)

                # Apply kill cascades
                for npc_id in actual_killed:
                    try:
                        killed_npc = await gq.get_npc(npc_id)
                        killed_name = killed_npc["name"] if killed_npc else npc_id

                        try:
                            from app.models.world_store import WorldStore
                            ws = WorldStore()
                            ws.update_npc("medieval_village", npc_id, {"alive": False, "mood": "dead", "current_hp": 0})
                        except Exception:
                            pass

                        # Cascade: inform related NPCs
                        victim_relations = await gq.get_relationships(npc_id)
                        witnesses = await gq.get_npcs_at_location(location["id"])
                        world_day = player.get("day", 1)
                        for rel in victim_relations:
                            other_id = rel["id"]
                            other_npc = await gq.get_npc(other_id)
                            if not other_npc or not other_npc.get("alive", True):
                                continue
                            sentiment = rel.get("sentiment", 0)
                            was_witness = any(w["id"] == other_id for w in witnesses)
                            if sentiment > 0.3:
                                add_memory(other_id, f"Day {world_day}: The adventurer KILLED {killed_name}!", day=world_day, importance=0.9)
                                await gq.update_npc(other_id, {"mood": "angry"})
                            elif sentiment < -0.3:
                                add_memory(other_id, f"Day {world_day}: The adventurer killed {killed_name}. Good riddance.", day=world_day, importance=0.7)
                                await gq.update_npc(other_id, {"mood": "content"})
                            else:
                                add_memory(other_id, f"Day {world_day}: The adventurer killed {killed_name}. Terrifying.", day=world_day, importance=0.8)
                                await gq.update_npc(other_id, {"mood": "fearful" if was_witness else "worried"})
                    except Exception as e:
                        log.warning("combat_kill_cascade_failed", npc_id=npc_id, error=str(e))

                # Save chat entries
                _save_chat_entry({"type": "player", "content": req.action, "timestamp": int(time.time() * 1000)})
                _save_chat_entry({"type": "dm", "content": narration, "timestamp": int(time.time() * 1000)})

                resp = ActionResponse(
                    narration=narration,
                    npcs_involved=[t["npc_id"] for t in intent["targets"]],
                    npcs_killed=actual_killed,
                    location=dict(location),
                    items_changed=[],
                    player_hp_change=player_hp_change,
                    player_killed=encounter.player_killed,
                    combat_rolls=[r for r in encounter.all_rolls],
                )
                xp_result = await gq.add_player_xp(PLAYER_ID, 25 if actual_killed else 10)
                if xp_result.get("leveled_up"):
                    resp.level_up = {"level": xp_result["new_level"], "max_hp": xp_result["new_max_hp"]}
                return resp

    # ── NON-COMBAT PATH: DM narrates the action ──

    # Enrich NPC data with combat stats and equipment summary
    enriched_npcs = []
    for npc in present_npcs:
        npc_data = dict(npc)
        # Build equipment summary from equipment_ids
        equip_ids = npc_data.get("equipment_ids", [])
        if equip_ids:
            from app.dnd.equipment import get_weapon, get_armor
            parts = []
            for eid in (equip_ids if isinstance(equip_ids, list) else []):
                w = get_weapon(eid)
                if w:
                    parts.append(f"{w.name} ({w.damage_dice})")
                a = get_armor(eid)
                if a:
                    parts.append(f"{a.name} (AC {a.ac_base})")
            npc_data["equipment_summary"] = ", ".join(parts) if parts else None
        enriched_npcs.append(npc_data)

    # Get dead NPCs at location for context
    dead_npcs = await gq.get_dead_npcs_at_location(location["id"])

    # Build recent chat context from chat log
    chat_log = _load_chat_log()
    recent_chat = [
        f"{'Player' if e.get('type') == 'player' else e.get('npc_name', 'DM')}: {e.get('content', '')}"
        for e in chat_log[-10:]
    ]

    result = await dm_agent.narrate(
        player_action=req.action,
        location_name=location["name"],
        location_description=location["description"],
        present_npcs=enriched_npcs,
        recent_events=[e["description"] for e in recent_events],
        inventory=[i["name"] for i in player_items],
        reputation=player.get("reputation", 0),
        world_day=player.get("day", 1),
        # Player combat stats
        player_level=player.get("level", 1),
        player_class=player.get("class_id", "commoner"),
        player_hp=player.get("current_hp", 10),
        player_max_hp=player.get("max_hp", 10),
        player_ac=player.get("ac", 10),
        time_of_day=player.get("time_of_day", "day"),
        dead_npcs=[{"id": n["id"], "name": n["name"], "occupation": n.get("occupation", "")} for n in dead_npcs],
        recent_chat=recent_chat,
        lang=req.lang,
    )

    # Apply location change if DM suggests one
    if result.get("location_changed"):
        all_locs = await gq.get_all_locations()
        for loc in all_locs:
            if result["location_changed"].lower() in loc["name"].lower():
                await gq.set_player_location(PLAYER_ID, loc["id"])
                location = loc
                break

    # ── Fallback kill detection: if LLM didn't return npcs_killed but narration implies death ──
    npcs_killed = list(result.get("npcs_killed", []))
    if not npcs_killed:
        narration_lower = result.get("narration", "").lower()
        kill_words = ["lies motionless", "falls dead", "killed", "slain", "dies", "collapsed lifeless", "throat", "stab"]
        if any(w in narration_lower for w in kill_words):
            action_lower = req.action.lower()
            for npc in present_npcs:
                npc_name_lower = npc["name"].lower()
                # Check if NPC is mentioned in the action AND narration suggests death
                if any(part in npc_name_lower for part in action_lower.split() if len(part) > 2):
                    if any(w in narration_lower for w in kill_words):
                        npcs_killed.append(npc["id"])
                        break
    result["npcs_killed"] = npcs_killed

    # Apply NPC kills — mark as dead + cascade consequences
    from app.models.memory import add_memory
    for npc_id in npcs_killed:
        try:
            killed_npc = await gq.get_npc(npc_id)
            killed_name = killed_npc["name"] if killed_npc else npc_id
            await gq.kill_npc(npc_id)
            log.info("npc_killed", npc_id=npc_id, by="player")

            # Persist kill to world JSON files
            try:
                from app.models.world_store import world_store
                # Find active world and update NPC alive status
                worlds = world_store.list_worlds()
                for w in worlds:
                    world_store.update_npc(w["id"], npc_id, {"alive": False, "mood": "dead"})
            except Exception:
                pass

            # ── CASCADE: Inform all NPCs who knew the victim ──
            victim_relations = await gq.get_relationships(npc_id)
            witnesses = await gq.get_npcs_at_location(location["id"])
            world_day = player.get("day", 1)

            for rel in victim_relations:
                other_id = rel["id"]
                other_npc = await gq.get_npc(other_id)
                if not other_npc or not other_npc.get("alive", True):
                    continue

                sentiment_to_victim = rel.get("sentiment", 0)
                was_witness = any(w["id"] == other_id for w in witnesses)

                if sentiment_to_victim > 0.3:
                    # Friend of victim → hates player, wants revenge
                    memory_text = f"Day {world_day}: The adventurer KILLED {killed_name}! " \
                                  f"{'I saw it happen with my own eyes!' if was_witness else 'I heard the terrible news.'} " \
                                  f"I will never forgive this."
                    new_mood = "angry" if sentiment_to_victim > 0.6 else "fearful"
                    rep_change = int(-40 * sentiment_to_victim)  # -12 to -40
                elif sentiment_to_victim < -0.3:
                    # Enemy of victim → grateful to player
                    memory_text = f"Day {world_day}: The adventurer killed {killed_name}. " \
                                  f"{'I witnessed it.' if was_witness else 'Word spread quickly.'} " \
                                  f"Good riddance, I say."
                    new_mood = "content"
                    rep_change = int(15 * abs(sentiment_to_victim))  # +5 to +15
                else:
                    # Neutral → shocked/fearful
                    memory_text = f"Day {world_day}: The adventurer killed {killed_name}. " \
                                  f"{'I was right there when it happened!' if was_witness else 'Everyone is talking about it.'} " \
                                  f"This is terrifying."
                    new_mood = "fearful" if was_witness else "worried"
                    rep_change = -20 if was_witness else -10

                add_memory(other_id, memory_text, day=world_day, importance=0.9)
                await gq.update_npc(other_id, {"mood": new_mood})

                try:
                    from app.simulation.reputation import update_reputation
                    await update_reputation(gq, PLAYER_ID, other_id, rep_change)
                except Exception:
                    pass

                log.info("kill_cascade", npc=other_npc["name"], mood=new_mood, rep=rep_change,
                         relation_to_victim=sentiment_to_victim, witness=was_witness)

        except Exception as e:
            log.warning("npc_kill_failed", npc_id=npc_id, error=str(e))

    # Apply NPC mood changes from DM
    for npc_id, new_mood in result.get("npcs_mood_changes", {}).items():
        try:
            await gq.update_npc(npc_id, {"mood": new_mood})
        except Exception:
            pass

    # Apply reputation changes from DM
    for npc_id, change in result.get("reputation_changes", {}).items():
        try:
            from app.simulation.reputation import update_reputation
            await update_reputation(gq, PLAYER_ID, npc_id, change)
        except Exception:
            pass

    # Apply player HP changes
    player_hp_change = result.get("player_hp_change", 0)
    if player_hp_change != 0:
        current_hp = player.get("current_hp", player.get("max_hp", 10))
        max_hp = player.get("max_hp", 10)
        new_hp = max(0, min(max_hp, current_hp + player_hp_change))
        # Update player HP — players are stored as Player nodes
        async with gq._session() as s:
            await s.run(
                "MATCH (p:Player {id: $id}) SET p.current_hp = $hp",
                id=PLAYER_ID, hp=new_hp,
            )

    # Handle player death
    if result.get("player_killed"):
        async with gq._session() as s:
            await s.run(
                "MATCH (p:Player {id: $id}) SET p.current_hp = 0",
                id=PLAYER_ID,
            )

    # Save chat entries
    _save_chat_entry({"type": "player", "content": req.action, "timestamp": int(time.time() * 1000)})
    _save_chat_entry({"type": "dm", "content": result.get("narration", ""), "timestamp": int(time.time() * 1000)})

    # Grant XP for action
    resp = ActionResponse(
        narration=result["narration"],
        npcs_involved=result.get("npcs_involved", []),
        npcs_killed=result.get("npcs_killed", []),
        location=dict(location),
        items_changed=result.get("items_changed", []),
        player_hp_change=result.get("player_hp_change", 0),
        player_killed=result.get("player_killed", False),
    )
    xp_result = await gq.add_player_xp(PLAYER_ID, 10)
    if xp_result.get("leveled_up"):
        resp.level_up = {"level": xp_result["new_level"], "max_hp": xp_result["new_max_hp"]}

    return resp


# ── Dialogue ─────────────────────────────────────────────────────────────


@router.post("/dialogue", response_model=DialogueResponse)
async def player_dialogue(req: DialogueRequest):
    """Talk to an NPC."""
    gq = _gq()

    npc = await gq.get_npc(req.npc_id)
    if not npc:
        raise HTTPException(404, f"NPC {req.npc_id} not found")
    if not npc.get("alive", True):
        # Dead NPC -- save to chat log but return dead response
        _save_chat_entry({"type": "player", "content": f"[to {npc.get('name', '???')}] {req.message}", "timestamp": int(time.time() * 1000)})
        _save_chat_entry({"type": "npc", "content": "*lies motionless on the ground*", "npc_name": npc.get("name", "???"), "timestamp": int(time.time() * 1000)})
        return DialogueResponse(
            npc_name=npc.get("name", "???"),
            dialogue="*lies motionless on the ground*",
            mood="dead",
        )

    reputation = await gq.get_player_reputation(PLAYER_ID, req.npc_id)
    relationships = await gq.get_relationships(req.npc_id)

    # Find player relationship
    player_rel = None
    for r in relationships:
        if "player" in r.get("id", "").lower():
            player_rel = r
            break

    relevant = search_memories(req.npc_id, req.message, top_k=3)

    # Build recent chat context
    chat_log = _load_chat_log()
    recent_chat = [
        f"{'Player' if e.get('type') == 'player' else e.get('npc_name', 'DM')}: {e.get('content', '')}"
        for e in chat_log[-10:]
    ]

    result = await npc_agent.dialogue(
        npc=npc,
        message=req.message,
        other_name="the adventurer",
        relationship=player_rel,
        relevant_memories=relevant,
        is_player=True,
        reputation=reputation,
        recent_chat=recent_chat,
        lang=req.lang,
    )

    # Store memories for both NPC and player interaction
    init_memory_db()
    add_memory(req.npc_id, f"The adventurer said: \"{req.message}\". I replied: \"{result['dialogue']}\"")

    # Update sentiment
    if result.get("sentiment_change", 0) != 0:
        new_sentiment = min(1.0, max(-1.0, (player_rel or {}).get("sentiment", 0) + result["sentiment_change"]))
        await gq.set_relationship(req.npc_id, PLAYER_ID, new_sentiment, result.get("internal_thought", ""))

    # Update mood
    mood = npc["mood"]
    if result["mood_change"] == "better":
        mood = "content" if mood in ("angry", "fearful") else "excited"
    elif result["mood_change"] == "worse":
        mood = "angry" if mood in ("content", "excited") else "fearful"
    if mood != npc["mood"]:
        await gq.update_npc(req.npc_id, {"mood": mood})

    # Save chat entries
    _save_chat_entry({"type": "player", "content": f"[to {npc['name']}] {req.message}", "timestamp": int(time.time() * 1000)})
    _save_chat_entry({"type": "npc", "content": result["dialogue"], "npc_name": npc["name"], "timestamp": int(time.time() * 1000)})

    # Grant XP for dialogue
    await gq.add_player_xp(PLAYER_ID, 5)

    # Evaluate bystander interjections (up to 3 concurrent)
    interjections = []
    try:
        location = await gq.get_player_location(PLAYER_ID)
        if location:
            import asyncio
            bystanders = await gq.get_npcs_at_location(location["id"])
            bystanders = [b for b in bystanders if b["id"] != req.npc_id and b.get("alive", True)][:1]

            async def _eval_interjection(bystander):
                try:
                    bystander_rep = await gq.get_player_reputation(PLAYER_ID, bystander["id"])
                    bystander_rels = await gq.get_relationships(bystander["id"])
                    rel_to_target = "neutral"
                    for br in bystander_rels:
                        if br.get("id") == req.npc_id:
                            rel_to_target = f"sentiment {br['sentiment']}: {br.get('reason', '')}"
                            break
                    bystander_memories = search_memories(bystander["id"], req.message, top_k=2)

                    ij_result = await npc_agent.evaluate_interjection(
                        npc=bystander,
                        player_message=req.message,
                        target_npc_name=npc["name"],
                        target_npc_occupation=npc.get("occupation", ""),
                        target_reply=result["dialogue"],
                        player_reputation=bystander_rep,
                        relationship_to_target=rel_to_target,
                        relevant_memories=bystander_memories,
                        location_name=location.get("name", ""),
                        recent_chat=recent_chat,
                        lang=req.lang,
                    )
                    if ij_result.get("should_interject"):
                        return DialogueInterjection(
                            npc_name=bystander["name"],
                            npc_id=bystander["id"],
                            dialogue=ij_result["dialogue"],
                            mood=bystander.get("mood", "neutral"),
                        )
                except Exception:
                    pass
                return None

            ij_results = await asyncio.gather(*[_eval_interjection(b) for b in bystanders])
            interjections = [ij for ij in ij_results if ij is not None]

            # Save interjection chat entries
            for ij in interjections:
                _save_chat_entry({"type": "npc", "content": f"[interjects] {ij.dialogue}", "npc_name": ij.npc_name, "timestamp": int(time.time() * 1000)})
    except Exception:
        pass

    return DialogueResponse(
        npc_name=npc["name"],
        dialogue=result["dialogue"],
        mood=mood,
        interjections=interjections,
    )


# ── Look ─────────────────────────────────────────────────────────────────


@router.get("/look", response_model=LookResponse)
async def look():
    """Describe current location."""
    gq = _gq()

    location = await gq.get_player_location(PLAYER_ID)
    if not location:
        raise HTTPException(400, "Player has no location")

    npcs = await gq.get_npcs_at_location(location["id"])
    # Filter to alive only (safety net — query already filters, but double-check)
    npcs = [n for n in npcs if n.get("alive", True)]
    dead_npcs = await gq.get_dead_npcs_at_location(location["id"])
    exits = await gq.get_connected_locations(location["id"])

    return LookResponse(
        location=dict(location),
        npcs=[{"id": n["id"], "name": n["name"], "occupation": n["occupation"], "mood": n["mood"]} for n in npcs],
        items=[],  # TODO: items at location
        exits=[{"id": e["id"], "name": e["name"], "type": e["type"]} for e in exits],
        dead_npcs=[{"id": n["id"], "name": n["name"], "occupation": n.get("occupation", "")} for n in dead_npcs],
    )


# ── World State ──────────────────────────────────────────────────────────


@router.get("/world/state", response_model=WorldStateResponse)
async def world_state():
    gq = _gq()
    player = await gq.get_player(PLAYER_ID)
    location = await gq.get_player_location(PLAYER_ID)
    items = await gq.get_player_items(PLAYER_ID)

    return WorldStateResponse(
        day=await gq.get_world_day(),
        player_location=dict(location) if location else {},
        player_gold=player.get("gold", 0) if player else 0,
        player_inventory=[dict(i) for i in items],
        player_hp=player.get("current_hp", player.get("max_hp", 10)) if player else 10,
        player_max_hp=player.get("max_hp", 10) if player else 10,
        player_level=player.get("level", 1) if player else 1,
        player_class=player.get("class_id", "commoner") if player else "commoner",
        player_xp=player.get("xp", 0) if player else 0,
    )


@router.get("/world/log", response_model=WorldLogResponse)
async def world_log():
    return WorldLogResponse(entries=_world_log[-20:])


@router.get("/world/map", response_model=WorldMapResponse)
async def world_map():
    gq = _gq()
    map_data = await gq.get_world_map()
    player_loc = await gq.get_player_location(PLAYER_ID)

    # Get NPC locations
    all_npcs = await gq.get_all_npcs()
    npc_locs = {}
    for npc in all_npcs:
        loc = await gq.get_npc_location(npc["id"])
        if loc:
            npc_locs[npc["id"]] = loc["id"]

    return WorldMapResponse(
        locations=map_data["locations"],
        connections=map_data["connections"],
        player_location_id=player_loc["id"] if player_loc else "",
        npc_locations=npc_locs,
    )


# ── Inventory ────────────────────────────────────────────────────────────


@router.get("/inventory")
async def get_inventory():
    """Get player inventory."""
    gq = _gq()
    items = await gq.get_player_items(PLAYER_ID)
    player = await gq.get_player(PLAYER_ID)
    return {
        "items": [dict(i) for i in items],
        "gold": player.get("gold", 0) if player else 0,
    }


@router.post("/inventory/pickup/{item_id}")
async def pickup_item(item_id: str):
    """Pick up an item."""
    gq = _gq()
    await gq.give_item_to_player(item_id, PLAYER_ID)
    return {"status": "picked_up", "item_id": item_id}


@router.post("/inventory/drop/{item_id}")
async def drop_item(item_id: str):
    """Drop an item at current location."""
    gq = _gq()
    # Remove ownership
    async with gq._session() as s:
        await s.run(
            "MATCH (p:Player {id: $pid})-[r:OWNS]->(i:Item {id: $iid}) DELETE r",
            pid=PLAYER_ID, iid=item_id,
        )
    return {"status": "dropped", "item_id": item_id}


# ── NPC ──────────────────────────────────────────────────────────────────


@router.get("/npc/{npc_id}")
async def npc_info(npc_id: str):
    gq = _gq()
    npc = await gq.get_npc(npc_id)
    if not npc:
        raise HTTPException(404, "NPC not found")

    location = await gq.get_npc_location(npc_id)
    relationships = await gq.get_relationships(npc_id)
    init_memory_db()
    memories = get_recent_memories(npc_id, limit=10)

    return {
        "id": npc["id"],
        "name": npc["name"],
        "personality": npc.get("personality", ""),
        "backstory": npc.get("backstory", ""),
        "goals": npc.get("goals", []),
        "mood": npc["mood"],
        "occupation": npc["occupation"],
        "age": npc.get("age", 0),
        "alive": npc.get("alive", True),
        "current_hp": npc.get("current_hp"),
        "max_hp": npc.get("max_hp"),
        "gold": npc.get("gold", 0),
        "level": npc.get("level", 1),
        "current_activity": npc.get("current_activity"),
        "location": dict(location) if location else None,
        "relationships": [
            {"name": r["name"], "id": r["id"], "sentiment": round(r["sentiment"], 2), "reason": r["reason"]}
            for r in relationships
        ],
        "recent_memories": memories,
    }


@router.get("/npcs")
async def list_npcs():
    """List all NPCs with basic info."""
    gq = _gq()
    all_npcs = await gq.get_all_npcs()
    result = []
    for npc in all_npcs:
        loc = await gq.get_npc_location(npc["id"])
        result.append({
            "id": npc["id"],
            "name": npc["name"],
            "occupation": npc["occupation"],
            "mood": npc["mood"],
            "alive": npc.get("alive", True),
            "level": npc.get("level", 1),
            "current_hp": npc.get("current_hp"),
            "max_hp": npc.get("max_hp"),
            "gold": npc.get("gold", 0),
            "current_activity": npc.get("current_activity"),
            "location": loc["name"] if loc else None,
        })
    return {"npcs": result}


@router.get("/npc/{npc_id}/observe", response_model=NPCObserveResponse)
async def npc_observe(npc_id: str):
    """Observer mode: full NPC state (debug/demo)."""
    gq = _gq()
    npc = await gq.get_npc(npc_id)
    if not npc:
        raise HTTPException(404, "NPC not found")

    location = await gq.get_npc_location(npc_id)
    relationships = await gq.get_relationships(npc_id)
    init_memory_db()
    memories = get_recent_memories(npc_id, limit=10)

    # Parse evolution state if present
    evo_json = npc.get("evolution_state_json")
    fears = []
    active_goals = []
    nemesis_data = None
    evolution_log = []
    trait_scale = None
    archetype_affinity = {}
    relationship_tags = {}

    if evo_json:
        try:
            from app.models.evolution import NPCEvolutionState
            evo = NPCEvolutionState.model_validate_json(evo_json)
            fears = [f.model_dump() for f in evo.fears]
            active_goals = [g.model_dump() for g in evo.goals if g.status == "active"]
            nemesis_data = evo.nemesis.model_dump() if evo.nemesis else None
            evolution_log = [e.model_dump() for e in evo.evolution_log[-20:]]
            trait_scale = evo.traits.as_dict()
            archetype_affinity = evo.archetype_affinity
            relationship_tags = {
                k: [t.model_dump() for t in v] for k, v in evo.relationship_tags.items()
            }
        except Exception:
            pass

    # Compute AC from equipment
    ac_val = npc.get("ac")
    if ac_val is None:
        ac_val = 10 + (npc.get("level", 1) if not npc.get("armor_id") else 0)

    return NPCObserveResponse(
        id=npc["id"],
        name=npc["name"],
        personality=npc["personality"],
        backstory=npc["backstory"],
        goals=npc.get("goals", []),
        mood=npc["mood"],
        occupation=npc["occupation"],
        age=npc["age"],
        alive=npc.get("alive", True),
        location=dict(location) if location else None,
        relationships=relationships,
        recent_memories=memories,
        # D&D stats
        level=npc.get("level", 1),
        class_id=npc.get("class_id"),
        race=npc.get("race"),
        archetype=npc.get("archetype"),
        current_hp=npc.get("current_hp"),
        max_hp=npc.get("max_hp"),
        ac=ac_val,
        gold=npc.get("gold", 0),
        equipment_ids=npc.get("equipment_ids", []),
        known_spells=npc.get("known_spells", []),
        proficient_skills=npc.get("proficient_skills", []),
        conditions=npc.get("conditions", []),
        # Evolution
        fears=fears,
        active_goals=active_goals,
        nemesis=nemesis_data,
        evolution_log=evolution_log,
        trait_scale=trait_scale,
        archetype_affinity=archetype_affinity,
        relationship_tags=relationship_tags,
    )


# ── Control ──────────────────────────────────────────────────────────────


@router.post("/world/tick", response_model=TickResponse)
async def manual_tick():
    """Trigger a manual world tick."""
    result = await run_world_tick()
    _world_log.append(result)
    if len(_world_log) > 50:
        _world_log[:] = _world_log[-50:]
    _save_world_log()
    # Flatten evolution_logs into evolution_changes list
    evo_changes = []
    for npc_id, logs in result.get("evolution_logs", {}).items():
        for log in logs:
            evo_changes.append({"npc_id": npc_id, **log})
    result["evolution_changes"] = evo_changes
    return TickResponse(**result)


@router.post("/world/tick/stream")
async def stream_tick():
    """Stream tick progress via SSE."""
    async def event_generator():
        yield f"data: {_json.dumps({'phase': 'starting', 'message': 'Tick starting...'})}\n\n"

        try:
            result = await run_world_tick()
            _world_log.append(result)
            if len(_world_log) > 50:
                _world_log[:] = _world_log[-50:]
            _save_world_log()

            # Stream scenario info
            for sc in result.get("active_scenarios", []):
                yield f"data: {_json.dumps({'phase': 'scenario', 'data': sc})}\n\n"

            # Stream events
            for e in result.get("events", []):
                yield f"data: {_json.dumps({'phase': 'event', 'data': e})}\n\n"

            # Stream NPC actions summary
            actions = {}
            for a in result.get("npc_actions", []):
                actions[a["action"]] = actions.get(a["action"], 0) + 1
            yield f"data: {_json.dumps({'phase': 'actions', 'data': {'summary': actions, 'total': len(result.get('npc_actions', []))}})}\n\n"

            # Stream interactions
            for i in result.get("interactions", []):
                yield f"data: {_json.dumps({'phase': 'interaction', 'data': i})}\n\n"

            # Final result
            yield f"data: {_json.dumps({'phase': 'complete', 'data': result}, default=str)}\n\n"

        except Exception as e:
            yield f"data: {_json.dumps({'phase': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/npcs/graph")
async def npc_graph():
    """Get NPC relationship graph for visualization. Unknown NPCs are masked."""
    gq = _gq()
    all_npcs = await gq.get_all_npcs()

    # Track which NPCs the player has met (has REPUTATION_WITH or talked to)
    player_known: set[str] = set()
    try:
        for npc in all_npcs:
            rep = await gq.get_player_reputation(PLAYER_ID, npc["id"])
            if rep and rep != 0:
                player_known.add(npc["id"])
    except Exception:
        pass

    # Also mark NPCs at player's current location as known
    try:
        player_loc = await gq.get_player_location(PLAYER_ID)
        if player_loc:
            local_npcs = await gq.get_npcs_at_location(player_loc["id"])
            for n in local_npcs:
                player_known.add(n["id"])
    except Exception:
        pass

    nodes = []
    for npc in all_npcs:
        if not npc.get("alive", True):
            continue
        known = npc["id"] in player_known
        nodes.append({
            "id": npc["id"],
            "name": npc["name"],  # Always show name
            "occupation": npc["occupation"],  # Always show
            "mood": npc["mood"],  # Always show
            "level": npc.get("level", 1),
            "archetype": npc.get("archetype"),
            "known": known,
            "alive": npc.get("alive", True),
        })

    # Build name lookup
    name_map = {n["id"]: n["name"] for n in all_npcs}

    edges = []
    for npc in all_npcs:
        if not npc.get("alive", True):
            continue
        rels = await gq.get_relationships(npc["id"])
        for rel in rels:
            if npc["id"] < rel["id"]:
                both_known = npc["id"] in player_known and rel["id"] in player_known
                edges.append({
                    "from": npc["id"],
                    "to": rel["id"],
                    "from_name": name_map.get(npc["id"], npc["id"]),
                    "to_name": name_map.get(rel["id"], rel["id"]),
                    "sentiment": round(rel["sentiment"], 2),
                    "reason": rel.get("reason", ""),
                    "visible": True,
                })

    return {"nodes": nodes, "edges": edges}


@router.get("/quests")
async def list_quests(status: str | None = None):
    """List quests, optionally filtered by status."""
    gq = _gq()
    quests = await gq.get_quests(status=status)
    return {"quests": quests}


@router.post("/quests/{quest_id}/accept")
async def accept_quest(quest_id: str):
    gq = _gq()
    quests = await gq.get_quests()
    quest = next((q for q in quests if q["id"] == quest_id), None)
    if not quest:
        raise HTTPException(404, "Quest not found")
    if quest["status"] != "available":
        raise HTTPException(400, f"Quest is {quest['status']}, cannot accept")
    await gq.update_quest(quest_id, {"status": "active"})
    return {"status": "accepted", "quest": quest}


@router.post("/quests/{quest_id}/complete")
async def complete_quest(quest_id: str):
    gq = _gq()
    quests = await gq.get_quests()
    quest = next((q for q in quests if q["id"] == quest_id), None)
    if not quest:
        raise HTTPException(404, "Quest not found")
    if quest["status"] != "active":
        raise HTTPException(400, f"Quest is {quest['status']}, cannot complete")
    await gq.update_quest(quest_id, {"status": "completed"})
    # Award gold
    if quest.get("reward_gold", 0) > 0:
        player = await gq.get_player(PLAYER_ID)
        if player:
            new_gold = player.get("gold", 0) + quest["reward_gold"]
            await gq.update_npc(PLAYER_ID, {"gold": new_gold})  # players use same update
    # Award XP for quest completion
    await gq.add_player_xp(PLAYER_ID, 50)
    return {"status": "completed", "reward_gold": quest.get("reward_gold", 0)}


@router.post("/player/respawn")
async def respawn_player():
    """Respawn player at tavern with half HP."""
    gq = _gq()
    player = await gq.get_player(PLAYER_ID)
    if not player:
        raise HTTPException(404, "Player not found")

    max_hp = player.get("max_hp", 10)
    respawn_hp = max(1, max_hp // 2)

    # Reset to tavern
    await gq.set_player_location(PLAYER_ID, "loc-tavern")
    await gq.update_player(PLAYER_ID, {"current_hp": respawn_hp})

    # Lose 10% gold
    gold = player.get("gold", 0)
    gold_lost = max(0, gold // 10)
    if gold_lost > 0:
        await gq.update_player(PLAYER_ID, {"gold": gold - gold_lost})

    return {
        "status": "respawned",
        "location": "The Rusty Flagon",
        "hp": respawn_hp,
        "max_hp": max_hp,
        "gold_lost": gold_lost,
    }


@router.post("/character/create")
async def create_character_simple(req: dict = Body(...)):
    """Create or update player character."""
    gq = _gq()
    name = req.get("name", "Hero")
    race = req.get("race", "human")
    class_id = req.get("class_id", "fighter")

    # HP by class
    hp_map = {"fighter": 12, "rogue": 10, "wizard": 8, "cleric": 10, "ranger": 12}
    max_hp = hp_map.get(class_id, 10)

    player = await gq.get_player(PLAYER_ID)
    if player:
        await gq.update_player(PLAYER_ID, {
            "name": name,
            "race": race,
            "class_id": class_id,
            "level": 1,
            "max_hp": max_hp,
            "current_hp": max_hp,
        })

    return {"status": "created", "name": name, "race": race, "class_id": class_id, "hp": max_hp}


@router.post("/world/save")
async def save_world():
    """Save current world state."""
    import json
    from pathlib import Path

    gq = _gq()
    save_dir = settings.worlds_dir / "saves"
    save_dir.mkdir(exist_ok=True)

    world_day = await gq.get_world_day()
    all_npcs = await gq.get_all_npcs()
    locations = await gq.get_all_locations()
    scenarios = await gq.get_active_scenarios()
    quests = await gq.get_quests()
    player = await gq.get_player(PLAYER_ID)
    player_loc = await gq.get_player_location(PLAYER_ID)
    player_items = await gq.get_player_items(PLAYER_ID)

    # Gather NPC locations and relationships
    npc_data = []
    for npc in all_npcs:
        loc = await gq.get_npc_location(npc["id"])
        rels = await gq.get_relationships(npc["id"])
        npc_data.append({
            "npc": dict(npc),
            "location_id": loc["id"] if loc else None,
            "relationships": [dict(r) for r in rels],
        })

    save_data = {
        "version": 1,
        "world_day": world_day,
        "player": dict(player) if player else None,
        "player_location_id": player_loc["id"] if player_loc else None,
        "player_items": [dict(i) for i in player_items],
        "npcs": npc_data,
        "scenarios": scenarios,
        "quests": quests,
        "world_log": _world_log[-20:],
    }

    save_path = save_dir / f"save_day{world_day}.json"
    save_path.write_text(json.dumps(save_data, indent=2, default=str), encoding="utf-8")

    return {"status": "saved", "file": str(save_path), "day": world_day}


@router.get("/world/saves")
async def list_saves():
    """List available save files."""
    import json
    save_dir = settings.worlds_dir / "saves"
    if not save_dir.exists():
        return {"saves": []}
    saves = []
    for f in sorted(save_dir.glob("save_*.json"), reverse=True):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            saves.append({
                "file": f.name,
                "day": data.get("world_day", 0),
                "npcs": len(data.get("npcs", [])),
                "scenarios": len(data.get("scenarios", [])),
            })
        except Exception:
            pass
    return {"saves": saves}


@router.post("/world/load/{filename}")
async def load_save(filename: str):
    """Load a save file."""
    import json
    save_path = settings.worlds_dir / "saves" / filename
    if not save_path.exists():
        raise HTTPException(404, "Save not found")

    data = json.loads(save_path.read_text(encoding="utf-8"))
    gq = _gq()

    # Clear and restore
    await gq.clear_all()
    init_memory_db()
    clear_all_memories()

    # Restore world day
    async with gq._session() as s:
        await s.run("MERGE (w:World {id: 'main'}) SET w.day = $day", day=data["world_day"])

    # Restore player
    if data.get("player"):
        await gq.create_player(data["player"])
        if data.get("player_location_id"):
            # Need to restore locations first
            pass

    # Restore NPCs and locations would need full seed + override
    # For now, re-seed and override NPC states
    from app.graph.seed import seed_world
    await seed_world(gq._driver, settings.worlds_dir / "medieval_village")

    # Override NPC states from save
    for npc_entry in data.get("npcs", []):
        npc = npc_entry["npc"]
        try:
            await gq.update_npc(npc["id"], {
                "mood": npc.get("mood", "neutral"),
                "gold": npc.get("gold", 0),
                "current_hp": npc.get("current_hp", npc.get("max_hp", 10)),
                "alive": npc.get("alive", True),
                "current_activity": npc.get("current_activity"),
            })
            if npc_entry.get("location_id"):
                await gq.set_npc_location(npc["id"], npc_entry["location_id"])
            for rel in npc_entry.get("relationships", []):
                await gq.set_relationship(npc["id"], rel["id"], rel["sentiment"], rel.get("reason", ""))
        except Exception:
            pass

    # Restore scenarios
    for sc in data.get("scenarios", []):
        try:
            await gq.create_scenario(sc)
        except Exception:
            pass

    # Restore quests
    for q in data.get("quests", []):
        try:
            await gq.create_quest(q)
        except Exception:
            pass

    # Restore world log
    _world_log.clear()
    _world_log.extend(data.get("world_log", []))

    return {"status": "loaded", "day": data["world_day"]}


@router.post("/world/inter-session")
async def inter_session(days: int = 3):
    """Simulate inter-session events (what happened while player was away)."""
    from app.simulation.inter_session import process_inter_session
    gq = _gq()
    world_day = await gq.get_world_day()
    map_data = await gq.get_world_map()
    location_names = [loc["name"] for loc in map_data.get("locations", [])]

    result = await process_inter_session(gq, days, world_day, location_names)

    # Advance world day
    new_day = world_day + days
    async with gq._session() as s:
        await s.run("MERGE (w:World {id: 'main'}) SET w.day = $day", day=new_day)

    # Add events to world log
    for event in result["events"]:
        _world_log.append({
            "day": world_day + event["day_offset"],
            "events": [event],
            "npc_actions": [],
            "interactions": [],
            "active_scenarios": [],
        })
    if len(_world_log) > 50:
        _world_log[:] = _world_log[-50:]
    _save_world_log()

    return {
        "new_day": new_day,
        "days_simulated": result["days_simulated"],
        "events": result["events"],
        "npc_changes": result["npc_changes"],
    }


@router.post("/world/reset")
async def reset_world():
    """Reset the world to initial state."""
    world_dir = settings.worlds_dir / "medieval_village"
    driver = get_driver()
    await seed_world(driver, world_dir)
    init_memory_db()
    clear_all_memories()
    _world_log.clear()
    _save_world_log()
    # Clear chat log
    if CHAT_LOG_PATH.exists():
        CHAT_LOG_PATH.unlink()
    return {"status": "world_reset", "message": "The world has been restored to its initial state."}
