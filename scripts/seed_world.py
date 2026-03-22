"""Script to seed the world from a preset into Neo4j."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.config import settings
from app.graph.connection import get_driver, close_driver
from app.graph.schema import ensure_schema
from app.graph.seed import seed_world
from app.models.memory import init_memory_db


async def main():
    world_name = sys.argv[1] if len(sys.argv) > 1 else "medieval_village"
    world_dir = settings.worlds_dir / world_name

    if not world_dir.exists():
        print(f"World preset not found: {world_dir}")
        sys.exit(1)

    print(f"Seeding world: {world_name}")

    driver = get_driver()
    await ensure_schema(driver)
    await seed_world(driver, world_dir)
    init_memory_db()

    print("World seeded successfully!")
    await close_driver()


if __name__ == "__main__":
    asyncio.run(main())
