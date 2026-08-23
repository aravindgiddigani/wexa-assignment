"""
Authentication Views for User Registration and Login with CognoDB
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from users.serializers import RegisterSerializer, LoginSerializer, UserSerializer
from users.models import UserManager
from users.authentication import CognoDBTokenAuthentication
from backend.utils import neo4j_session
import secrets
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


ACCESS_TOKEN_LIFETIME = timedelta(minutes=30)
REFRESH_TOKEN_LIFETIME = timedelta(days=7)


def store_user_token(user_id, token, token_type, expires_at, session_id):
    """Store user token in CognoDB"""
    with neo4j_session() as session:
        session.run("""
            MATCH (u:User {id: $user_id})
            CREATE (u)-[:HAS_TOKEN]->(t:Token {
                key: $token, token_type: $token_type,
                session_id: $session_id,
                created_at: datetime(), expires_at: $expires_at
            })
        """, {
            'user_id': user_id,
            'token': token,
            'token_type': token_type,
            'session_id': session_id,
            'expires_at': expires_at
        })


def issue_tokens(user_id):
    now = datetime.now(timezone.utc)
    access_token = secrets.token_urlsafe(32)
    refresh_token = secrets.token_urlsafe(48)
    session_id = secrets.token_urlsafe(32)
    store_user_token(user_id, access_token, 'access', now + ACCESS_TOKEN_LIFETIME, session_id)
    store_user_token(user_id, refresh_token, 'refresh', now + REFRESH_TOKEN_LIFETIME, session_id)
    return access_token, refresh_token


def delete_token_by_key(token_key):
    """Revoke the access token and its paired refresh token."""
    with neo4j_session() as session:
        session.run("""
            MATCH (u:User)-[:HAS_TOKEN]->(access:Token {
                key: $token, token_type: 'access'
            })
            WITH u, access.session_id as session_id
            MATCH (u)-[:HAS_TOKEN]->(token:Token)
            WHERE (session_id IS NOT NULL AND token.session_id = session_id)
               OR (session_id IS NULL AND NOT token.session_id IS NOT NULL)
            DETACH DELETE token
        """, {'token': token_key})


class BaseAuthView(APIView):
    """Base view with common auth configuration"""
    permission_classes = [AllowAny]
    authentication_classes = []


class RegisterView(BaseAuthView):
    """User registration endpoint"""
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                
                return Response({
                    'message': 'Successfully registered, log in to continue.'
                }, status=status.HTTP_201_CREATED)
            except ValueError as e:
                logger.error(f"Registration validation error: {e}")
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Registration error: {e}")
                return Response({'error': 'Registration failed due to server error. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(BaseAuthView):
    """User login endpoint with email or phone number"""
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            access_token, refresh_token = issue_tokens(user.id)
            
            return Response({
                'message': 'Login successful',
                'access_token': access_token,
                'refresh_token': refresh_token
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(BaseAuthView):
    """Issue a new access token using a valid refresh token."""

    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with neo4j_session() as session:
                result = session.run("""
                    MATCH (u:User)-[:HAS_TOKEN]->(t:Token {
                        key: $token, token_type: 'refresh'
                    })
                    WHERE t.expires_at > datetime() AND u.is_active = true
                    RETURN u.id as id, t.session_id as session_id
                """, {'token': refresh_token})
                record = result.single()

            if not record:
                return Response({'error': 'Invalid or expired refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)

            access_token = secrets.token_urlsafe(32)
            session_id = record['session_id'] or secrets.token_urlsafe(32)
            store_user_token(record['id'], access_token, 'access', datetime.now(timezone.utc) + ACCESS_TOKEN_LIFETIME, session_id)
            return Response({'access_token': access_token}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return Response({'error': 'Token refresh failed.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutView(APIView):
    """User logout endpoint"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [CognoDBTokenAuthentication]
    
    def post(self, request):
        try:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Bearer '):
                delete_token_by_key(auth_header[7:])
            elif auth_header.startswith('Token '):
                delete_token_by_key(auth_header[6:])
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return Response({'error': 'Logout failed due to server error. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(APIView):
    """Get current user profile"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [CognoDBTokenAuthentication]
    
    def post(self, request):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)