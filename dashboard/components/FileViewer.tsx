import React, { useState, useEffect } from 'react';
import { Download, Eye, FileText, Image, Code, BarChart3, File, Cloud, CloudOff, ExternalLink, RefreshCw } from 'lucide-react';

interface FileRecord {
  filename: string;
  category: string;
  path: string;
  size: number;
  created_at: string;
  modified_at: string;
  drive_url?: string;
  drive_synced?: boolean;
}

interface DriveStatus {
  enabled: boolean;
  folder_id?: string;
  folder_url?: string;
  synced_files: Array<{
    name: string;
    size: number;
    category: string;
    web_view_link?: string;
  }>;
  local_only_files: Array<{
    name: string;
    size: number;
    category: string;
  }>;
  drive_only_files: Array<{
    name: string;
    size: number;
    category: string;
    web_view_link?: string;
  }>;
  out_of_sync_files: Array<{
    name: string;
    local_size: number;
    drive_size: number;
    category: string;
  }>;
  local_files_count: number;
  drive_files_count: number;
}

interface FileViewerProps {
  sessionId?: string;
  onFileSelect?: (file: FileRecord) => void;
}

const FileViewer: React.FC<FileViewerProps> = ({ sessionId, onFileSelect }) => {
  const [files, setFiles] = useState<FileRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'name' | 'date' | 'size'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [driveStatus, setDriveStatus] = useState<DriveStatus | null>(null);
  const [syncing, setSyncing] = useState(false);
  const [showDriveDetails, setShowDriveDetails] = useState(false);

  const categories = ['all', 'docs', 'code', 'designs', 'reports', 'data'];

  useEffect(() => {
    fetchFiles();
    fetchDriveStatus();
  }, [sessionId]);

  const fetchFiles = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/files${sessionId ? `?session=${sessionId}` : ''}`);
      if (response.ok) {
        const data = await response.json();
        setFiles(data.files || []);
      }
    } catch (error) {
      console.error('Error fetching files:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDriveStatus = async () => {
    if (!sessionId) return;
    
    try {
      const response = await fetch(`/api/files/drive-status?session=${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        setDriveStatus(data);
      }
    } catch (error) {
      console.error('Error fetching drive status:', error);
    }
  };

  const handleSyncToDrive = async () => {
    if (!sessionId) return;
    
    try {
      setSyncing(true);
      const response = await fetch(`/api/files/sync-drive`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_id: sessionId }),
      });
      
      if (response.ok) {
        await fetchDriveStatus();
        await fetchFiles();
      }
    } catch (error) {
      console.error('Error syncing to drive:', error);
    } finally {
      setSyncing(false);
    }
  };

  const getFileIcon = (filename: string, category: string) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    
    if (category === 'code' || ['js', 'ts', 'py', 'html', 'css', 'json'].includes(ext || '')) {
      return <Code className="w-5 h-5 text-blue-500" />;
    }
    if (['jpg', 'jpeg', 'png', 'gif', 'svg'].includes(ext || '')) {
      return <Image className="w-5 h-5 text-green-500" />;
    }
    if (['xlsx', 'csv'].includes(ext || '')) {
      return <BarChart3 className="w-5 h-5 text-emerald-500" />;
    }
    if (['docx', 'pdf', 'txt'].includes(ext || '')) {
      return <FileText className="w-5 h-5 text-red-500" />;
    }
    return <File className="w-5 h-5 text-gray-500" />;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const filteredFiles = files
    .filter(file => selectedCategory === 'all' || file.category === selectedCategory)
    .sort((a, b) => {
      let aValue, bValue;
      
      switch (sortBy) {
        case 'name':
          aValue = a.filename.toLowerCase();
          bValue = b.filename.toLowerCase();
          break;
        case 'size':
          aValue = a.size;
          bValue = b.size;
          break;
        case 'date':
        default:
          aValue = new Date(a.created_at).getTime();
          bValue = new Date(b.created_at).getTime();
          break;
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

  const handleDownload = async (file: FileRecord) => {
    try {
      const response = await fetch(`/api/files/download?path=${encodeURIComponent(file.path)}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = file.filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Error downloading file:', error);
    }
  };

  const handlePreview = (file: FileRecord) => {
    if (onFileSelect) {
      onFileSelect(file);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span className="ml-2 text-gray-600">Loading files...</span>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-4 border-b border-gray-200">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center gap-3">
            <h3 className="text-lg font-semibold text-gray-900">Generated Files</h3>
            
            {/* Google Drive Status */}
            {driveStatus && (
              <div className="flex items-center gap-2">
                {driveStatus.enabled ? (
                  <div className="flex items-center gap-1 text-sm">
                    <Cloud className="w-4 h-4 text-green-500" />
                    <span className="text-green-600">Drive Connected</span>
                    {driveStatus.folder_url && (
                      <a
                        href={driveStatus.folder_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-500 hover:text-blue-700"
                        title="Open in Google Drive"
                      >
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </div>
                ) : (
                  <div className="flex items-center gap-1 text-sm text-gray-500">
                    <CloudOff className="w-4 h-4" />
                    <span>Drive Disabled</span>
                  </div>
                )}
              </div>
            )}
          </div>
          
          <div className="flex flex-col sm:flex-row gap-2">
            {/* Google Drive Actions */}
            {driveStatus?.enabled && (
              <div className="flex gap-2">
                <button
                  onClick={handleSyncToDrive}
                  disabled={syncing}
                  className="flex items-center gap-1 px-3 py-2 text-sm bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
                  {syncing ? 'Syncing...' : 'Sync to Drive'}
                </button>
                
                <button
                  onClick={() => setShowDriveDetails(!showDriveDetails)}
                  className="px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Drive Details
                </button>
              </div>
            )}
            {/* Category Filter */}
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {categories.map(category => (
                <option key={category} value={category}>
                  {category === 'all' ? 'All Categories' : category.charAt(0).toUpperCase() + category.slice(1)}
                </option>
              ))}
            </select>
            
            {/* Sort Options */}
            <select
              value={`${sortBy}-${sortOrder}`}
              onChange={(e) => {
                const [field, order] = e.target.value.split('-');
                setSortBy(field as 'name' | 'date' | 'size');
                setSortOrder(order as 'asc' | 'desc');
              }}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="date-desc">Newest First</option>
              <option value="date-asc">Oldest First</option>
              <option value="name-asc">Name A-Z</option>
              <option value="name-desc">Name Z-A</option>
              <option value="size-desc">Largest First</option>
              <option value="size-asc">Smallest First</option>
            </select>
          </div>
        </div>
      </div>

      <div className="p-4">
        {filteredFiles.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <File className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>No files found</p>
            <p className="text-sm">Files will appear here when agents generate outputs</p>
          </div>
        ) : (
          <div className="grid gap-3">
            {filteredFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center space-x-3 flex-1 min-w-0">
                  {getFileIcon(file.filename, file.category)}
                  
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {file.filename}
                    </p>
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <span className="capitalize">{file.category}</span>
                      <span>{formatFileSize(file.size)}</span>
                      <span>{formatDate(file.created_at)}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handlePreview(file)}
                    className="p-2 text-gray-400 hover:text-blue-500 hover:bg-blue-50 rounded-md transition-colors"
                    title="Preview file"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  
                  <button
                    onClick={() => handleDownload(file)}
                    className="p-2 text-gray-400 hover:text-green-500 hover:bg-green-50 rounded-md transition-colors"
                    title="Download file"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {filteredFiles.length > 0 && (
        <div className="px-4 py-3 border-t border-gray-200 bg-gray-50 text-sm text-gray-600">
          Showing {filteredFiles.length} of {files.length} files
        </div>
      )}
    </div>
  );
};

export default FileViewer;