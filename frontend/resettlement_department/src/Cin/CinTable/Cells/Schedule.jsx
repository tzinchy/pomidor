import { useState, useCallback } from 'react';

export default function Schedule({ props, column, type=null }) {
  const [value, setValue] = useState((type === 'cin' ? props.cin_schedule : props.dep_schedule) || '');
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState('');

  const handleEditClick = useCallback(() => {
    setEditValue(value);
    setIsEditing(true);
  }, [value]);

  const handleSave = useCallback(() => {
    setValue(editValue);
    setIsEditing(false);
    // Здесь можно добавить логику сохранения данных
  }, [editValue]);

  const handleCancel = useCallback(() => {
    setIsEditing(false);
  }, []);

  // Получаем размер колонки из пропсов
  const columnWidth = column?.getSize() || 'auto';

  return (
    <div 
      className="flex items-center justify-between gap-2 relative"
      style={{ width: columnWidth, maxWidth: columnWidth }}
    >
      <div className="flex-1 overflow-hidden">
        <div className="truncate">
          {value || 'Не указано'}
        </div>
      </div>

      <button
        onClick={handleEditClick}
        className="flex-shrink-0 p-1 text-gray-400 hover:text-blue-500 transition-colors"
        aria-label="Редактировать"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-5 w-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
          />
        </svg>
      </button>

      {/* Модальное окно редактирования */}
      {isEditing && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          onClick={handleCancel}
        >
          <div 
            className="bg-white rounded-lg p-6 w-full max-w-md"
            onClick={e => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium">Редактирование</h3>
              <button 
                onClick={handleCancel}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                &times;
              </button>
            </div>

            <div className="mb-6">
              <textarea
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                className="w-full border rounded px-3 py-2 min-h-[100px]"
                placeholder="Введите новое значение"
              />
            </div>

            <div className="flex space-x-2">
              <button
                onClick={handleCancel}
                className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 py-2 px-4 rounded transition-colors"
              >
                Отмена
              </button>
              <button
                onClick={handleSave}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded transition-colors"
              >
                Сохранить
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}