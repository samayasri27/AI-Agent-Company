"""
Session Manager Module
Manages session lifecycle, metadata, and coordination for AI Agent Company
"""
import uuid
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from utils.file_manager import FileManager


@dataclass
class Session:
    """Session data model"""
    id: str
    mode: str  # 'persistent' or 'oneshot'
    project_name: Optional[str]
    created_at: str
    status: str  # 'active', 'completed', 'archived'
    file_count: int = 0
    total_size: int = 0
    departments_involved: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.departments_involved is None:
            self.departments_involved = []
        if self.metadata is None:
            self.metadata = {}


class SessionManager:
    """Manages session lifecycle and coordination"""
    
    def __init__(self, mode: str = "persistent"):
        self.mode = mode
        self.current_session: Optional[Session] = None
        self.file_manager: Optional[FileManager] = None
        self.sessions_file = "sessions_registry.json"
        
        # Load existing sessions registry
        self.sessions_registry = self._load_sessions_registry()
    
    def create_session(self, project_name: str = None) -> str:
        """Create a new session"""
        # Generate unique session ID
        session_id = str(uuid.uuid4())[:8]
        
        # Create session object
        session = Session(
            id=session_id,
            mode=self.mode,
            project_name=project_name,
            created_at=datetime.now().isoformat(),
            status='active'
        )
        
        # Initialize file manager for this session
        self.file_manager = FileManager(
            mode=self.mode,
            session_id=session_id,
            project_name=project_name
        )
        
        # Create session folder structure
        session_path = self.file_manager.create_session_structure()
        session.metadata['session_path'] = session_path
        
        # Set as current session
        self.current_session = session
        
        # Register session
        self._register_session(session)
        
        return session_id
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific session"""
        session = self._find_session(session_id)
        if not session:
            return None
        
        # Get file statistics if file manager is available
        if self.file_manager and self.file_manager.session_id == session_id:
            stats = self.file_manager.get_session_stats()
            session.file_count = stats.get('total_files', 0)
            session.total_size = stats.get('total_size', 0)
        
        return asdict(session)
    
    def list_sessions(self, mode: str = None, status: str = None) -> List[Dict[str, Any]]:
        """List sessions with optional filtering"""
        sessions = []
        
        for session_data in self.sessions_registry:
            session = Session(**session_data)
            
            # Apply filters
            if mode and session.mode != mode:
                continue
            if status and session.status != status:
                continue
            
            sessions.append(asdict(session))
        
        return sorted(sessions, key=lambda x: x['created_at'], reverse=True)
    
    def end_session(self, session_id: str, archive: bool = False) -> Dict[str, Any]:
        """End a session and optionally archive it"""
        session = self._find_session(session_id)
        if not session:
            return {'success': False, 'error': 'Session not found'}
        
        try:
            # Update session status
            session.status = 'completed'
            
            # Get final statistics
            if self.file_manager and self.file_manager.session_id == session_id:
                stats = self.file_manager.get_session_stats()
                session.file_count = stats.get('total_files', 0)
                session.total_size = stats.get('total_size', 0)
                
                # Archive if requested
                if archive:
                    cleanup_result = self.file_manager.cleanup_session(archive=True)
                    if cleanup_result.get('success'):
                        session.status = 'archived'
                        session.metadata['archive_path'] = cleanup_result.get('archive_path')
            
            # Update registry
            self._update_session_in_registry(session)
            
            # Clear current session if it's the one being ended
            if self.current_session and self.current_session.id == session_id:
                self.current_session = None
                self.file_manager = None
            
            return {
                'success': True,
                'session_id': session_id,
                'status': session.status,
                'file_count': session.file_count,
                'total_size': session.total_size
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get detailed statistics for a session"""
        session = self._find_session(session_id)
        if not session:
            return {}
        
        stats = {
            'session_id': session_id,
            'mode': session.mode,
            'project_name': session.project_name,
            'status': session.status,
            'created_at': session.created_at,
            'file_count': session.file_count,
            'total_size': session.total_size,
            'departments_involved': session.departments_involved
        }
        
        # Get real-time file statistics if session is active
        if session.status == 'active' and self.file_manager and self.file_manager.session_id == session_id:
            file_stats = self.file_manager.get_session_stats()
            stats.update(file_stats)
        
        return stats
    
    def switch_session(self, session_id: str) -> bool:
        """Switch to a different active session"""
        session = self._find_session(session_id)
        if not session or session.status != 'active':
            return False
        
        # Initialize file manager for the session
        self.file_manager = FileManager(
            mode=session.mode,
            session_id=session_id,
            project_name=session.project_name
        )
        
        # Set session path from metadata
        if 'session_path' in session.metadata:
            self.file_manager.session_path = session.metadata['session_path']
        
        self.current_session = session
        return True
    
    def add_department_to_session(self, session_id: str, department: str):
        """Add a department to session's involved departments"""
        session = self._find_session(session_id)
        if session and department not in session.departments_involved:
            session.departments_involved.append(department)
            self._update_session_in_registry(session)
    
    def get_current_session(self) -> Optional[Dict[str, Any]]:
        """Get current active session"""
        if self.current_session:
            return asdict(self.current_session)
        return None
    
    def get_file_manager(self) -> Optional[FileManager]:
        """Get file manager for current session"""
        return self.file_manager
    
    def _find_session(self, session_id: str) -> Optional[Session]:
        """Find session by ID"""
        for session_data in self.sessions_registry:
            if session_data['id'] == session_id:
                return Session(**session_data)
        return None
    
    def _register_session(self, session: Session):
        """Register a new session in the registry"""
        self.sessions_registry.append(asdict(session))
        self._save_sessions_registry()
    
    def _update_session_in_registry(self, session: Session):
        """Update existing session in registry"""
        for i, session_data in enumerate(self.sessions_registry):
            if session_data['id'] == session.id:
                self.sessions_registry[i] = asdict(session)
                break
        self._save_sessions_registry()
    
    def _load_sessions_registry(self) -> List[Dict[str, Any]]:
        """Load sessions registry from file"""
        if os.path.exists(self.sessions_file):
            try:
                with open(self.sessions_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return []
    
    def _save_sessions_registry(self):
        """Save sessions registry to file"""
        try:
            with open(self.sessions_file, 'w') as f:
                json.dump(self.sessions_registry, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save sessions registry: {e}")
    
    def cleanup_old_sessions(self, days: int = 30) -> Dict[str, Any]:
        """Clean up old completed sessions"""
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        cleaned_sessions = []
        
        for session_data in self.sessions_registry[:]:  # Copy list to modify during iteration
            session = Session(**session_data)
            
            if session.status == 'completed':
                session_date = datetime.fromisoformat(session.created_at)
                if session_date < cutoff_date:
                    # Archive and remove old session
                    if 'session_path' in session.metadata and os.path.exists(session.metadata['session_path']):
                        file_manager = FileManager(
                            mode=session.mode,
                            session_id=session.id,
                            project_name=session.project_name
                        )
                        file_manager.session_path = session.metadata['session_path']
                        cleanup_result = file_manager.cleanup_session(archive=True)
                        
                        if cleanup_result.get('success'):
                            session.status = 'archived'
                            session.metadata['archive_path'] = cleanup_result.get('archive_path')
                            cleaned_sessions.append(session.id)
        
        # Save updated registry
        self._save_sessions_registry()
        
        return {
            'success': True,
            'cleaned_sessions': cleaned_sessions,
            'count': len(cleaned_sessions)
        }