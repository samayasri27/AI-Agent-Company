"""
Authentication Manager for API Gateway
Handles token-based authentication and authorization
"""
import os
import jwt
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from fastapi import HTTPException


class AuthManager:
    """Manages authentication and authorization for API access"""
    
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        self.algorithm = 'HS256'
        self.token_expiry_hours = int(os.getenv('TOKEN_EXPIRY_HOURS', '24'))
        
        # Simple user store (in production, use a proper database)
        self.users = {
            'admin': {
                'user_id': 'admin',
                'password_hash': self._hash_password('admin123'),
                'role': 'admin',
                'permissions': ['read', 'write', 'admin']
            },
            'api_user': {
                'user_id': 'api_user',
                'password_hash': self._hash_password('api123'),
                'role': 'user',
                'permissions': ['read', 'write']
            },
            'readonly': {
                'user_id': 'readonly',
                'password_hash': self._hash_password('readonly123'),
                'role': 'readonly',
                'permissions': ['read']
            }
        }
        
        # API key store (for service-to-service authentication)
        self.api_keys = {
            'ak_test_12345': {
                'name': 'Test API Key',
                'user_id': 'api_service',
                'role': 'service',
                'permissions': ['read', 'write'],
                'created_at': datetime.now().isoformat()
            }
        }
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with username and password"""
        user = self.users.get(username)
        if not user:
            return None
        
        password_hash = self._hash_password(password)
        if password_hash != user['password_hash']:
            return None
        
        return {
            'user_id': user['user_id'],
            'role': user['role'],
            'permissions': user['permissions']
        }
    
    def generate_token(self, user_info: Dict[str, Any]) -> str:
        """Generate JWT token for authenticated user"""
        payload = {
            'user_id': user_info['user_id'],
            'role': user_info['role'],
            'permissions': user_info['permissions'],
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return user info"""
        try:
            # Development mode bypass
            if token == 'dev-token' or os.getenv('DEVELOPMENT_MODE', 'false').lower() == 'true':
                return {
                    'user_id': 'dev_user',
                    'role': 'admin',
                    'permissions': ['read', 'write', 'admin']
                }
            
            # Check if it's an API key
            if token.startswith('ak_'):
                return self._verify_api_key(token)
            
            # Decode JWT token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            return {
                'user_id': payload['user_id'],
                'role': payload['role'],
                'permissions': payload['permissions']
            }
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
    
    def _verify_api_key(self, api_key: str) -> Dict[str, Any]:
        """Verify API key"""
        key_info = self.api_keys.get(api_key)
        if not key_info:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        return {
            'user_id': key_info['user_id'],
            'role': key_info['role'],
            'permissions': key_info['permissions'],
            'auth_type': 'api_key'
        }
    
    def check_permission(self, user_info: Dict[str, Any], required_permission: str) -> bool:
        """Check if user has required permission"""
        user_permissions = user_info.get('permissions', [])
        return required_permission in user_permissions or 'admin' in user_permissions
    
    def require_permission(self, required_permission: str):
        """Decorator to require specific permission"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # Extract user_info from kwargs (should be injected by auth middleware)
                user_info = kwargs.get('user_info')
                if not user_info:
                    raise HTTPException(status_code=401, detail="Authentication required")
                
                if not self.check_permission(user_info, required_permission):
                    raise HTTPException(status_code=403, detail="Insufficient permissions")
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    def create_api_key(self, name: str, permissions: List[str]) -> str:
        """Create new API key"""
        import secrets
        api_key = f"ak_{secrets.token_urlsafe(16)}"
        
        self.api_keys[api_key] = {
            'name': name,
            'user_id': f'api_{secrets.token_hex(4)}',
            'role': 'api',
            'permissions': permissions,
            'created_at': datetime.now().isoformat()
        }
        
        return api_key
    
    def revoke_api_key(self, api_key: str) -> bool:
        """Revoke API key"""
        if api_key in self.api_keys:
            del self.api_keys[api_key]
            return True
        return False
    
    def list_api_keys(self) -> Dict[str, Dict[str, Any]]:
        """List all API keys (without the actual key values)"""
        return {
            key: {
                'name': info['name'],
                'user_id': info['user_id'],
                'role': info['role'],
                'permissions': info['permissions'],
                'created_at': info['created_at']
            }
            for key, info in self.api_keys.items()
        }
    
    def get_login_endpoint(self):
        """Get login endpoint configuration"""
        return {
            'endpoint': '/auth/login',
            'method': 'POST',
            'body': {
                'username': 'string',
                'password': 'string'
            },
            'response': {
                'access_token': 'string',
                'token_type': 'bearer',
                'expires_in': 'number'
            }
        }


# Authentication endpoints (to be added to the main FastAPI app)
def setup_auth_routes(app, auth_manager: AuthManager):
    """Setup authentication routes"""
    from fastapi import Form
    from pydantic import BaseModel
    
    class LoginRequest(BaseModel):
        username: str
        password: str
    
    class LoginResponse(BaseModel):
        access_token: str
        token_type: str
        expires_in: int
        user_info: Dict[str, Any]
    
    @app.post("/auth/login", response_model=LoginResponse)
    async def login(login_request: LoginRequest):
        """Login endpoint"""
        user_info = auth_manager.authenticate_user(
            login_request.username, 
            login_request.password
        )
        
        if not user_info:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token = auth_manager.generate_token(user_info)
        
        return LoginResponse(
            access_token=token,
            token_type="bearer",
            expires_in=auth_manager.token_expiry_hours * 3600,
            user_info=user_info
        )
    
    @app.post("/auth/api-key")
    async def create_api_key(
        name: str = Form(...),
        permissions: str = Form(...),  # Comma-separated permissions
        credentials = None  # Add proper auth dependency
    ):
        """Create new API key (admin only)"""
        # This would need proper admin authentication
        permissions_list = [p.strip() for p in permissions.split(',')]
        api_key = auth_manager.create_api_key(name, permissions_list)
        
        return {
            'api_key': api_key,
            'name': name,
            'permissions': permissions_list,
            'created_at': datetime.now().isoformat()
        }
    
    @app.get("/auth/keys")
    async def list_api_keys():
        """List API keys (admin only)"""
        return auth_manager.list_api_keys()
    
    @app.delete("/auth/keys/{api_key}")
    async def revoke_api_key(api_key: str):
        """Revoke API key (admin only)"""
        success = auth_manager.revoke_api_key(api_key)
        if success:
            return {"message": "API key revoked successfully"}
        else:
            raise HTTPException(status_code=404, detail="API key not found")