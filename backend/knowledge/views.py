"""
Django REST Framework Views for Knowledge Graph
Provides API endpoints for querying the knowledge graph
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from backend.utils import neo4j_session
from users.authentication import CognoDBTokenAuthentication
import logging

logger = logging.getLogger(__name__)

RELATIONSHIP_TYPES = ('BUILDS_ON', 'RELATED_TO', 'PART_OF', 'APPLIES_TO', 'CONTRADICTS')
TOPIC_LIST_QUERY = """
    MATCH (t:Topic)
    RETURN t.name as name, t.description as description,
           t.category as category, t.importance as importance
    ORDER BY t.name
"""
TOPIC_DETAIL_QUERY = """
    MATCH (t:Topic {name: $name})
    RETURN t.name as name, t.description as description,
           t.category as category, t.importance as importance,
           t.article_content as article_content,
           t.real_world_examples as real_world_examples,
           t.resource_links as resource_links,
           t.topic_image as topic_image,
           t.code_image as code_image,
           t.graph_image as graph_image,
           t.code_language as code_language,
           t.code_snippet as code_snippet,
           t.cypher_example as cypher_example
"""
TOPIC_SEARCH_QUERY = """
    MATCH (t:Topic)
    WHERE t.name CONTAINS $term OR t.description CONTAINS $term
    RETURN t.name as name, t.description as description,
           t.category as category, t.importance as importance
    ORDER BY t.name
"""
TOPIC_CATEGORY_QUERY = """
    MATCH (t:Topic {category: $category})
    RETURN t.name as name, t.description as description,
           t.category as category, t.importance as importance
    ORDER BY t.importance DESC, t.name
"""
HOP_QUERIES = {
    1: """MATCH path = (t:Topic {name: $name})-[*1..1]-(other:Topic)
        WHERE other.name <> $name
        RETURN DISTINCT other.name as name, other.description as description,
               other.category as category, other.importance as importance,
               length(path) as distance
        ORDER BY distance, other.importance DESC LIMIT 20""",
    2: """MATCH path = (t:Topic {name: $name})-[*1..2]-(other:Topic)
        WHERE other.name <> $name
        RETURN DISTINCT other.name as name, other.description as description,
               other.category as category, other.importance as importance,
               length(path) as distance
        ORDER BY distance, other.importance DESC LIMIT 20""",
    3: """MATCH path = (t:Topic {name: $name})-[*1..3]-(other:Topic)
        WHERE other.name <> $name
        RETURN DISTINCT other.name as name, other.description as description,
               other.category as category, other.importance as importance,
               length(path) as distance
        ORDER BY distance, other.importance DESC LIMIT 20""",
    4: """MATCH path = (t:Topic {name: $name})-[*1..4]-(other:Topic)
        WHERE other.name <> $name
        RETURN DISTINCT other.name as name, other.description as description,
               other.category as category, other.importance as importance,
               length(path) as distance
        ORDER BY distance, other.importance DESC LIMIT 20""",
}
COUNT_QUERIES = {
    'topics': 'MATCH (n:Topic) RETURN count(n) as count',
    'categories': 'MATCH (n:KnowledgeCategory) RETURN count(n) as count',
    'sections': 'MATCH (n:KnowledgeSection) RETURN count(n) as count',
}


def handle_error(e, message):
    """Handle and log errors"""
    logger.error(f"{message}: {e}")
    return Response({'error': message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def map_topic_record(record):
    """Map a topic record to dictionary"""
    topic = {
        'name': record['name'],
        'description': record['description'],
        'category': record['category'],
        'importance': record['importance']
    }
    for field in ('article_content', 'real_world_examples', 'resource_links', 'topic_image', 'code_image', 'graph_image', 'code_language', 'code_snippet', 'cypher_example'):
        if field in record.keys():
            topic[field] = record[field]
    return topic


class BaseAuthenticatedView(APIView):
    """Base view with common authentication configuration"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [CognoDBTokenAuthentication]


