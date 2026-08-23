"""
Shared utility functions for NexusKnowledge backend
"""
from knowledge.db import neo4j_connection
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


@contextmanager
def neo4j_session():
    """Context manager for Neo4j session handling"""
    session = neo4j_connection.get_session()
    try:
        yield session
    finally:
        session.close()
