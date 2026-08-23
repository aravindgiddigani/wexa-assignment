"""
Knowledge Graph Data Model
Defines the structure of nodes and relationships for the knowledge graph
"""

# Graph Data Model:
# 
# Nodes:
# - Topic: Represents a concept, idea, or subject
#   Properties: name, description, category, importance, created_at
# - User: Represents application users
#   Properties: id, email, first_name, last_name, phone_number, password, password_salt, is_active, is_staff, is_superuser, created_at, updated_at
# - Token: Represents authentication tokens
#   Properties: key, created_at
#
# Relationships:
# - RELATED_TO: General connection between topics
# - BUILDS_ON: Prerequisite relationship (A builds on B)
# - CONTRADICTS: Opposing concepts
# - PART_OF: Hierarchical relationship (A is part of B)
# - APPLIES_TO: Application relationship (A applies to B)
# - HAS_TOKEN: User-token relationship (User)-[:HAS_TOKEN]->(Token)
#
# Example Use Cases:
# - Find topics that build on a given concept
# - Discover contradictions in knowledge
# - Trace hierarchical relationships
# - Find related topics through multi-hop traversals
# - Explore applications of concepts

class RelationshipType:
    """Types of relationships between topics"""
    RELATED_TO = "RELATED_TO"
    BUILDS_ON = "BUILDS_ON"
    CONTRADICTS = "CONTRADICTS"
    PART_OF = "PART_OF"
    APPLIES_TO = "APPLIES_TO"
    
    @classmethod
    def all_types(cls):
        return [cls.RELATED_TO, cls.BUILDS_ON, cls.CONTRADICTS, 
                cls.PART_OF, cls.APPLIES_TO]