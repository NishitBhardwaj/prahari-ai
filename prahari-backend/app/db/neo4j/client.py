"""
Neo4j AuraDB async client — connection pool and Cypher execution utilities.
"""

from typing import Any, Dict, List, Optional
from neo4j import AsyncGraphDatabase, AsyncDriver
from loguru import logger

from app.config import get_settings

settings = get_settings()

_driver: Optional[AsyncDriver] = None


async def init_neo4j():
    global _driver
    _driver = AsyncGraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
    )
    await _driver.verify_connectivity()
    logger.info(f"Neo4j AuraDB connected: {settings.NEO4J_URI}")


async def close_neo4j():
    global _driver
    if _driver:
        await _driver.close()
        logger.info("Neo4j connection closed.")


def get_neo4j_driver() -> AsyncDriver:
    if not _driver:
        raise RuntimeError("Neo4j driver not initialized. Call init_neo4j() first.")
    return _driver


async def execute_query(
    cypher: str,
    parameters: Optional[Dict[str, Any]] = None,
    database: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Execute a Cypher query and return records as list of dicts."""
    driver = get_neo4j_driver()
    db = database or settings.NEO4J_DATABASE

    async with driver.session(database=db) as session:
        result = await session.run(cypher, parameters or {})
        records = await result.data()
        return records


async def execute_write(
    cypher: str,
    parameters: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Execute a write Cypher transaction."""
    driver = get_neo4j_driver()

    async with driver.session(database=settings.NEO4J_DATABASE) as session:
        result = await session.execute_write(
            lambda tx: tx.run(cypher, parameters or {})
        )
        return result
