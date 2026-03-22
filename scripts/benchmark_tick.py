"""Benchmark world tick performance."""

import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.simulation.ticker import run_world_tick


async def main():
    iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    times = []

    print(f"Running {iterations} world ticks...")

    for i in range(iterations):
        start = time.perf_counter()
        result = await run_world_tick()
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        print(f"  Tick {i + 1}: {elapsed:.2f}s — "
              f"{len(result['events'])} events, "
              f"{len(result['npc_actions'])} actions, "
              f"{len(result['interactions'])} interactions")

    avg = sum(times) / len(times)
    print(f"\nAverage: {avg:.2f}s per tick")
    print(f"Min: {min(times):.2f}s, Max: {max(times):.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