class HealthCheckView(APIView):
    """Health check endpoint"""
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def get(self, request):
        try:
            with neo4j_session() as session:
                session.run("RETURN 1")
            return Response({'status': 'healthy', 'database': 'connected'})
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return Response({'status': 'unhealthy', 'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class TopicListView(BaseAuthenticatedView):
    """Get all topics in the knowledge graph"""
    
    def post(self, request):
        try:
            with neo4j_session() as session:
                result = session.run(TOPIC_LIST_QUERY)
                topics = [map_topic_record(record) for record in result]
            return Response({'topics': topics})
        except Exception as e:
            return handle_error(e, 'Failed to retrieve topics. Please try again later.')


class TopicDetailView(BaseAuthenticatedView):
    """Get details of a specific topic"""
    
    def post(self, request):
        topic_name = request.data.get('topic_name')
        if not topic_name:
            return Response({'error': 'topic_name required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with neo4j_session() as session:
                result = session.run(TOPIC_DETAIL_QUERY, {'name': topic_name})
                topic = result.single()

                if not topic:
                    return Response({'error': 'Topic not found'}, status=status.HTTP_404_NOT_FOUND)
                
                return Response({'topic': map_topic_record(topic)})
        except Exception as e:
            return handle_error(e, 'Failed to retrieve topic details. Please try again later.')


class TopicRelationshipsView(BaseAuthenticatedView):
    """Get all relationships for a specific topic"""
    
    def post(self, request):
        topic_name = request.data.get('topic_name')
        if not topic_name:
            return Response({'error': 'topic_name required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with neo4j_session() as session:
                result = session.run("""
                    MATCH (t:Topic {name: $name})-[r]->(other:Topic)
                    RETURN t.name as from_topic, other.name as to_topic, type(r) as relationship_type
                    UNION
                    MATCH (t:Topic {name: $name})<-[r]-(other:Topic)
                    RETURN other.name as from_topic, t.name as to_topic, type(r) as relationship_type
                """, {'name': topic_name})
                relationships = [
                    {
                        'from_topic': r['from_topic'],
                        'to_topic': r['to_topic'],
                        'relationship_type': r['relationship_type']
                    }
                    for r in result
                ]
            return Response({'relationships': relationships})
        except Exception as e:
            return handle_error(e, 'Failed to retrieve topic relationships. Please try again later.')


class SearchTopicsView(BaseAuthenticatedView):
    """Search topics by name or description"""
    
    def post(self, request):
        search_term = request.data.get('q', '')
        if not search_term:
            return Response({'error': 'Search term required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with neo4j_session() as session:
                result = session.run(TOPIC_SEARCH_QUERY, {'term': search_term})
                topics = [map_topic_record(record) for record in result]
            return Response({'topics': topics, 'search_term': search_term})
        except Exception as e:
            return handle_error(e, 'Search failed. Please try again later.')


class TopicsByCategoryView(BaseAuthenticatedView):
    """Get all topics in a specific category"""
    
    def post(self, request):
        category = request.data.get('category')
        if not category:
            return Response({'error': 'category required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with neo4j_session() as session:
                result = session.run(TOPIC_CATEGORY_QUERY, {'category': category})
                topics = [map_topic_record(record) for record in result]
            return Response({'topics': topics, 'category': category})
        except Exception as e:
            return handle_error(e, 'Failed to retrieve topics by category. Please try again later.')


class RelatedTopicsView(BaseAuthenticatedView):
    """Find topics related to a given topic (multi-hop traversal)"""
    
    def post(self, request):
        topic_name = request.data.get('topic_name')
        hops = request.data.get('hops')
        
        if not topic_name:
            return Response({'error': 'topic_name required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if hops is None:
            return Response({'error': 'hops required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            hops = int(hops)
        except (ValueError, TypeError):
            return Response({'error': 'hops must be a valid integer'}, status=status.HTTP_400_BAD_REQUEST)
        
        if hops not in HOP_QUERIES:
            return Response({'error': 'Hops must be between 1 and 4'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with neo4j_session() as session:
                result = session.run(HOP_QUERIES[hops], {'name': topic_name})
                topics = [
                    {
                        'name': r['name'],
                        'description': r['description'],
                        'category': r['category'],
                        'importance': r['importance'],
                        'distance': r['distance']
                    }
                    for r in result
                ]
            return Response({'related_topics': topics, 'original_topic': topic_name, 'max_hops': hops})
        except Exception as e:
            return handle_error(e, 'Failed to find related topics. Please try again later.')


class PrerequisitesView(BaseAuthenticatedView):
    """Get prerequisites for a topic (topics that build up to this one)"""
    
    def post(self, request):
        topic_name = request.data.get('topic_name')
        if not topic_name:
            return Response({'error': 'topic_name required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with neo4j_session() as session:
                result = session.run("""
                          MATCH (t:Topic {name: $name})-[:BUILDS_ON*]->(prereq:Topic)
                          RETURN DISTINCT prereq.name as name, prereq.description as description,
                              prereq.category as category, prereq.importance as importance
                    ORDER BY prereq.importance DESC
                """, {'name': topic_name})
                prerequisites = [map_topic_record(record) for record in result]
            return Response({'prerequisites': prerequisites, 'topic': topic_name})
        except Exception as e:
            return handle_error(e, 'Failed to retrieve prerequisites. Please try again later.')


class ApplicationsView(BaseAuthenticatedView):
    """Get applications of a topic (where this topic is applied)"""
    
    def post(self, request):
        topic_name = request.data.get('topic_name')
        if not topic_name:
            return Response({'error': 'topic_name required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with neo4j_session() as session:
                result = session.run("""
                    MATCH (t:Topic {name: $name})-[:APPLIES_TO]->(app:Topic)
                    RETURN app.name as name, app.description as description,
                           app.category as category, app.importance as importance
                    ORDER BY app.importance DESC
                """, {'name': topic_name})
                applications = [map_topic_record(record) for record in result]
            return Response({'applications': applications, 'topic': topic_name})
        except Exception as e:
            return handle_error(e, 'Failed to retrieve applications. Please try again later.')


class CategoriesView(BaseAuthenticatedView):
    """Get all unique categories in the knowledge graph"""
    
    def post(self, request):
        try:
            with neo4j_session() as session:
                result = session.run("""
                    MATCH (t:Topic)
                    RETURN DISTINCT t.category as category
                    ORDER BY category
                """)
                categories = [r['category'] for r in result]
            return Response({'categories': categories})
        except Exception as e:
            return handle_error(e, 'Failed to retrieve categories. Please try again later.')


class KnowledgeSectionsView(BaseAuthenticatedView):
    """Return the curated learning sections seeded for the Explorer."""

    def post(self, request):
        try:
            with neo4j_session() as session:
                result = session.run("""
                    MATCH (s:KnowledgeSection)
                    OPTIONAL MATCH (s)-[:COVERS_CATEGORY]->(c:KnowledgeCategory)
                    OPTIONAL MATCH (s)-[:INCLUDES_TOPIC]->(t:Topic)
                    RETURN s.name as name,
                           s.display_order as display_order,
                           s.objective as objective,
                           s.introduction as introduction,
                           s.graph_database_context as graph_database_context,
                           s.cognodb_context as cognodb_context,
                           s.example_path as example_path,
                           collect(DISTINCT c.name) as categories,
                           collect(DISTINCT t.name) as topics
                    ORDER BY s.display_order
                """)
                sections = [dict(record) for record in result]
            return Response({'sections': sections})
        except Exception as e:
            return handle_error(e, 'Failed to retrieve knowledge sections. Please try again later.')


class KnowledgeOverviewView(BaseAuthenticatedView):
    """Return graph statistics and relationship explanations for the Explorer."""

    def post(self, request):
        try:
            with neo4j_session() as session:
                counts = {}
                for key in COUNT_QUERIES:
                    result = session.run(COUNT_QUERIES[key])
                    counts[key] = result.single()['count']

                result = session.run('MATCH (:Topic)-[r]->(:Topic) RETURN count(r) as count')
                counts['relationships'] = result.single()['count']

                result = session.run("""
                    MATCH (r:RelationshipType)
                    RETURN r.name as name, r.description as description
                    ORDER BY r.name
                """)
                relationship_types = [dict(record) for record in result]

            return Response({
                'counts': counts,
                'relationship_types': relationship_types,
                'relationship_type_names': list(RELATIONSHIP_TYPES),
            })
        except Exception as e:
            return handle_error(e, 'Failed to retrieve knowledge graph overview.')