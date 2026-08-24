"""
Neo4j Database Connection Manager
Handles connection to CognoDB using Neo4j driver
"""
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Neo4jConnection:
    """Singleton Neo4j connection manager"""
    
    _instance = None
    _driver = None
    _connection_attempts = 0
    _max_attempts = 3
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Neo4jConnection, cls).__new__(cls)
        return cls._instance
    
    def connect(self):
        """Establish connection to Neo4j/CognoDB"""
        if self._driver is None:
            driver = None
            try:
                uri = settings.NEO4J_URI
                user = settings.NEO4J_USER
                password = settings.NEO4J_PASSWORD
                
                if not uri:
                    raise ValueError("NEO4J_URI is not configured. Please check your settings.")
                if not user:
                    raise ValueError("NEO4J_USER is not configured. Please check your settings.")
                if not password:
                    raise ValueError("NEO4J_PASSWORD is not configured. Please check your settings.")
                
                driver = GraphDatabase.driver(uri, auth=(user, password))
                driver.verify_connectivity()
                self._driver = driver
                self._connection_attempts = 0
                logger.info("Successfully connected to CognoDB")
            except AuthError as e:
                if driver:
                    driver.close()
                logger.error(f"Authentication failed: {e}")
                raise ConnectionError("Invalid CognoDB credentials. Please check NEO4J_USER and NEO4J_PASSWORD.")
            except ServiceUnavailable as e:
                if driver:
                    driver.close()
                self._connection_attempts += 1
                if self._connection_attempts < self._max_attempts:
                    logger.warning(f"Connection attempt {self._connection_attempts} failed, retrying...")
                    return self.connect()
                logger.error(f"Failed to connect to CognoDB after {self._max_attempts} attempts: {e}")
                raise ConnectionError("Unable to connect to CognoDB. Please check NEO4J_URI and network connectivity.")
            except Exception as e:
                if driver:
                    driver.close()
                logger.error(f"Unexpected error connecting to CognoDB: {e}")
                raise ConnectionError(f"Connection error: {str(e)}")
        return self._driver
    
    def close(self):
        """Close the Neo4j connection"""
        if self._driver is not None:
            try:
                self._driver.close()
                self._driver = None
                logger.info("Closed CognoDB connection")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
    
    def get_session(self):
        """Get a Neo4j session"""
        try:
            driver = self.connect()
            return driver.session()
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    def execute_query(self, query, parameters=None):
        """Execute a Cypher query with parameters"""
        session = None
        try:
            session = self.get_session()
            result = session.run(query, parameters or {})
            return [record for record in result]
        except ServiceUnavailable as e:
            logger.error(f"Service unavailable during query execution: {e}")
            raise ConnectionError("Database service unavailable. Please check your connection.")
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
        finally:
            if session:
                try:
                    session.close()
                except Exception as e:
                    logger.error(f"Error closing session: {e}")


neo4j_connection = Neo4jConnection()