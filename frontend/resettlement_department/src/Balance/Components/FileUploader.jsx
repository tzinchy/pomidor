import React, { useState } from 'react';

const FileUploader = () => {
    const [files, setFiles] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState(null);
  
    const handleFileChange = (e) => {
      const selectedFiles = Array.from(e.target.files);
      setFiles(selectedFiles);
    };
  
    const handleRemoveFiles = () => {
      setFiles(null);
    };
  
    const handleUpload = async () => {
      if (!files || files.length === 0) {
        setError('Пожалуйста, выберите файлы для загрузки.');
        return;
      }
  
      setUploading(true);
      setError(null);
  
      const formData = new FormData();
      files.forEach((file) => {
        formData.append('files', file); // 'files' — это ключ, который сервер ожидает
      });
  
      try {
        const response = await fetch('http://localhost:5000/upload', {
          method: 'POST',
          body: formData,
        });
  
        if (!response.ok) {
          throw new Error('Ошибка при загрузке файлов');
        }
  
        const result = await response.json();
        console.log('Файлы успешно загружены:', result);
        setFiles(null); // Очищаем выбранные файлы после успешной загрузки
      } catch (err) {
        setError(err.message);
      } finally {
        setUploading(false);
      }
    };
  
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };
  
    return (
      <div className="max-w-md mx-auto p-6">
        <div className="relative border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors">
          <input
            type="file"
            multiple
            onChange={handleFileChange}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          
          <div className="flex flex-col items-center space-y-2">
            <svg
              className="w-12 h-12 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            <p className="text-gray-600">
              <span className="font-medium text-blue-600">Нажмите чтобы загрузить</span> или перетащите файлы
            </p>
          </div>
        </div>
  
        {files && (
          <div className="mt-4 space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="font-medium">Выбранные файлы:</h3>
              <button
                onClick={handleRemoveFiles}
                className="text-red-600 hover:text-red-700 text-sm"
              >
                Удалить все
              </button>
            </div>
            
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <span className="truncate mr-2">{file.name}</span>
                <span className="text-xs text-gray-500">
                  {formatFileSize(file.size)}
                </span>
              </div>
            ))}
  
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-blue-300"
            >
              {uploading ? 'Загрузка...' : 'Загрузить файлы'}
            </button>
          </div>
        )}
  
        {error && (
          <div className="mt-4 text-red-600 text-sm">
            {error}
          </div>
        )}
      </div>
    );
  };

export default FileUploader;