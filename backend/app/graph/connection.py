from neo4j import AsyncGraphDatabase, AsyncDriver

from app.config import settings
from app.utils.logger import get_logger

log = get_logger("neo4j")

_driver: AsyncDriver | None = None


def get_driver() -> AsyncDriver:
    global _driver
    if _driver is None:
        log.info("connecting_neo4j", uri=settings.neo4j_uri)
        _driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
    return _driver


async def close_driver() -> None:
    global _driver
    if _driver:
        await _driver.close()
        _driver = None
        log.info("neo4j_closed")
