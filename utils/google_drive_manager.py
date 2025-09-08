"""
Google Drive Manager Module
Handles Google Drive integration for file synchronization and collaboration
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False


class GoogleDriveManager:
    """Manages Google Drive integration for file synchronization"""
    
    # Google Drive API scopes
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    def __init__(self, credentials_path: str = None, token_path: str = None):
        self.credentials_path = credentials_path or os.getenv('GOOGLE_DRIVE_CREDENTIALS_PATH', 'credentials.json')
        self.token_path = token_path or os.getenv('GOOGLE_DRIVE_TOKEN_PATH', 'token.json')
        self.service = None
        self.enabled = os.getenv('GOOGLE_DRIVE_ENABLED', 'false').lower() == 'true'
        self.root_folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID', None)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        if not GOOGLE_DRIVE_AVAILABLE:
            self.logger.warning("Google Drive API libraries not available. Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
            self.enabled = False
        
        if self.enabled:
            self._authenticate()
    
    def _authenticate(self) -> bool:
        """Authenticate with Google Drive API"""
        if not GOOGLE_DRIVE_AVAILABLE:
            return False
        
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
            except Exception as e:
                self.logger.error(f"Error loading token: {e}")
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    self.logger.error(f"Error refreshing token: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_path):
                    self.logger.error(f"Credentials file not found: {self.credentials_path}")
                    self.enabled = False
                    return False
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    self.logger.error(f"Error during OAuth flow: {e}")
                    self.enabled = False
                    return False
            
            # Save the credentials for the next run
            try:
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                self.logger.error(f"Error saving token: {e}")
        
        try:
            self.service = build('drive', 'v3', credentials=creds)
            return True
        except Exception as e:
            self.logger.error(f"Error building Drive service: {e}")
            self.enabled = False
            return False
    
    def is_enabled(self) -> bool:
        """Check if Google Drive integration is enabled and working"""
        return self.enabled and self.service is not None
    
    def create_session_folder(self, session_id: str, project_name: str = None) -> Optional[str]:
        """Create a folder in Google Drive for the session"""
        if not self.is_enabled():
            return None
        
        try:
            # Determine folder name
            if project_name:
                folder_name = f"{project_name}_{session_id}"
            else:
                folder_name = f"Session_{session_id}"
            
            # Create folder metadata
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [self.root_folder_id] if self.root_folder_id else []
            }
            
            # Create folder
            folder = self.service.files().create(body=folder_metadata, fields='id,name,webViewLink').execute()
            
            folder_id = folder.get('id')
            self.logger.info(f"Created Google Drive folder: {folder_name} (ID: {folder_id})")
            
            # Create subfolders for categories
            categories = ['docs', 'code', 'designs', 'reports', 'data', 'logs']
            subfolder_ids = {}
            
            for category in categories:
                subfolder_metadata = {
                    'name': category,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [folder_id]
                }
                
                subfolder = self.service.files().create(body=subfolder_metadata, fields='id').execute()
                subfolder_ids[category] = subfolder.get('id')
            
            # Store folder mapping
            folder_info = {
                'session_id': session_id,
                'project_name': project_name,
                'folder_id': folder_id,
                'folder_name': folder_name,
                'web_view_link': folder.get('webViewLink'),
                'subfolder_ids': subfolder_ids,
                'created_at': datetime.now().isoformat()
            }
            
            return folder_id
            
        except Exception as e:
            self.logger.error(f"Error creating Google Drive folder: {e}")
            return None
    
    def upload_file(self, local_file_path: str, drive_folder_id: str, category: str = None) -> Optional[Dict[str, Any]]:
        """Upload a file to Google Drive"""
        if not self.is_enabled():
            return None
        
        if not os.path.exists(local_file_path):
            self.logger.error(f"Local file not found: {local_file_path}")
            return None
        
        try:
            filename = os.path.basename(local_file_path)
            
            # Determine MIME type
            mime_type = self._get_mime_type(local_file_path)
            
            # Create file metadata
            file_metadata = {
                'name': filename,
                'parents': [drive_folder_id]
            }
            
            # Upload file
            media = MediaFileUpload(local_file_path, mimetype=mime_type, resumable=True)
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink,size,createdTime'
            ).execute()
            
            file_info = {
                'file_id': file.get('id'),
                'name': file.get('name'),
                'web_view_link': file.get('webViewLink'),
                'size': file.get('size'),
                'created_time': file.get('createdTime'),
                'local_path': local_file_path,
                'category': category,
                'uploaded_at': datetime.now().isoformat()
            }
            
            self.logger.info(f"Uploaded file to Google Drive: {filename}")
            return file_info
            
        except Exception as e:
            self.logger.error(f"Error uploading file to Google Drive: {e}")
            return None
    
    def sync_session_files(self, session_path: str, drive_folder_id: str, subfolder_ids: Dict[str, str]) -> Dict[str, Any]:
        """Sync all files in a session to Google Drive"""
        if not self.is_enabled():
            return {'success': False, 'error': 'Google Drive not enabled'}
        
        if not os.path.exists(session_path):
            return {'success': False, 'error': 'Session path not found'}
        
        sync_results = {
            'success': True,
            'uploaded_files': [],
            'failed_files': [],
            'total_files': 0,
            'total_size': 0
        }
        
        try:
            # Categories to sync
            categories = ['docs', 'code', 'designs', 'reports', 'data']
            
            for category in categories:
                category_path = os.path.join(session_path, category)
                if not os.path.exists(category_path):
                    continue
                
                category_folder_id = subfolder_ids.get(category, drive_folder_id)
                
                for filename in os.listdir(category_path):
                    file_path = os.path.join(category_path, filename)
                    if os.path.isfile(file_path):
                        sync_results['total_files'] += 1
                        sync_results['total_size'] += os.path.getsize(file_path)
                        
                        # Upload file
                        upload_result = self.upload_file(file_path, category_folder_id, category)
                        
                        if upload_result:
                            sync_results['uploaded_files'].append(upload_result)
                        else:
                            sync_results['failed_files'].append({
                                'file_path': file_path,
                                'category': category,
                                'error': 'Upload failed'
                            })
            
            return sync_results
            
        except Exception as e:
            self.logger.error(f"Error syncing session files: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_folder_info(self, folder_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a Google Drive folder"""
        if not self.is_enabled():
            return None
        
        try:
            folder = self.service.files().get(
                fileId=folder_id,
                fields='id,name,webViewLink,createdTime,modifiedTime'
            ).execute()
            
            return {
                'id': folder.get('id'),
                'name': folder.get('name'),
                'web_view_link': folder.get('webViewLink'),
                'created_time': folder.get('createdTime'),
                'modified_time': folder.get('modifiedTime')
            }
            
        except Exception as e:
            self.logger.error(f"Error getting folder info: {e}")
            return None
    
    def list_folder_files(self, folder_id: str) -> List[Dict[str, Any]]:
        """List files in a Google Drive folder"""
        if not self.is_enabled():
            return []
        
        try:
            results = self.service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields='files(id,name,mimeType,size,createdTime,modifiedTime,webViewLink)'
            ).execute()
            
            files = results.get('files', [])
            return files
            
        except Exception as e:
            self.logger.error(f"Error listing folder files: {e}")
            return []
    
    def delete_folder(self, folder_id: str) -> bool:
        """Delete a Google Drive folder"""
        if not self.is_enabled():
            return False
        
        try:
            self.service.files().delete(fileId=folder_id).execute()
            self.logger.info(f"Deleted Google Drive folder: {folder_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting folder: {e}")
            return False
    
    def get_sync_status(self, session_path: str, drive_folder_id: str) -> Dict[str, Any]:
        """Get synchronization status between local session and Google Drive"""
        if not self.is_enabled():
            return {'enabled': False, 'error': 'Google Drive not enabled'}
        
        try:
            # Get local files
            local_files = {}
            if os.path.exists(session_path):
                categories = ['docs', 'code', 'designs', 'reports', 'data']
                for category in categories:
                    category_path = os.path.join(session_path, category)
                    if os.path.exists(category_path):
                        for filename in os.listdir(category_path):
                            file_path = os.path.join(category_path, filename)
                            if os.path.isfile(file_path):
                                stat = os.stat(file_path)
                                local_files[f"{category}/{filename}"] = {
                                    'size': stat.st_size,
                                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                    'category': category
                                }
            
            # Get Drive files
            drive_files = {}
            drive_file_list = self.list_folder_files(drive_folder_id)
            
            for file_info in drive_file_list:
                if file_info.get('mimeType') == 'application/vnd.google-apps.folder':
                    # This is a subfolder, get its files
                    subfolder_files = self.list_folder_files(file_info['id'])
                    for subfile in subfolder_files:
                        drive_files[f"{file_info['name']}/{subfile['name']}"] = {
                            'size': int(subfile.get('size', 0)),
                            'modified': subfile.get('modifiedTime'),
                            'category': file_info['name'],
                            'web_view_link': subfile.get('webViewLink')
                        }
            
            # Compare files
            sync_status = {
                'enabled': True,
                'folder_id': drive_folder_id,
                'local_files_count': len(local_files),
                'drive_files_count': len(drive_files),
                'synced_files': [],
                'local_only_files': [],
                'drive_only_files': [],
                'out_of_sync_files': []
            }
            
            all_files = set(local_files.keys()) | set(drive_files.keys())
            
            for file_key in all_files:
                local_file = local_files.get(file_key)
                drive_file = drive_files.get(file_key)
                
                if local_file and drive_file:
                    # File exists in both places
                    if local_file['size'] == drive_file['size']:
                        sync_status['synced_files'].append({
                            'name': file_key,
                            'size': local_file['size'],
                            'category': local_file['category'],
                            'web_view_link': drive_file.get('web_view_link')
                        })
                    else:
                        sync_status['out_of_sync_files'].append({
                            'name': file_key,
                            'local_size': local_file['size'],
                            'drive_size': drive_file['size'],
                            'category': local_file['category']
                        })
                elif local_file:
                    # File only exists locally
                    sync_status['local_only_files'].append({
                        'name': file_key,
                        'size': local_file['size'],
                        'category': local_file['category']
                    })
                elif drive_file:
                    # File only exists in Drive
                    sync_status['drive_only_files'].append({
                        'name': file_key,
                        'size': drive_file['size'],
                        'category': drive_file['category'],
                        'web_view_link': drive_file.get('web_view_link')
                    })
            
            return sync_status
            
        except Exception as e:
            self.logger.error(f"Error getting sync status: {e}")
            return {'enabled': False, 'error': str(e)}
    
    def _get_mime_type(self, file_path: str) -> str:
        """Determine MIME type based on file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        
        mime_types = {
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.py': 'text/x-python',
            '.js': 'application/javascript',
            '.html': 'text/html',
            '.css': 'text/css',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.zip': 'application/zip',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif'
        }
        
        return mime_types.get(ext, 'application/octet-stream')
    
    @staticmethod
    def get_setup_instructions() -> Dict[str, Any]:
        """Get instructions for setting up Google Drive integration"""
        return {
            'steps': [
                "1. Go to the Google Cloud Console (https://console.cloud.google.com/)",
                "2. Create a new project or select an existing one",
                "3. Enable the Google Drive API for your project",
                "4. Create credentials (OAuth 2.0 Client ID) for a desktop application",
                "5. Download the credentials JSON file and save it as 'credentials.json'",
                "6. Set environment variables:",
                "   - GOOGLE_DRIVE_ENABLED=true",
                "   - GOOGLE_DRIVE_CREDENTIALS_PATH=path/to/credentials.json",
                "   - GOOGLE_DRIVE_FOLDER_ID=your_root_folder_id (optional)",
                "7. Install required packages: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
            ],
            'environment_variables': {
                'GOOGLE_DRIVE_ENABLED': 'Set to "true" to enable Google Drive integration',
                'GOOGLE_DRIVE_CREDENTIALS_PATH': 'Path to the credentials.json file',
                'GOOGLE_DRIVE_TOKEN_PATH': 'Path to store the token.json file (optional)',
                'GOOGLE_DRIVE_FOLDER_ID': 'ID of the root folder in Google Drive (optional)'
            },
            'required_packages': [
                'google-api-python-client',
                'google-auth-httplib2', 
                'google-auth-oauthlib'
            ]
        }


# Utility functions for easy integration
def create_drive_manager() -> GoogleDriveManager:
    """Create a Google Drive manager instance"""
    return GoogleDriveManager()


def is_drive_available() -> bool:
    """Check if Google Drive integration is available"""
    return GOOGLE_DRIVE_AVAILABLE and os.getenv('GOOGLE_DRIVE_ENABLED', 'false').lower() == 'true'