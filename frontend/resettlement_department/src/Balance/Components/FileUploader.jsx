import React, { useState } from 'react';
import { HOSTLINK } from '../..';

const FileUploader = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = async (e) => {
    const selectedFile = e.target.files[0];

    if (!selectedFile) return;

    // Проверяем, что файл имеет допустимый тип
    const isValid = selectedFile.type === 'application/vnd.ms-excel' ||
                    selectedFile.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';

    if (!isValid) {
      setError('Можно загружать только Excel-файлы (.xls, .xlsx).');
      setFile(null);
      return;
    }

    setFile(selectedFile);
    setError(null);
    
    // Загружаем файл сразу после выбора
    await handleUpload(selectedFile);
  };

  const handleUpload = async (selectedFile) => {
    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`${HOSTLINK}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Ошибка при загрузке файла');
      }

      const result = await response.json();
      console.log('Файл успешно загружен:', result);
      setFile(null); // Очищаем файл после успешной загрузки
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
          onChange={handleFileChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          accept=".xls,.xlsx,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
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
            <span className="font-medium text-blue-600">Нажмите чтобы загрузить</span> или перетащите файл
          </p>
          <p className="text-xs text-gray-500">Поддерживаются только Excel-файлы (.xls, .xlsx)</p>
        </div>
      </div>

      {file && (
        <div className="mt-4 space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="font-medium">Выбранный файл:</h3>
            <button
              onClick={() => setFile(null)}
              className="text-red-600 hover:text-red-700 text-sm"
            >
              Удалить
            </button>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span className="truncate mr-2">{file.name}</span>
            <span className="text-xs text-gray-500">
              {formatFileSize(file.size)}
            </span>
          </div>
        </div>
      )}

      {uploading && (
        <div className="mt-4 text-blue-600 text-sm">
          Загрузка...
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
