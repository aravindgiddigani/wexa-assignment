from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from neo4j import GraphDatabase
from rest_framework.test import APIRequestFactory

from knowledge.db import Neo4jConnection
from knowledge.views import HealthCheckView, PrerequisitesView, handle_error


class KnowledgeViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @staticmethod
    def session_context(session):
        context = MagicMock()
        context.__enter__.return_value = session
        context.__exit__.return_value = None
        return context

    def test_prerequisites_follow_edges_into_selected_topic(self):
        result = MagicMock()
        result.__iter__.return_value = iter([])
        session = MagicMock()
        session.run.return_value = result

        with patch('knowledge.views.neo4j_session', return_value=self.session_context(session)):
            request = PrerequisitesView().initialize_request(self.factory.post(
                '/api/knowledge/topics/prerequisites/',
                {'topic_name': 'Deep Learning'},
                format='json',
            ))
            response = PrerequisitesView().post(request)

        query, parameters = session.run.call_args.args
        self.assertIn('(prereq:Topic)-[:BUILDS_ON*]->(t:Topic {name: $name})', query)
        self.assertEqual(parameters, {'name': 'Deep Learning'})
        self.assertEqual(response.status_code, 200)

    def test_database_errors_return_service_unavailable(self):
        response = handle_error(ConnectionError('connection failed'), 'Graph unavailable')

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.data, {'error': 'Graph unavailable'})

    def test_health_check_hides_database_exception_details(self):
        session = MagicMock()
        session.run.side_effect = ConnectionError('credentials leaked here')

        with patch('knowledge.views.neo4j_session', return_value=self.session_context(session)):
            response = HealthCheckView().get(HealthCheckView().initialize_request(
                self.factory.get('/api/knowledge/health/')
            ))

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.data, {
            'status': 'unhealthy',
            'database': 'unavailable',
            'error': 'Database is unavailable. Please try again later.',
        })
        self.assertNotIn('credentials', str(response.data))

    def test_failed_driver_verification_is_closed_and_not_cached(self):
        driver = MagicMock()
        driver.verify_connectivity.side_effect = RuntimeError('verification failed')
        connection = Neo4jConnection()
        connection.close()
        connection._connection_attempts = connection._max_attempts

        with patch.object(GraphDatabase, 'driver', return_value=driver):
            with self.assertRaises(ConnectionError):
                connection.connect()

        driver.close.assert_called_once_with()
        self.assertIsNone(connection._driver)