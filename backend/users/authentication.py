"""
Custom Authentication Backend for CognoDB
"""
from django.contrib.auth.backends import BaseBackend
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from users.models import UserManager
from backend.utils import neo4j_session
import logging

logger = logging.getLogger(__name__)


class CognoDBAuthenticationBackend(BaseBackend):
    """Authentication backend using CognoDB"""
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
        
        user = UserManager.get_user_by_email(username) if '@' in username else UserManager.get_user_by_phone(username)
        return user if user and user.check_password(password) and user.is_active else None
    
    def get_user(self, user_id):
        try:
            return UserManager.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None


class CognoDBTokenAuthentication(BaseAuthentication):
    """Authenticate API requests using access tokens stored in CognoDB."""

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header:
            return None

        scheme, _, token = auth_header.partition(' ')
        if scheme not in ('Bearer', 'Token') or not token:
            raise AuthenticationFailed('Invalid authorization header.')

        try:
            with neo4j_session() as session:
                result = session.run("""
                    MATCH (u:User)-[:HAS_TOKEN]->(t:Token {
                        key: $token, token_type: 'access'
                    })
                    WHERE t.expires_at > datetime() AND u.is_active = true
                    RETURN u.id as id, u.email as email,
                           u.first_name as first_name, u.last_name as last_name,
                           u.phone_number as phone_number, u.password as password,
                           u.password_salt as password_salt, u.is_active as is_active,
                           u.is_staff as is_staff, u.is_superuser as is_superuser,
                           u.created_at as created_at, u.updated_at as updated_at
                """, {'token': token})
                record = result.single()

            if not record:
                raise AuthenticationFailed('Invalid or expired access token.')

            from users.models import User
            user = User(
                id=record['id'], email=record['email'],
                first_name=record['first_name'], last_name=record['last_name'],
                phone_number=record['phone_number'], password=record['password'],
                password_salt=record['password_salt'], is_active=record['is_active'],
                is_staff=record['is_staff'], is_superuser=record['is_superuser'],
                created_at=record['created_at'], updated_at=record['updated_at']
            )
            return user, token
        except AuthenticationFailed:
            raise
        except Exception as e:
            logger.error(f"Error authenticating API token: {e}")
            raise AuthenticationFailed('Token authentication failed.')