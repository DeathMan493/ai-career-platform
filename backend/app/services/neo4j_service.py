from __future__ import annotations

from contextlib import contextmanager

from neo4j import GraphDatabase

from app.core.config import settings


def get_neo4j_driver():
    return GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password),
    )


@contextmanager
def neo4j_session():
    driver = get_neo4j_driver()
    try:
        with driver.session() as session:
            yield session
    finally:
        driver.close()
