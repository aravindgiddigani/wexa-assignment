"""
CognoDB-based User Model for Authentication
Supports login with email or phone number using graph database
"""
import hashlib
import secrets
from backend.utils import neo4j_session
import logging

logger = logging.getLogger(__name__)


def _map_record_to_user(record):
    """Map a Neo4j record to User object"""
    return User(
        id=record['id'],
        email=record['email'],
        first_name=record['first_name'],
        last_name=record['last_name'],
        phone_number=record['phone_number'],
        password=record['password'],
        password_salt=record['password_salt'],
        is_active=record['is_active'],
        is_staff=record['is_staff'],
        is_superuser=record['is_superuser'],
        created_at=record['created_at'],
        updated_at=record['updated_at']
    )


class User:
    """User model backed by CognoDB graph database"""
    
    def __init__(self, id=None, email=None, first_name=None, last_name=None, 
                 phone_number=None, password=None, password_salt=None, 
                 is_active=True, is_staff=False, is_superuser=False, 
                 created_at=None, updated_at=None):
        self.id = id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.password = password
        self.password_salt = password_salt
        self.is_active = is_active
        self.is_staff = is_staff
        self.is_superuser = is_superuser
        self.created_at = created_at
        self.updated_at = updated_at
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def to_dict(self):
        """Convert user to dictionary"""
        created_at = self.created_at.isoformat() if self.created_at else None
        updated_at = self.updated_at.isoformat() if self.updated_at else None
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone_number': self.phone_number,
            'is_active': self.is_active,
            'is_staff': self.is_staff,
            'is_superuser': self.is_superuser,
            'created_at': created_at,
            'updated_at': updated_at
        }
    
    def set_password(self, raw_password):
        """Set password with salt-based hashing"""
        self.password_salt = secrets.token_hex(32)
        salted_password = f"{self.password_salt}{raw_password}".encode('utf-8')
        self.password = hashlib.sha256(salted_password).hexdigest()
    
    def check_password(self, raw_password):
        """Check password with salt-based hashing"""
        if not self.password_salt or not self.password:
            return False
        salted_password = f"{self.password_salt}{raw_password}".encode('utf-8')
        return self.password == hashlib.sha256(salted_password).hexdigest()
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        return self.is_superuser
    
    @property
    def is_authenticated(self):
        return self.id is not None
    
    @property
    def is_anonymous(self):
        return self.id is None


