from neo4j import AsyncDriver

from app.utils.logger import get_logger

log = get_logger("schema")

CONSTRAINTS = [
    "CREATE CONSTRAINT npc_id IF NOT EXISTS FOR (n:NPC) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT location_id IF NOT EXISTS FOR (l:Location) REQUIRE l.id IS UNIQUE",
    "CREATE CONSTRAINT item_id IF NOT EXISTS FOR (i:Item) REQUIRE i.id IS UNIQUE",
    "CREATE CONSTRAINT faction_id IF NOT EXISTS FOR (f:Faction) REQUIRE f.id IS UNIQUE",
    "CREATE CONSTRAINT player_id IF NOT EXISTS FOR (p:Player) REQUIRE p.id IS UNIQUE",
    "CREATE CONSTRAINT event_id IF NOT EXISTS FOR (e:WorldEvent) REQUIRE e.id IS UNIQUE",
    "CREATE CONSTRAINT scenario_id IF NOT EXISTS FOR (s:Scenario) REQUIRE s.id IS UNIQUE",
    "CREATE CONSTRAINT quest_id IF NOT EXISTS FOR (q:Quest) REQUIRE q.id IS UNIQUE",
]

INDEXES = [
    "CREATE INDEX npc_name IF NOT EXISTS FOR (n:NPC) ON (n.name)",
    "CREATE INDEX location_name IF NOT EXISTS FOR (l:Location) ON (l.name)",
    "CREATE INDEX event_day IF NOT EXISTS FOR (e:WorldEvent) ON (e.day)",
]


async def ensure_schema(driver: AsyncDriver) -> None:
    """Create constraints and indexes in Neo4j."""
    async with driver.session() as session:
        for stmt in CONSTRAINTS + INDEXES:
            try:
                await session.run(stmt)
            except Exception as e:
                log.warning("schema_statement_failed", stmt=stmt, error=str(e))
    log.info("schema_ensured")
