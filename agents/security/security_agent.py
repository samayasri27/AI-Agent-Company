"""
Security Agent - Handles authentication, authorization, and security monitoring
"""
import os
import jwt
import bcrypt
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.agent_base import AgentBase


class SecurityAgent(AgentBase):
    """Security Agent for authentication and security monitoring"""
    
    def __init__(self):
        super().__init__(
            name="Security Agent",
            role="Security & Authentication Manager",
            department="Security"
        )
        self.capabilities = [
            "API key validation",
            "JWT token management", 
            "Access logging and monitoring",
            "Security threat detection",
            "User authentication",
            "Rate limiting enforcement"
        ]
        
        # Security configuration
        self.jwt_secret = os.getenv('JWT_SECRET_KEY', 'default-secret-change-in-production')
        self.jwt_expiry_hours = int(os.getenv('JWT_EXPIRY_HOURS', '24'))
        self.api_key_prefix = 'ak_'
        self.max_login_attempts = 5
        self.rate_limit_window = 3600  # 1 hour in seconds
        self.rate_limit_max_requests = 100
        
        # In-memory storage (in production, use Redis or database)
        self.valid_api_keys = self._load_api_keys()
        self.users = self._load_users()
        self.security_events = []
        self.login_attempts = {}
        self.rate_limit_tracking = {}
        
        # Initialize default users if none exist
        if not self.users:
            self._create_default_users()
    
    async def execute_task(self, task: str) -> Dict[str, Any]:
        """Execute security-related tasks"""
        try:
            if isinstance(task, str):
                task_dict = {'description': task, 'type': 'general'}
            else:
                task_dict = task
            
            task_description = task_dict.get('description', '').lower()
            
            if 'validate' in task_description and 'api key' in task_description:
                api_key = task_dict.get('api_key', '')
                return {'success': True, 'valid': self.validate_api_key(api_key)}
            
            elif 'generate' in task_description and 'token' in task_description:
                user_data = task_dict.get('user_data', {})
                token = self.generate_jwt_token(user_data)
                return {'success': True, 'token': token}
            
            elif 'security' in task_description and 'report' in task_description:
                return self._generate_security_report()
            
            elif 'audit' in task_description:
                return self._perform_security_audit()
            
            else:
                return self._general_security_check()
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Security task processing failed: {str(e)}",
                'agent': self.name,
                'timestamp': datetime.now().isoformat()
            }
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key"""
        try:
            if not api_key or not api_key.startswith(self.api_key_prefix):
                self._log_security_event('invalid_api_key_format', {'api_key': api_key[:10] + '...'})
                return False
            
            # Check if API key exists and is active
            key_hash = self._hash_api_key(api_key)
            is_valid = key_hash in self.valid_api_keys and self.valid_api_keys[key_hash].get('active', False)
            
            if is_valid:
                # Update last used timestamp
                self.valid_api_keys[key_hash]['last_used'] = datetime.now().isoformat()
                self._log_security_event('api_key_validated', {'key_hash': key_hash[:16] + '...'})
            else:
                self._log_security_event('invalid_api_key', {'key_hash': key_hash[:16] + '...'})
            
            return is_valid
            
        except Exception as e:
            self._log_security_event('api_key_validation_error', {'error': str(e)})
            return False
    
    def generate_jwt_token(self, user_data: Dict[str, Any]) -> str:
        """Generate JWT token for user"""
        try:
            payload = {
                'user_id': user_data.get('user_id'),
                'username': user_data.get('username'),
                'role': user_data.get('role', 'user'),
                'permissions': user_data.get('permissions', []),
                'exp': datetime.utcnow() + timedelta(hours=self.jwt_expiry_hours),
                'iat': datetime.utcnow(),
                'iss': 'ai-agent-company'
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
            
            self._log_security_event('jwt_token_generated', {
                'user_id': user_data.get('user_id'),
                'username': user_data.get('username'),
                'expires_in_hours': self.jwt_expiry_hours
            })
            
            return token
            
        except Exception as e:
            self._log_security_event('jwt_generation_error', {'error': str(e)})
            raise Exception(f"Token generation failed: {str(e)}")
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            self._log_security_event('jwt_token_verified', {
                'user_id': payload.get('user_id'),
                'username': payload.get('username')
            })
            
            return {
                'valid': True,
                'payload': payload,
                'user_id': payload.get('user_id'),
                'username': payload.get('username'),
                'role': payload.get('role'),
                'permissions': payload.get('permissions', [])
            }
            
        except jwt.ExpiredSignatureError:
            self._log_security_event('jwt_token_expired', {'token': token[:20] + '...'})
            return {'valid': False, 'error': 'Token expired'}
        
        except jwt.InvalidTokenError as e:
            self._log_security_event('jwt_token_invalid', {'error': str(e)})
            return {'valid': False, 'error': 'Invalid token'}
        
        except Exception as e:
            self._log_security_event('jwt_verification_error', {'error': str(e)})
            return {'valid': False, 'error': 'Token verification failed'}
    
    def authenticate_user(self, username: str, password: str, ip_address: str = None) -> Optional[Dict[str, Any]]:
        """Authenticate user with username and password"""
        try:
            # Check rate limiting
            if not self._check_rate_limit(username, ip_address):
                self._log_security_event('rate_limit_exceeded', {
                    'username': username,
                    'ip_address': ip_address
                })
                return None
            
            # Check login attempts
            if not self._check_login_attempts(username):
                self._log_security_event('max_login_attempts_exceeded', {'username': username})
                return None
            
            # Find user
            user = self.users.get(username)
            if not user:
                self._increment_login_attempts(username)
                self._log_security_event('user_not_found', {'username': username})
                return None
            
            # Verify password
            if not self._verify_password(password, user['password_hash']):
                self._increment_login_attempts(username)
                self._log_security_event('invalid_password', {'username': username})
                return None
            
            # Check if user is active
            if not user.get('active', True):
                self._log_security_event('inactive_user_login_attempt', {'username': username})
                return None
            
            # Reset login attempts on successful login
            self._reset_login_attempts(username)
            
            # Update last login
            user['last_login'] = datetime.now().isoformat()
            
            self._log_security_event('user_authenticated', {
                'username': username,
                'role': user.get('role'),
                'ip_address': ip_address
            })
            
            return {
                'user_id': user['user_id'],
                'username': username,
                'role': user.get('role', 'user'),
                'permissions': user.get('permissions', []),
                'last_login': user['last_login']
            }
            
        except Exception as e:
            self._log_security_event('authentication_error', {
                'username': username,
                'error': str(e)
            })
            return None
    
    def log_access_attempt(self, request_data: Dict[str, Any]) -> None:
        """Log access attempt"""
        try:
            access_log = {
                'timestamp': datetime.now().isoformat(),
                'ip_address': request_data.get('ip_address'),
                'user_agent': request_data.get('user_agent'),
                'method': request_data.get('method'),
                'endpoint': request_data.get('endpoint'),
                'user_id': request_data.get('user_id'),
                'success': request_data.get('success', False),
                'response_code': request_data.get('response_code'),
                'response_time': request_data.get('response_time')
            }
            
            self._log_security_event('access_attempt', access_log)
            
        except Exception as e:
            print(f"Error logging access attempt: {e}")
    
    def check_security_threats(self) -> List[Dict[str, Any]]:
        """Check for security threats and anomalies"""
        threats = []
        
        try:
            # Check for suspicious login patterns
            recent_events = [e for e in self.security_events 
                           if (datetime.now() - datetime.fromisoformat(e['timestamp'])).seconds < 3600]
            
            # Multiple failed logins
            failed_logins = [e for e in recent_events if e['event_type'] == 'invalid_password']
            if len(failed_logins) > 10:
                threats.append({
                    'type': 'brute_force_attack',
                    'severity': 'high',
                    'description': f'{len(failed_logins)} failed login attempts in the last hour',
                    'count': len(failed_logins)
                })
            
            # Multiple invalid API key attempts
            invalid_keys = [e for e in recent_events if e['event_type'] == 'invalid_api_key']
            if len(invalid_keys) > 20:
                threats.append({
                    'type': 'api_key_scanning',
                    'severity': 'medium',
                    'description': f'{len(invalid_keys)} invalid API key attempts in the last hour',
                    'count': len(invalid_keys)
                })
            
            # Rate limit violations
            rate_violations = [e for e in recent_events if e['event_type'] == 'rate_limit_exceeded']
            if len(rate_violations) > 5:
                threats.append({
                    'type': 'rate_limit_abuse',
                    'severity': 'medium',
                    'description': f'{len(rate_violations)} rate limit violations in the last hour',
                    'count': len(rate_violations)
                })
            
        except Exception as e:
            threats.append({
                'type': 'threat_detection_error',
                'severity': 'low',
                'description': f'Error in threat detection: {str(e)}'
            })
        
        return threats
    
    def create_api_key(self, name: str, permissions: List[str] = None) -> str:
        """Create new API key"""
        try:
            # Generate random API key
            import secrets
            key_suffix = secrets.token_urlsafe(32)
            api_key = f"{self.api_key_prefix}{key_suffix}"
            
            # Hash the key for storage
            key_hash = self._hash_api_key(api_key)
            
            # Store key metadata
            self.valid_api_keys[key_hash] = {
                'name': name,
                'permissions': permissions or [],
                'created_at': datetime.now().isoformat(),
                'last_used': None,
                'active': True
            }
            
            self._log_security_event('api_key_created', {
                'name': name,
                'key_hash': key_hash[:16] + '...',
                'permissions': permissions
            })
            
            return api_key
            
        except Exception as e:
            self._log_security_event('api_key_creation_error', {'error': str(e)})
            raise Exception(f"API key creation failed: {str(e)}")
    
    def revoke_api_key(self, api_key: str) -> bool:
        """Revoke API key"""
        try:
            key_hash = self._hash_api_key(api_key)
            
            if key_hash in self.valid_api_keys:
                self.valid_api_keys[key_hash]['active'] = False
                self.valid_api_keys[key_hash]['revoked_at'] = datetime.now().isoformat()
                
                self._log_security_event('api_key_revoked', {
                    'key_hash': key_hash[:16] + '...'
                })
                
                return True
            
            return False
            
        except Exception as e:
            self._log_security_event('api_key_revocation_error', {'error': str(e)})
            return False
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics"""
        try:
            recent_events = [e for e in self.security_events 
                           if (datetime.now() - datetime.fromisoformat(e['timestamp'])).seconds < 86400]  # 24 hours
            
            event_counts = {}
            for event in recent_events:
                event_type = event['event_type']
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            return {
                'total_events_24h': len(recent_events),
                'event_breakdown': event_counts,
                'active_api_keys': len([k for k in self.valid_api_keys.values() if k.get('active', False)]),
                'total_users': len(self.users),
                'active_users': len([u for u in self.users.values() if u.get('active', True)]),
                'security_threats': len(self.check_security_threats()),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f"Failed to get security stats: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
    
    # Private helper methods
    def _load_api_keys(self) -> Dict[str, Dict[str, Any]]:
        """Load API keys from storage"""
        try:
            if os.path.exists('security_api_keys.json'):
                with open('security_api_keys.json', 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _load_users(self) -> Dict[str, Dict[str, Any]]:
        """Load users from storage"""
        try:
            if os.path.exists('security_users.json'):
                with open('security_users.json', 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _create_default_users(self):
        """Create default users for development"""
        default_users = [
            {
                'username': 'admin',
                'password': 'admin123',
                'role': 'admin',
                'permissions': ['read', 'write', 'admin']
            },
            {
                'username': 'api_user',
                'password': 'api123',
                'role': 'api_user',
                'permissions': ['read', 'write']
            },
            {
                'username': 'readonly',
                'password': 'readonly123',
                'role': 'readonly',
                'permissions': ['read']
            }
        ]
        
        for user_data in default_users:
            username = user_data['username']
            password_hash = self._hash_password(user_data['password'])
            
            self.users[username] = {
                'user_id': f"user_{len(self.users) + 1}",
                'username': username,
                'password_hash': password_hash,
                'role': user_data['role'],
                'permissions': user_data['permissions'],
                'created_at': datetime.now().isoformat(),
                'active': True,
                'last_login': None
            }
    
    def _hash_api_key(self, api_key: str) -> str:
        """Hash API key for secure storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception:
            return False
    
    def _log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security event"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details,
            'agent': self.name
        }
        
        self.security_events.append(event)
        
        # Keep only last 1000 events in memory
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]
    
    def _check_rate_limit(self, identifier: str, ip_address: str = None) -> bool:
        """Check if request is within rate limits"""
        now = datetime.now()
        key = identifier or ip_address or 'anonymous'
        
        if key not in self.rate_limit_tracking:
            self.rate_limit_tracking[key] = []
        
        # Remove old requests outside the window
        window_start = now - timedelta(seconds=self.rate_limit_window)
        self.rate_limit_tracking[key] = [
            req_time for req_time in self.rate_limit_tracking[key]
            if req_time > window_start
        ]
        
        # Check if under limit
        if len(self.rate_limit_tracking[key]) >= self.rate_limit_max_requests:
            return False
        
        # Add current request
        self.rate_limit_tracking[key].append(now)
        return True
    
    def _check_login_attempts(self, username: str) -> bool:
        """Check if user has exceeded login attempts"""
        if username not in self.login_attempts:
            return True
        
        attempts_data = self.login_attempts[username]
        
        # Reset if enough time has passed
        if datetime.now() - attempts_data['last_attempt'] > timedelta(hours=1):
            del self.login_attempts[username]
            return True
        
        return attempts_data['count'] < self.max_login_attempts
    
    def _increment_login_attempts(self, username: str):
        """Increment failed login attempts for user"""
        if username not in self.login_attempts:
            self.login_attempts[username] = {'count': 0, 'last_attempt': datetime.now()}
        
        self.login_attempts[username]['count'] += 1
        self.login_attempts[username]['last_attempt'] = datetime.now()
    
    def _reset_login_attempts(self, username: str):
        """Reset login attempts for user"""
        if username in self.login_attempts:
            del self.login_attempts[username]
    
    def _generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        stats = self.get_security_stats()
        threats = self.check_security_threats()
        
        return {
            'success': True,
            'report_type': 'security_overview',
            'generated_at': datetime.now().isoformat(),
            'statistics': stats,
            'threats': threats,
            'recommendations': self._get_security_recommendations(stats, threats),
            'agent': self.name
        }
    
    def _perform_security_audit(self) -> Dict[str, Any]:
        """Perform security audit"""
        audit_results = {
            'jwt_configuration': self._audit_jwt_config(),
            'api_key_security': self._audit_api_keys(),
            'user_accounts': self._audit_user_accounts(),
            'rate_limiting': self._audit_rate_limiting(),
            'logging': self._audit_logging()
        }
        
        return {
            'success': True,
            'audit_type': 'comprehensive_security_audit',
            'performed_at': datetime.now().isoformat(),
            'results': audit_results,
            'overall_score': self._calculate_security_score(audit_results),
            'agent': self.name
        }
    
    def _general_security_check(self) -> Dict[str, Any]:
        """Perform general security check"""
        return {
            'success': True,
            'check_type': 'general_security_status',
            'timestamp': datetime.now().isoformat(),
            'status': 'operational',
            'active_threats': len(self.check_security_threats()),
            'security_events_24h': len([e for e in self.security_events 
                                      if (datetime.now() - datetime.fromisoformat(e['timestamp'])).seconds < 86400]),
            'agent': self.name
        }
    
    def _get_security_recommendations(self, stats: Dict, threats: List) -> List[str]:
        """Get security recommendations based on current state"""
        recommendations = []
        
        if len(threats) > 0:
            recommendations.append("Investigate and address detected security threats")
        
        if stats.get('event_breakdown', {}).get('invalid_password', 0) > 10:
            recommendations.append("Consider implementing stronger password policies")
        
        if stats.get('active_api_keys', 0) == 0:
            recommendations.append("Create API keys for external integrations")
        
        recommendations.append("Regularly review security logs and user access")
        recommendations.append("Keep JWT secret key secure and rotate periodically")
        
        return recommendations
    
    def _audit_jwt_config(self) -> Dict[str, Any]:
        """Audit JWT configuration"""
        return {
            'secret_key_set': bool(self.jwt_secret and self.jwt_secret != 'default-secret-change-in-production'),
            'expiry_reasonable': 1 <= self.jwt_expiry_hours <= 168,  # 1 hour to 1 week
            'algorithm_secure': True,  # Using HS256
            'score': 85 if self.jwt_secret != 'default-secret-change-in-production' else 40
        }
    
    def _audit_api_keys(self) -> Dict[str, Any]:
        """Audit API key security"""
        active_keys = [k for k in self.valid_api_keys.values() if k.get('active', False)]
        
        return {
            'total_keys': len(self.valid_api_keys),
            'active_keys': len(active_keys),
            'keys_with_permissions': len([k for k in active_keys if k.get('permissions')]),
            'recently_used': len([k for k in active_keys if k.get('last_used')]),
            'score': 75 if len(active_keys) > 0 else 50
        }
    
    def _audit_user_accounts(self) -> Dict[str, Any]:
        """Audit user accounts"""
        active_users = [u for u in self.users.values() if u.get('active', True)]
        
        return {
            'total_users': len(self.users),
            'active_users': len(active_users),
            'admin_users': len([u for u in active_users if u.get('role') == 'admin']),
            'users_with_recent_login': len([u for u in active_users if u.get('last_login')]),
            'score': 80
        }
    
    def _audit_rate_limiting(self) -> Dict[str, Any]:
        """Audit rate limiting configuration"""
        return {
            'enabled': True,
            'window_seconds': self.rate_limit_window,
            'max_requests': self.rate_limit_max_requests,
            'currently_tracking': len(self.rate_limit_tracking),
            'score': 90
        }
    
    def _audit_logging(self) -> Dict[str, Any]:
        """Audit security logging"""
        return {
            'events_logged': len(self.security_events),
            'event_types': len(set(e['event_type'] for e in self.security_events)),
            'recent_events': len([e for e in self.security_events 
                                if (datetime.now() - datetime.fromisoformat(e['timestamp'])).seconds < 3600]),
            'score': 85
        }
    
    def _calculate_security_score(self, audit_results: Dict) -> int:
        """Calculate overall security score"""
        scores = [result.get('score', 0) for result in audit_results.values()]
        return int(sum(scores) / len(scores)) if scores else 0