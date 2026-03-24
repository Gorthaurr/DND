"""Neo4j CRUD operations for the world graph."""

from neo4j import AsyncDriver, AsyncSession

from app.utils.logger import get_logger

log = get_logger("queries")


class GraphQueries:
    """Centralized Neo4j query executor."""

    def __init__(self, driver: AsyncDriver):
        self._driver = driver

    def _session(self) -> AsyncSession:
        return self._driver.session()

    # ── NPC ──────────────────────────────────────────────────────────────

    async def create_npc(self, npc: dict) -> None:
        # Extract optional fields with defaults so Cypher always gets them
        max_hp = npc.get("max_hp", 10)
        params = {
            "id": npc["id"],
            "name": npc["name"],
            "personality": npc.get("personality", ""),
            "backstory": npc.get("backstory", ""),
            "goals": npc.get("goals", []),
            "mood": npc.get("mood", "neutral"),
            "occupation": npc.get("occupation", ""),
            "age": npc.get("age", 30),
            "archetype": npc.get("archetype"),
            "current_activity": npc.get("current_activity"),
            "alive": npc.get("alive", True),
            # D&D stats
            "level": npc.get("level", 1),
            "class_id": npc.get("class_id"),
            "race": npc.get("race"),
            "max_hp": max_hp,
            "current_hp": npc.get("current_hp", max_hp),
            "ac": npc.get("ac", 10),
            "gold": npc.get("gold", 0),
            "equipment_ids": npc.get("equipment_ids", []),
            "known_spells": npc.get("known_spells", []),
            "proficient_skills": npc.get("proficient_skills", []),
            "expertise_skills": npc.get("expertise_skills", []),
            "saving_throw_proficiencies": npc.get("saving_throw_proficiencies", []),
        }
        async with self._session() as s:
            await s.run(
                """
                MERGE (n:NPC {id: $id})
                SET n.name = $name,
                    n.personality = $personality,
                    n.backstory = $backstory,
                    n.goals = $goals,
                    n.mood = $mood,
                    n.occupation = $occupation,
                    n.age = $age,
                    n.alive = $alive,
                    n.archetype = $archetype,
                    n.current_activity = $current_activity,
                    n.level = $level,
                    n.class_id = $class_id,
                    n.race = $race,
                    n.max_hp = $max_hp,
                    n.current_hp = $current_hp,
                    n.ac = $ac,
                    n.gold = $gold,
                    n.equipment_ids = $equipment_ids,
                    n.known_spells = $known_spells,
                    n.proficient_skills = $proficient_skills,
                    n.expertise_skills = $expertise_skills,
                    n.saving_throw_proficiencies = $saving_throw_proficiencies
                """,
                **params,
            )

    async def get_npc(self, npc_id: str) -> dict | None:
        async with self._session() as s:
            result = await s.run("MATCH (n:NPC {id: $id}) RETURN n", id=npc_id)
            record = await result.single()
            return dict(record["n"]) if record else None

    async def get_all_npcs(self) -> list[dict]:
        async with self._session() as s:
            result = await s.run("MATCH (n:NPC {alive: true}) RETURN n")
            return [dict(r["n"]) async for r in result]

    async def update_npc(self, npc_id: str, updates: dict) -> None:
        set_clause = ", ".join(f"n.{k} = ${k}" for k in updates)
        async with self._session() as s:
            await s.run(f"MATCH (n:NPC {{id: $id}}) SET {set_clause}", id=npc_id, **updates)

    async def kill_npc(self, npc_id: str) -> None:
        """Mark NPC as dead."""
        async with self._session() as s:
            await s.run(
                "MATCH (n:NPC {id: $id}) SET n.alive = false, n.mood = 'dead', n.current_hp = 0",
                id=npc_id,
            )

    async def damage_npc(self, npc_id: str, damage: int) -> dict | None:
        """Deal damage to NPC. Returns updated NPC or None. Kills if HP <= 0."""
        async with self._session() as s:
            result = await s.run(
                """
                MATCH (n:NPC {id: $id})
                SET n.current_hp = CASE
                    WHEN n.current_hp - $dmg <= 0 THEN 0
                    ELSE n.current_hp - $dmg
                END,
                n.alive = CASE
                    WHEN n.current_hp - $dmg <= 0 THEN false
                    ELSE n.alive
                END,
                n.mood = CASE
                    WHEN n.current_hp - $dmg <= 0 THEN 'dead'
                    ELSE n.mood
                END
                RETURN n
                """,
                id=npc_id, dmg=damage,
            )
            record = await result.single()
            return dict(record["n"]) if record else None

    async def heal_npc(self, npc_id: str, amount: int) -> None:
        """Heal NPC up to max_hp."""
        async with self._session() as s:
            await s.run(
                """
                MATCH (n:NPC {id: $id})
                SET n.current_hp = CASE
                    WHEN n.current_hp + $amt > n.max_hp THEN n.max_hp
                    ELSE n.current_hp + $amt
                END
                """,
                id=npc_id, amt=amount,
            )

    async def transfer_gold(self, from_id: str, to_id: str, amount: int) -> bool:
        """Transfer gold between NPCs. Returns False if insufficient funds."""
        async with self._session() as s:
            result = await s.run(
                "MATCH (n:NPC {id: $id}) RETURN n.gold as gold",
                id=from_id,
            )
            rec = await result.single()
            if not rec or (rec["gold"] or 0) < amount:
                return False
            await s.run(
                "MATCH (n:NPC {id: $from}) SET n.gold = n.gold - $amt",
                **{"from": from_id}, amt=amount,
            )
            await s.run(
                "MATCH (n:NPC {id: $to}) SET n.gold = n.gold + $amt",
                to=to_id, amt=amount,
            )
            return True

    # ── Location ─────────────────────────────────────────────────────────

    async def create_location(self, loc: dict) -> None:
        async with self._session() as s:
            await s.run(
                """
                MERGE (l:Location {id: $id})
                SET l.name = $name, l.type = $type, l.description = $description
                """,
                **loc,
            )

    async def connect_locations(self, loc_a_id: str, loc_b_id: str, distance: int = 1) -> None:
        async with self._session() as s:
            await s.run(
                """
                MATCH (a:Location {id: $a}), (b:Location {id: $b})
                MERGE (a)-[:CONNECTED_TO {distance: $d}]->(b)
                MERGE (b)-[:CONNECTED_TO {distance: $d}]->(a)
                """,
                a=loc_a_id, b=loc_b_id, d=distance,
            )

    async def get_all_locations(self) -> list[dict]:
        async with self._session() as s:
            result = await s.run("MATCH (l:Location) RETURN l")
            return [dict(r["l"]) async for r in result]

    async def get_connected_locations(self, loc_id: str) -> list[dict]:
        async with self._session() as s:
            result = await s.run(
                """
                MATCH (l:Location {id: $id})-[:CONNECTED_TO]->(c:Location)
                RETURN c
                """,
                id=loc_id,
            )
            return [dict(r["c"]) async for r in result]

    # ── NPC Location ─────────────────────────────────────────────────────

    async def set_npc_location(self, npc_id: str, loc_id: str) -> None:
        async with self._session() as s:
            await s.run(
                """
                MATCH (n:NPC {id: $npc}), (l:Location {id: $loc})
                OPTIONAL MATCH (n)-[r:LOCATED_IN]->()
                DELETE r
                MERGE (n)-[:LOCATED_IN]->(l)
                """,
                npc=npc_id, loc=loc_id,
            )

    async def get_npcs_at_location(self, loc_id: str) -> list[dict]:
        async with self._session() as s:
            result = await s.run(
                """
                MATCH (n:NPC {alive: true})-[:LOCATED_IN]->(l:Location {id: $id})
                RETURN n
                """,
                id=loc_id,
            )
            return [dict(r["n"]) async for r in result]

    async def get_dead_npcs_at_location(self, loc_id: str) -> list[dict]:
        async with self._session() as s:
            result = await s.run(
                """
                MATCH (n:NPC {alive: false})-[:LOCATED_IN]->(l:Location {id: $id})
                RETURN n
                """,
                id=loc_id,
            )
            return [dict(r["n"]) async for r in result]

    async def get_npc_location(self, npc_id: str) -> dict | None:
        async with self._session() as s:
            result = await s.run(
                "MATCH (n:NPC {id: $id})-[:LOCATED_IN]->(l:Location) RETURN l",
                id=npc_id,
            )
            record = await result.single()
            return dict(record["l"]) if record else None

    # ── Relationships ────────────────────────────────────────────────────

    async def set_relationship(self, from_id: str, to_id: str, sentiment: float, reason: str) -> None:
        async with self._session() as s:
            await s.run(
                """
                MATCH (a:NPC {id: $a}), (b:NPC {id: $b})
                MERGE (a)-[r:FEELS]->(b)
                SET r.sentiment = $s, r.reason = $reason
                """,
                a=from_id, b=to_id, s=sentiment, reason=reason,
            )

    async def get_relationships(self, npc_id: str) -> list[dict]:
        async with self._session() as s:
            result = await s.run(
                """
                MATCH (n:NPC {id: $id})-[r:FEELS]->(other:NPC)
                RETURN other.name AS name, other.id AS id, r.sentiment AS sentiment, r.reason AS reason
                """,
                id=npc_id,
            )
            return [dict(r) async for r in result]

    async def set_relationship_tags(self, from_id: str, to_id: str, tags_json: str) -> None:
        """Store relationship tags JSON on the FEELS edge."""
        async with self._session() as s:
            await s.run(
                """
                MATCH (a:NPC {id: $a})-[r:FEELS]->(b:NPC {id: $b})
                SET r.tags_json = $tags
                """,
                a=from_id, b=to_id, tags=tags_json,
            )

    async def get_relationship_tags(self, from_id: str, to_id: str) -> str | None:
        """Get relationship tags JSON from FEELS edge."""
        async with self._session() as s:
            result = await s.run(
                """
                MATCH (a:NPC {id: $a})-[r:FEELS]->(b:NPC {id: $b})
                RETURN r.tags_json AS tags
                """,
                a=from_id, b=to_id,
            )
            record = await result.single()
            return record["tags"] if record else None

    async def set_knows(self, from_id: str, to_id: str, since_day: int, context: str) -> None:
        async with self._session() as s:
            await s.run(
                """
                MATCH (a:NPC {id: $a}), (b:NPC {id: $b})
                MERGE (a)-[r:KNOWS]->(b)
                SET r.since_day = $day, r.context = $ctx
                """,
                a=from_id, b=to_id, day=since_day, ctx=context,
            )

    # ── Items ────────────────────────────────────────────────────────────

    async def create_item(self, item: dict) -> None:
        async with self._session() as s:
            await s.run(
                """
                MERGE (i:Item {id: $id})
                SET i.name = $name, i.type = $type,
                    i.description = $description, i.value = $value
                """,
                **item,
            )

    async def give_item_to_npc(self, item_id: str, npc_id: str) -> None:
        async with self._session() as s:
            await s.run(
                """
                MATCH (i:Item {id: $item}), (n:NPC {id: $npc})
                OPTIONAL MATCH (i)<-[r:OWNS]-()
                DELETE r
                MERGE (n)-[:OWNS]->(i)
                """,
                item=item_id, npc=npc_id,
            )

    # ── Factions ──────────────────────────────────────────────────────────

    async def create_faction(self, faction: dict) -> None:
        async with self._session() as s:
            await s.run(
                """
                MERGE (f:Faction {id: $id})
                SET f.name = $name, f.description = $description, f.goals = $goals
                """,
                **faction,
            )

    async def set_faction_member(self, npc_id: str, faction_id: str, role: str) -> None:
        async with self._session() as s:
            await s.run(
                """
                MATCH (n:NPC {id: $npc}), (f:Faction {id: $fac})
                MERGE (n)-[r:MEMBER_OF]->(f)
                SET r.role = $role
                """,
                npc=npc_id, fac=faction_id, role=role,
            )

    # ── Player ───────────────────────────────────────────────────────────

    async def create_player(self, player: dict) -> None:
        async with self._session() as s:
            await s.run(
                """
                MERGE (p:Player {id: $id})
                SET p.name = $name, p.reputation = $reputation, p.gold = $gold
                """,
                **player,
            )

    async def get_player(self, player_id: str) -> dict | None:
        async with self._session() as s:
            result = await s.run("MATCH (p:Player {id: $id}) RETURN p", id=player_id)
            record = await result.single()
            return dict(record["p"]) if record else None

    async def set_player_location(self, player_id: str, loc_id: str) -> None:
        async with self._session() as s:
            await s.run(
                """
                MATCH (p:Player {id: $id}), (l:Location {id: $loc})
                OPTIONAL MATCH (p)-[r:LOCATED_IN]->()
                DELETE r
                MERGE (p)-[:LOCATED_IN]->(l)
                """,
                id=player_id, loc=loc_id,
            )

    async def get_player_location(self, player_id: str) -> dict | None:
        async with self._session() as s:
            result = await s.run(
                "MATCH (p:Player {id: $id})-[:LOCATED_IN]->(l:Location) RETURN l",
                id=player_id,
            )
            record = await result.single()
            return dict(record["l"]) if record else None

    async def set_player_reputation(self, player_id: str, npc_id: str, value: int) -> None:
        async with self._session() as s:
            await s.run(
                """
                MATCH (p:Player {id: $pid}), (n:NPC {id: $nid})
                MERGE (p)-[r:REPUTATION_WITH]->(n)
                SET r.value = $val
                """,
                pid=player_id, nid=npc_id, val=value,
            )

    async def get_player_reputation(self, player_id: str, npc_id: str) -> int:
        async with self._session() as s:
            result = await s.run(
                """
                MATCH (p:Player {id: $pid})-[r:REPUTATION_WITH]->(n:NPC {id: $nid})
                RETURN r.value AS value
                """,
                pid=player_id, nid=npc_id,
            )
            record = await result.single()
            return record["value"] if record else 0

    async def give_item_to_player(self, item_id: str, player_id: str) -> None:
        async with self._session() as s:
            await s.run(
                """
                MATCH (i:Item {id: $item}), (p:Player {id: $pid})
                OPTIONAL MATCH (i)<-[r:OWNS]-()
                DELETE r
                MERGE (p)-[:OWNS]->(i)
                """,
                item=item_id, pid=player_id,
            )

    async def get_player_items(self, player_id: str) -> list[dict]:
        async with self._session() as s:
            result = await s.run(
                "MATCH (p:Player {id: $id})-[:OWNS]->(i:Item) RETURN i",
                id=player_id,
            )
            return [dict(r["i"]) async for r in result]

    async def update_player(self, player_id: str, updates: dict) -> None:
        set_clause = ", ".join(f"p.{k} = ${k}" for k in updates)
        async with self._session() as s:
            await s.run(f"MATCH (p:Player {{id: $id}}) SET {set_clause}", id=player_id, **updates)

    # ── World Events ─────────────────────────────────────────────────────

    async def create_world_event(self, event: dict) -> None:
        async with self._session() as s:
            await s.run(
                """
                CREATE (e:WorldEvent {
                    id: $id, day: $day, description: $description, type: $type
                })
                """,
                **event,
            )

    async def link_event_to_npc(self, event_id: str, npc_id: str) -> None:
        async with self._session() as s:
            await s.run(
                """
                MATCH (e:WorldEvent {id: $eid}), (n:NPC {id: $nid})
                MERGE (e)-[:INVOLVES]->(n)
                """,
                eid=event_id, nid=npc_id,
            )

    async def link_event_to_location(self, event_id: str, loc_id: str) -> None:
        async with self._session() as s:
            await s.run(
                """
                MATCH (e:WorldEvent {id: $eid}), (l:Location {id: $lid})
                MERGE (e)-[:OCCURRED_AT]->(l)
                """,
                eid=event_id, lid=loc_id,
            )

    async def get_recent_events(self, since_day: int, limit: int = 10) -> list[dict]:
        async with self._session() as s:
            result = await s.run(
                """
                MATCH (e:WorldEvent)
                WHERE e.day >= $day
                RETURN e ORDER BY e.day DESC LIMIT $limit
                """,
                day=since_day, limit=limit,
            )
            return [dict(r["e"]) async for r in result]

    # ── World Map ────────────────────────────────────────────────────────

    async def get_world_map(self) -> dict:
        """Return locations and connections for map visualization."""
        async with self._session() as s:
            loc_result = await s.run("MATCH (l:Location) RETURN l")
            locations = [dict(r["l"]) async for r in loc_result]

            conn_result = await s.run(
                """
                MATCH (a:Location)-[r:CONNECTED_TO]->(b:Location)
                RETURN a.id AS from_id, b.id AS to_id, r.distance AS distance
                """
            )
            connections = [dict(r) async for r in conn_result]

        return {"locations": locations, "connections": connections}

    # ── Scenarios ─────────────────────────────────────────────────────────

    async def create_scenario(self, data: dict) -> None:
        import json
        async with self._session() as s:
            await s.run(
                """
                MERGE (sc:Scenario {id: $id})
                SET sc.title = $title,
                    sc.description = $description,
                    sc.scenario_type = $scenario_type,
                    sc.start_day = $start_day,
                    sc.current_phase_index = $current_phase_index,
                    sc.phases_json = $phases_json,
                    sc.involved_npc_ids = $involved_npc_ids,
                    sc.active = true,
                    sc.tension_level = $tension_level
                """,
                id=data["id"],
                title=data["title"],
                description=data["description"],
                scenario_type=data.get("scenario_type", "main"),
                start_day=data.get("start_day", 1),
                current_phase_index=data.get("current_phase_index", 0),
                phases_json=json.dumps(data.get("phases", [])),
                involved_npc_ids=data.get("involved_npc_ids", []),
                tension_level=data.get("tension_level", "low"),
            )
        # Link to involved NPCs
        for npc_id in data.get("involved_npc_ids", []):
            await self.link_scenario_to_npc(data["id"], npc_id)

    async def get_active_scenarios(self) -> list[dict]:
        import json
        async with self._session() as s:
            result = await s.run("MATCH (sc:Scenario {active: true}) RETURN sc")
            rows = [dict(r["sc"]) async for r in result]
        for row in rows:
            row["phases"] = json.loads(row.pop("phases_json", "[]"))
        return rows

    async def update_scenario(self, scenario_id: str, updates: dict) -> None:
        import json
        if "phases" in updates:
            updates["phases_json"] = json.dumps(updates.pop("phases"))
        set_clause = ", ".join(f"sc.{k} = ${k}" for k in updates)
        async with self._session() as s:
            await s.run(
                f"MATCH (sc:Scenario {{id: $id}}) SET {set_clause}",
                id=scenario_id,
                **updates,
            )

    async def deactivate_scenario(self, scenario_id: str) -> None:
        async with self._session() as s:
            await s.run(
                "MATCH (sc:Scenario {id: $id}) SET sc.active = false",
                id=scenario_id,
            )

    async def link_scenario_to_npc(self, scenario_id: str, npc_id: str) -> None:
        async with self._session() as s:
            await s.run(
                """
                MATCH (sc:Scenario {id: $sid}), (n:NPC {id: $nid})
                MERGE (sc)-[:INVOLVES]->(n)
                """,
                sid=scenario_id,
                nid=npc_id,
            )

    # ── World State ──────────────────────────────────────────────────────

    async def get_world_day(self) -> int:
        async with self._session() as s:
            result = await s.run("MERGE (w:World {id: 'main'}) ON CREATE SET w.day = 0 RETURN w.day AS day")
            record = await result.single()
            return record["day"] if record else 0

    async def increment_world_day(self) -> int:
        async with self._session() as s:
            result = await s.run(
                "MERGE (w:World {id: 'main'}) ON CREATE SET w.day = 0 SET w.day = w.day + 1 RETURN w.day AS day"
            )
            record = await result.single()
            return record["day"] if record else 1

    # ── Quests ──────────────────────────────────────────────────────────

    async def create_quest(self, data: dict) -> None:
        import json
        async with self._session() as s:
            await s.run(
                """
                MERGE (q:Quest {id: $id})
                SET q.title = $title,
                    q.description = $description,
                    q.giver_npc_id = $giver_npc_id,
                    q.giver_npc_name = $giver_npc_name,
                    q.objectives_json = $objectives_json,
                    q.reward_gold = $reward_gold,
                    q.reward_description = $reward_description,
                    q.difficulty = $difficulty,
                    q.status = $status,
                    q.scenario_id = $scenario_id
                """,
                id=data["id"],
                title=data["title"],
                description=data.get("description", ""),
                giver_npc_id=data.get("giver_npc_id"),
                giver_npc_name=data.get("giver_npc_name"),
                objectives_json=json.dumps(data.get("objectives", [])),
                reward_gold=data.get("reward_gold", 0),
                reward_description=data.get("reward_description", ""),
                difficulty=data.get("difficulty", "medium"),
                status=data.get("status", "available"),
                scenario_id=data.get("scenario_id"),
            )

    async def get_quests(self, status: str | None = None) -> list[dict]:
        import json
        query = "MATCH (q:Quest) "
        if status:
            query += "WHERE q.status = $status "
        query += "RETURN q"
        async with self._session() as s:
            result = await s.run(query, status=status)
            rows = [dict(r["q"]) async for r in result]
        for row in rows:
            row["objectives"] = json.loads(row.pop("objectives_json", "[]"))
        return rows

    async def update_quest(self, quest_id: str, updates: dict) -> None:
        import json
        if "objectives" in updates:
            updates["objectives_json"] = json.dumps(updates.pop("objectives"))
        set_clause = ", ".join(f"q.{k} = ${k}" for k in updates)
        async with self._session() as s:
            await s.run(
                f"MATCH (q:Quest {{id: $id}}) SET {set_clause}",
                id=quest_id,
                **updates,
            )

    # ── XP / Leveling ─────────────────────────────────────────────────────

    async def add_player_xp(self, player_id: str, xp: int) -> dict:
        """Add XP and check for level up. Returns updated player stats."""
        async with self._session() as s:
            # First, ensure xp field exists
            result = await s.run(
                """
                MATCH (p:Player {id: $id})
                SET p.xp = COALESCE(p.xp, 0) + $xp
                RETURN p.xp AS xp, p.level AS level, p.max_hp AS max_hp, p.current_hp AS current_hp
                """,
                id=player_id, xp=xp,
            )
            rec = await result.single()
            if not rec:
                return {}

            current_xp = rec["xp"] or 0
            current_level = rec["level"] or 1

            # XP thresholds: level 2=100, 3=300, 4=600, 5=1000, etc
            xp_for_next = current_level * current_level * 100

            if current_xp >= xp_for_next:
                new_level = current_level + 1
                new_max_hp = (rec["max_hp"] or 10) + 5 + (new_level // 2)
                await s.run(
                    """
                    MATCH (p:Player {id: $id})
                    SET p.level = $level,
                        p.max_hp = $max_hp,
                        p.current_hp = $max_hp
                    """,
                    id=player_id, level=new_level, max_hp=new_max_hp,
                )
                return {"leveled_up": True, "new_level": new_level, "new_max_hp": new_max_hp, "xp": current_xp}

            return {"leveled_up": False, "level": current_level, "xp": current_xp, "xp_needed": xp_for_next}

    # ── Utility ──────────────────────────────────────────────────────────

    async def clear_all(self) -> None:
        """Delete everything in the database. Use for reset."""
        async with self._session() as s:
            await s.run("MATCH (n) DETACH DELETE n")
        log.warning("database_cleared")
