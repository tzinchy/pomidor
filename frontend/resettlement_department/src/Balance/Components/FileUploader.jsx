import React, { useState, useRef } from 'react';
import { HOSTLINK } from '../..';

const FileUploader = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = async (e) => {
    const selectedFile = e.target.files[0];
    setUploadSuccess(false);
    setError(null);

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
    await handleUpload(selectedFile);
  };

  const handleUpload = async (selectedFile) => {
    setUploading(true);
    setError(null);
    setUploadSuccess(false);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`${HOSTLINK}/fisrt_matching/upload-file/`, {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      
      if (!response.ok) {
        throw new Error(result.message || 'Ошибка при загрузке файла');
      }

      console.log('Файл успешно загружен:', result);
      setUploadSuccess(true);
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = ''; // Сбрасываем значение input
      }
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
          ref={fileInputRef}
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
              onClick={() => {
                setFile(null);
                setUploadSuccess(false);
                if (fileInputRef.current) fileInputRef.current.value = '';
              }}
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
        <div className="mt-4 text-blue-600 text-sm flex items-center">
          <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Загрузка...
        </div>
      )}

      {error && (
        <div className="mt-4 p-3 bg-red-50 text-red-600 text-sm rounded-lg flex items-center">
          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          {error}
        </div>
      )}

      {uploadSuccess && (
        <div className="mt-4 p-3 bg-green-50 text-green-600 text-sm rounded-lg flex items-center">
          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          Файл успешно загружен!
        </div>
      )}
    </div>
  );
};

export default FileUploader;