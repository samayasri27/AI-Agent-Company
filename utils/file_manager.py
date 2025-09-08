"""
File Manager Module
Handles file storage, organization, and management for AI Agent Company
"""
import os
import json
import shutil
import zipfile
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    from .google_drive_manager import GoogleDriveManager
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False


class FileManager:
    """Central file management system for AI Agent Company"""
    
    def __init__(self, mode: str = "persistent", session_id: str = None, project_name: str = None):
        self.mode = mode  # 'persistent' or 'oneshot'
        self.session_id = session_id
        self.project_name = project_name
        self.base_path = self._determine_base_path()
        self.session_path = None
        
        # File categories and their subdirectories
        self.categories = {
            'docs': 'docs',
            'code': 'code', 
            'designs': 'designs',
            'reports': 'reports',
            'data': 'data',
            'logs': 'logs'
        }
        
        # Google Drive integration
        self.drive_manager = None
        self.drive_folder_id = None
        self.drive_subfolder_ids = {}
        
        if GOOGLE_DRIVE_AVAILABLE and os.getenv('GOOGLE_DRIVE_ENABLED', 'false').lower() == 'true':
            try:
                self.drive_manager = GoogleDriveManager()
            except Exception as e:
                print(f"Warning: Could not initialize Google Drive manager: {e}")
        
        # Initialize session structure
        if session_id:
            self.session_path = self.create_session_structure()
    
    def _determine_base_path(self) -> str:
        """Determine base path based on mode"""
        if self.mode == "oneshot" and self.project_name:
            return f"projects/{self.project_name}"
        else:
            return "company_outputs"
    
    def create_session_structure(self) -> str:
        """Create folder structure for current session"""
        if self.mode == "oneshot":
            session_dir = self.base_path
        else:
            # Create timestamped session folder for persistent mode
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_dir = f"{self.base_path}/session_{timestamp}"
        
        # Create main session directory
        os.makedirs(session_dir, exist_ok=True)
        
        # Create category subdirectories
        for category, subdir in self.categories.items():
            category_path = os.path.join(session_dir, subdir)
            os.makedirs(category_path, exist_ok=True)
        
        # Create Google Drive folder if enabled
        drive_info = {}
        if self.drive_manager and self.drive_manager.is_enabled():
            try:
                self.drive_folder_id = self.drive_manager.create_session_folder(
                    self.session_id, self.project_name
                )
                if self.drive_folder_id:
                    # Get subfolder IDs for categories
                    folder_files = self.drive_manager.list_folder_files(self.drive_folder_id)
                    for file_info in folder_files:
                        if file_info.get('mimeType') == 'application/vnd.google-apps.folder':
                            folder_name = file_info.get('name')
                            if folder_name in self.categories:
                                self.drive_subfolder_ids[folder_name] = file_info.get('id')
                    
                    drive_info = {
                        'enabled': True,
                        'folder_id': self.drive_folder_id,
                        'subfolder_ids': self.drive_subfolder_ids,
                        'folder_url': self.drive_manager.get_folder_info(self.drive_folder_id).get('web_view_link') if self.drive_folder_id else None
                    }
            except Exception as e:
                print(f"Warning: Could not create Google Drive folder: {e}")
                drive_info = {'enabled': False, 'error': str(e)}
        else:
            drive_info = {'enabled': False}
        
        # Create session metadata file
        metadata = {
            'session_id': self.session_id,
            'mode': self.mode,
            'project_name': self.project_name,
            'created_at': datetime.now().isoformat(),
            'categories': list(self.categories.keys()),
            'base_path': session_dir,
            'google_drive': drive_info
        }
        
        metadata_path = os.path.join(session_dir, 'session_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return session_dir
    
    def save_file(self, content: bytes, filename: str, category: str, agent_name: str = None) -> str:
        """Save file to appropriate category folder"""
        if not self.session_path:
            raise ValueError("Session not initialized. Call create_session_structure() first.")
        
        if category not in self.categories:
            raise ValueError(f"Invalid category: {category}. Valid categories: {list(self.categories.keys())}")
        
        # Ensure filename is safe
        safe_filename = self._sanitize_filename(filename)
        
        # Create full file path
        category_dir = os.path.join(self.session_path, self.categories[category])
        file_path = os.path.join(category_dir, safe_filename)
        
        # Handle duplicate filenames
        file_path = self._handle_duplicate_filename(file_path)
        
        # Write file
        if isinstance(content, str):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            with open(file_path, 'wb') as f:
                f.write(content)
        
        # Log file creation
        self._log_file_operation('create', file_path, agent_name)
        
        # Sync to Google Drive if enabled
        if self.drive_manager and self.drive_manager.is_enabled() and self.drive_folder_id:
            try:
                drive_folder_id = self.drive_subfolder_ids.get(category, self.drive_folder_id)
                upload_result = self.drive_manager.upload_file(file_path, drive_folder_id, category)
                if upload_result:
                    self._log_file_operation('sync_to_drive', file_path, agent_name, {
                        'drive_file_id': upload_result.get('file_id'),
                        'web_view_link': upload_result.get('web_view_link')
                    })
            except Exception as e:
                self._log_file_operation('sync_failed', file_path, agent_name, {'error': str(e)})
        
        return file_path
    
    def get_file_path(self, filename: str, category: str) -> str:
        """Get full path for a file in specified category"""
        if not self.session_path:
            raise ValueError("Session not initialized")
        
        if category not in self.categories:
            raise ValueError(f"Invalid category: {category}")
        
        safe_filename = self._sanitize_filename(filename)
        return os.path.join(self.session_path, self.categories[category], safe_filename)
    
    def list_session_files(self) -> List[Dict[str, Any]]:
        """List all files in current session"""
        if not self.session_path or not os.path.exists(self.session_path):
            return []
        
        files = []
        for category, subdir in self.categories.items():
            category_path = os.path.join(self.session_path, subdir)
            if os.path.exists(category_path):
                for filename in os.listdir(category_path):
                    file_path = os.path.join(category_path, filename)
                    if os.path.isfile(file_path):
                        stat = os.stat(file_path)
                        files.append({
                            'filename': filename,
                            'category': category,
                            'path': file_path,
                            'size': stat.st_size,
                            'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                            'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
        
        return sorted(files, key=lambda x: x['created_at'], reverse=True)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics for current session"""
        if not self.session_path or not os.path.exists(self.session_path):
            return {}
        
        files = self.list_session_files()
        total_size = sum(f['size'] for f in files)
        
        category_stats = {}
        for category in self.categories.keys():
            category_files = [f for f in files if f['category'] == category]
            category_stats[category] = {
                'count': len(category_files),
                'size': sum(f['size'] for f in category_files)
            }
        
        return {
            'session_id': self.session_id,
            'mode': self.mode,
            'project_name': self.project_name,
            'session_path': self.session_path,
            'total_files': len(files),
            'total_size': total_size,
            'category_stats': category_stats,
            'created_at': self._get_session_creation_time()
        }
    
    def cleanup_session(self, archive: bool = True) -> Dict[str, Any]:
        """Clean up session files with optional archiving"""
        if not self.session_path or not os.path.exists(self.session_path):
            return {'success': False, 'error': 'Session path not found'}
        
        try:
            archive_path = None
            if archive:
                # Create archive
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_name = f"{self.session_id or 'session'}_{timestamp}.zip"
                archive_path = os.path.join(os.path.dirname(self.session_path), archive_name)
                
                with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(self.session_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, self.session_path)
                            zipf.write(file_path, arcname)
            
            # Remove session directory
            shutil.rmtree(self.session_path)
            
            return {
                'success': True,
                'archived': archive,
                'archive_path': archive_path,
                'cleaned_path': self.session_path
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to be filesystem-safe"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        return filename
    
    def _handle_duplicate_filename(self, file_path: str) -> str:
        """Handle duplicate filenames by adding counter"""
        if not os.path.exists(file_path):
            return file_path
        
        base, ext = os.path.splitext(file_path)
        counter = 1
        
        while os.path.exists(f"{base}_{counter}{ext}"):
            counter += 1
        
        return f"{base}_{counter}{ext}"
    
    def _log_file_operation(self, operation: str, file_path: str, agent_name: str = None, extra_data: Dict = None):
        """Log file operations"""
        if not self.session_path:
            return
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'file_path': file_path,
            'agent_name': agent_name,
            'session_id': self.session_id
        }
        
        if extra_data:
            log_entry.update(extra_data)
        
        log_file = os.path.join(self.session_path, 'logs', 'file_operations.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def _get_session_creation_time(self) -> str:
        """Get session creation time from metadata"""
        if not self.session_path:
            return datetime.now().isoformat()
        
        metadata_path = os.path.join(self.session_path, 'session_metadata.json')
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    return metadata.get('created_at', datetime.now().isoformat())
            except:
                pass
        
        return datetime.now().isoformat()
    
    @staticmethod
    def list_all_sessions(mode: str = None) -> List[Dict[str, Any]]:
        """List all available sessions"""
        sessions = []
        
        # Check persistent mode sessions
        if mode != "oneshot":
            company_outputs = "company_outputs"
            if os.path.exists(company_outputs):
                for item in os.listdir(company_outputs):
                    session_path = os.path.join(company_outputs, item)
                    if os.path.isdir(session_path) and item.startswith('session_'):
                        metadata_path = os.path.join(session_path, 'session_metadata.json')
                        if os.path.exists(metadata_path):
                            try:
                                with open(metadata_path, 'r') as f:
                                    metadata = json.load(f)
                                    sessions.append(metadata)
                            except:
                                pass
        
        # Check oneshot mode projects
        if mode != "persistent":
            projects_dir = "projects"
            if os.path.exists(projects_dir):
                for item in os.listdir(projects_dir):
                    project_path = os.path.join(projects_dir, item)
                    if os.path.isdir(project_path):
                        metadata_path = os.path.join(project_path, 'session_metadata.json')
                        if os.path.exists(metadata_path):
                            try:
                                with open(metadata_path, 'r') as f:
                                    metadata = json.load(f)
                                    sessions.append(metadata)
                            except:
                                pass
        
        return sorted(sessions, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def sync_to_drive(self, file_path: str = None) -> Dict[str, Any]:
        """Sync files to Google Drive"""
        if not self.drive_manager or not self.drive_manager.is_enabled():
            return {'success': False, 'error': 'Google Drive not enabled'}
        
        if not self.drive_folder_id:
            return {'success': False, 'error': 'Google Drive folder not created'}
        
        if file_path:
            # Sync single file
            if not os.path.exists(file_path):
                return {'success': False, 'error': 'File not found'}
            
            # Determine category from file path
            category = None
            for cat, subdir in self.categories.items():
                if f"/{subdir}/" in file_path or file_path.endswith(f"/{subdir}"):
                    category = cat
                    break
            
            drive_folder_id = self.drive_subfolder_ids.get(category, self.drive_folder_id)
            result = self.drive_manager.upload_file(file_path, drive_folder_id, category)
            
            if result:
                return {'success': True, 'file': result}
            else:
                return {'success': False, 'error': 'Upload failed'}
        else:
            # Sync all session files
            if not self.session_path:
                return {'success': False, 'error': 'Session not initialized'}
            
            return self.drive_manager.sync_session_files(
                self.session_path, self.drive_folder_id, self.drive_subfolder_ids
            )
    
    def get_drive_sync_status(self) -> Dict[str, Any]:
        """Get Google Drive synchronization status"""
        if not self.drive_manager or not self.drive_manager.is_enabled():
            return {'enabled': False, 'error': 'Google Drive not enabled'}
        
        if not self.drive_folder_id or not self.session_path:
            return {'enabled': False, 'error': 'Session or Drive folder not initialized'}
        
        return self.drive_manager.get_sync_status(self.session_path, self.drive_folder_id)
    
    def get_drive_folder_url(self) -> Optional[str]:
        """Get Google Drive folder URL"""
        if not self.drive_manager or not self.drive_manager.is_enabled() or not self.drive_folder_id:
            return None
        
        folder_info = self.drive_manager.get_folder_info(self.drive_folder_id)
        return folder_info.get('web_view_link') if folder_info else None
    
    def is_drive_enabled(self) -> bool:
        """Check if Google Drive integration is enabled"""
        return self.drive_manager is not None and self.drive_manager.is_enabled()
    
    def get_drive_setup_instructions(self) -> Dict[str, Any]:
        """Get Google Drive setup instructions"""
        if GOOGLE_DRIVE_AVAILABLE:
            return GoogleDriveManager.get_setup_instructions()
        else:
            return {
                'error': 'Google Drive libraries not available',
                'install_command': 'pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib'
            }