class UserManager:
    """Manager for User operations using CognoDB"""
    
    USER_QUERY = """
        RETURN u.id as id, u.email as email, u.first_name as first_name,
               u.last_name as last_name, u.phone_number as phone_number,
               u.password as password, u.password_salt as password_salt,
               u.is_active as is_active, u.is_staff as is_staff,
               u.is_superuser as is_superuser, u.created_at as created_at,
               u.updated_at as updated_at
    """
    USER_LOOKUP_QUERIES = {
        'email': "MATCH (u:User {email: $value}) " + USER_QUERY,
        'phone_number': "MATCH (u:User {phone_number: $value}) " + USER_QUERY,
        'id': "MATCH (u:User {id: $value}) " + USER_QUERY,
    }
    USER_EXISTS_QUERIES = {
        'email': "MATCH (u:User {email: $value}) RETURN count(u) as count",
        'phone_number': "MATCH (u:User {phone_number: $value}) RETURN count(u) as count",
        'id': "MATCH (u:User {id: $value}) RETURN count(u) as count",
    }
    USER_ID_UPDATE_QUERIES = {
        'email': "MATCH (u:User {email: $value}) SET u.id = $id",
        'phone_number': "MATCH (u:User {phone_number: $value}) SET u.id = $id",
        'id': "MATCH (u:User {id: $value}) SET u.id = $id",
    }
    
    @staticmethod
    def create_user(email, first_name, last_name, phone_number, password=None, **extra_fields):
        if not email or not phone_number:
            raise ValueError('Email and phone number are required')
        
        if UserManager.email_exists(email):
            raise ValueError('User with this email already exists')
        if UserManager.phone_exists(phone_number):
            raise ValueError('User with this phone number already exists')
        
        user = User(email=email.lower(), first_name=first_name, last_name=last_name, 
                   phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        
        UserManager.save_user(user)
        return user
    
    @staticmethod
    def create_superuser(email, first_name, last_name, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if not extra_fields.get('is_staff') or not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_staff=True and is_superuser=True.')
        return UserManager.create_user(email, first_name, last_name, phone_number, password, **extra_fields)
    
    @staticmethod
    def save_user(user):
        try:
            with neo4j_session() as session:
                user_data = {
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone_number': user.phone_number,
                    'password': user.password,
                    'password_salt': user.password_salt,
                    'is_active': user.is_active,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser
                }
                
                if user.id:
                    user_data['id'] = user.id
                    result = session.run("""
                        MATCH (u:User {id: $id})
                        SET u.email = $email, u.first_name = $first_name, u.last_name = $last_name,
                            u.phone_number = $phone_number, u.password = $password, u.password_salt = $password_salt,
                            u.is_active = $is_active, u.is_staff = $is_staff, u.is_superuser = $is_superuser,
                            u.updated_at = datetime()
                        RETURN u.id as id
                    """, user_data)
                else:
                    user_data['id'] = secrets.randbits(63)
                    result = session.run("""
                        CREATE (u:User {
                            id: $id,
                            email: $email, first_name: $first_name, last_name: $last_name,
                            phone_number: $phone_number, password: $password, password_salt: $password_salt,
                            is_active: $is_active, is_staff: $is_staff, is_superuser: $is_superuser,
                            created_at: datetime(), updated_at: datetime()
                        })
                        RETURN u.id as id
                    """, user_data)
                
                if record := result.single():
                    user.id = record['id']
            logger.info(f"User saved: {user.email}")
        except Exception as e:
            logger.error(f"Error saving user: {e}")
            raise
    
    @staticmethod
    def _get_user_by_field(field, value):
        """Generic method to get user by any field"""
        try:
            with neo4j_session() as session:
                result = session.run(UserManager.USER_LOOKUP_QUERIES[field], {'value': value})
                if record := result.single():
                    user = _map_record_to_user(record)
                    if user.id is None:
                        user.id = secrets.randbits(63)
                        session.run(UserManager.USER_ID_UPDATE_QUERIES[field], {'value': value, 'id': user.id})
                    return user
            return None
        except Exception as e:
            logger.error(f"Error getting user by {field}: {e}")
            raise
    
    @staticmethod
    def get_user_by_email(email):
        return UserManager._get_user_by_field('email', email.lower())
    
    @staticmethod
    def get_user_by_phone(phone_number):
        return UserManager._get_user_by_field('phone_number', phone_number)
    
    @staticmethod
    def get_user_by_id(user_id):
        return UserManager._get_user_by_field('id', user_id)
    
    @staticmethod
    def _field_exists(field, value):
        """Generic method to check if field value exists"""
        try:
            with neo4j_session() as session:
                result = session.run(UserManager.USER_EXISTS_QUERIES[field], {'value': value})
                if record := result.single():
                    return record['count'] > 0
            return False
        except Exception as e:
            logger.error(f"Error checking {field} existence: {e}")
            return False
    
    @staticmethod
    def email_exists(email):
        return UserManager._field_exists('email', email.lower())
    
    @staticmethod
    def phone_exists(phone_number):
        return UserManager._field_exists('phone_number', phone_number)
    
    @staticmethod
    def delete_user(user_id):
        try:
            with neo4j_session() as session:
                session.run("MATCH (u:User {id: $id}) DETACH DELETE u", {'id': user_id})
            logger.info(f"User deleted: {user_id}")
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            raise
