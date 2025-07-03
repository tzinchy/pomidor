import { useState, useCallback } from 'react';

export default function Schedule({ props, column, type=null }) {
  const [value, setValue] = useState((type === 'cin' ? props.cin_schedule : props.dep_schedule) || '');
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState('');

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
    </div>
  );
}