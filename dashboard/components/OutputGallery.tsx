import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Code, 
  BarChart3, 
  Image, 
  File, 
  Download, 
  Eye, 
  Calendar,
  User,
  Folder
} from 'lucide-react';

interface FileRecord {
  filename: string;
  category: string;
  path: string;
  size: number;
  created_at: string;
  modified_at: string;
  created_by?: string;
}

interface OutputGalleryProps {
  sessionId?: string;
  viewMode?: 'grid' | 'list';
  showDepartmentFilter?: boolean;
}

const OutputGallery: React.FC<OutputGalleryProps> = ({
  sessionId,
  viewMode = 'grid',
  showDepartmentFilter = true
}) => {
  const [files, setFiles] = useState<FileRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedDepartment, setSelectedDepartment] = useState<string>('all');
  const [previewFile, setPreviewFile] = useState<FileRecord | null>(null);

  const categories = ['all', 'docs', 'code', 'designs', 'reports', 'data'];
  const departments = ['all', 'R&D', 'Marketing', 'Finance', 'Engineering', 'Sales', 'Security'];

  useEffect(() => {
    fetchFiles();
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

  const getFileIcon = (filename: string, category: string, size: 'sm' | 'lg' = 'sm') => {
    const ext = filename.split('.').pop()?.toLowerCase();
    const iconSize = size === 'lg' ? 'w-8 h-8' : 'w-5 h-5';
    
    if (category === 'code' || ['js', 'ts', 'py', 'html', 'css', 'json'].includes(ext || '')) {
      return <Code className={`${iconSize} text-blue-500`} />;
    }
    if (['jpg', 'jpeg', 'png', 'gif', 'svg'].includes(ext || '')) {
      return <Image className={`${iconSize} text-green-500`} />;
    }
    if (['xlsx', 'csv'].includes(ext || '')) {
      return <BarChart3 className={`${iconSize} text-emerald-500`} />;
    }
    if (['docx', 'pdf', 'txt', 'pptx'].includes(ext || '')) {
      return <FileText className={`${iconSize} text-red-500`} />;
    }
    return <File className={`${iconSize} text-gray-500`} />;
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      docs: 'bg-blue-100 text-blue-800',
      code: 'bg-green-100 text-green-800',
      designs: 'bg-purple-100 text-purple-800',
      reports: 'bg-orange-100 text-orange-800',
      data: 'bg-gray-100 text-gray-800'
    };
    return colors[category as keyof typeof colors] || 'bg-gray-100 text-gray-800';
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
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

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

  const filteredFiles = files.filter(file => {
    const categoryMatch = selectedCategory === 'all' || file.category === selectedCategory;
    const departmentMatch = selectedDepartment === 'all' || 
      (file.created_by && file.created_by.toLowerCase().includes(selectedDepartment.toLowerCase()));
    return categoryMatch && departmentMatch;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span className="ml-2 text-gray-600">Loading outputs...</span>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-4 border-b border-gray-200">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <h3 className="text-lg font-semibold text-gray-900">Output Gallery</h3>
          
          <div className="flex flex-col sm:flex-row gap-2">
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
            
            {/* Department Filter */}
            {showDepartmentFilter && (
              <select
                value={selectedDepartment}
                onChange={(e) => setSelectedDepartment(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {departments.map(dept => (
                  <option key={dept} value={dept}>
                    {dept === 'all' ? 'All Departments' : dept}
                  </option>
                ))}
              </select>
            )}
          </div>
        </div>
      </div>

      <div className="p-4">
        {filteredFiles.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Folder className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p className="text-lg font-medium">No outputs found</p>
            <p className="text-sm">Generated files will appear here when agents complete tasks</p>
          </div>
        ) : (
          <>
            {viewMode === 'grid' ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {filteredFiles.map((file, index) => (
                  <div
                    key={index}
                    className="group relative bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all duration-200 hover:border-gray-300"
                  >
                    {/* File Icon and Category Badge */}
                    <div className="flex items-start justify-between mb-3">
                      {getFileIcon(file.filename, file.category, 'lg')}
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(file.category)}`}>
                        {file.category}
                      </span>
                    </div>
                    
                    {/* File Name */}
                    <h4 className="text-sm font-medium text-gray-900 mb-2 line-clamp-2 group-hover:text-blue-600">
                      {file.filename}
                    </h4>
                    
                    {/* File Details */}
                    <div className="space-y-1 text-xs text-gray-500 mb-3">
                      <div className="flex items-center space-x-1">
                        <Calendar className="w-3 h-3" />
                        <span>{formatDate(file.created_at)}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <File className="w-3 h-3" />
                        <span>{formatFileSize(file.size)}</span>
                      </div>
                      {file.created_by && (
                        <div className="flex items-center space-x-1">
                          <User className="w-3 h-3" />
                          <span className="truncate">{file.created_by}</span>
                        </div>
                      )}
                    </div>
                    
                    {/* Action Buttons */}
                    <div className="flex items-center justify-end space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => setPreviewFile(file)}
                        className="p-1.5 text-gray-400 hover:text-blue-500 hover:bg-blue-50 rounded-md transition-colors"
                        title="Preview"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDownload(file)}
                        className="p-1.5 text-gray-400 hover:text-green-500 hover:bg-green-50 rounded-md transition-colors"
                        title="Download"
                      >
                        <Download className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-2">
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
                          <span className={`px-2 py-1 rounded-full ${getCategoryColor(file.category)}`}>
                            {file.category}
                          </span>
                          <span>{formatFileSize(file.size)}</span>
                          <span>{formatDate(file.created_at)}</span>
                          {file.created_by && <span>{file.created_by}</span>}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => setPreviewFile(file)}
                        className="p-2 text-gray-400 hover:text-blue-500 hover:bg-blue-50 rounded-md transition-colors"
                        title="Preview"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDownload(file)}
                        className="p-2 text-gray-400 hover:text-green-500 hover:bg-green-50 rounded-md transition-colors"
                        title="Download"
                      >
                        <Download className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
      
      {filteredFiles.length > 0 && (
        <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <span>Showing {filteredFiles.length} of {files.length} files</span>
            <div className="flex items-center space-x-4">
              <span>Total size: {formatFileSize(filteredFiles.reduce((sum, file) => sum + file.size, 0))}</span>
            </div>
          </div>
        </div>
      )}

      {/* File Preview Modal */}
      {previewFile && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <div className="flex items-center space-x-3">
                {getFileIcon(previewFile.filename, previewFile.category)}
                <div>
                  <h3 className="text-lg font-medium text-gray-900">{previewFile.filename}</h3>
                  <p className="text-sm text-gray-500">
                    {formatFileSize(previewFile.size)} • {formatDate(previewFile.created_at)}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setPreviewFile(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="p-4">
              <div className="text-center py-8 text-gray-500">
                <File className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                <p>File preview not available</p>
                <p className="text-sm">Click download to view the file</p>
                <button
                  onClick={() => handleDownload(previewFile)}
                  className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
                >
                  Download File
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OutputGallery;