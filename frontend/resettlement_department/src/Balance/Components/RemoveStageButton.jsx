import React from 'react';
import { useDropdown } from './DropdownContext';

const RemoveStageButton = ({ stageId, onRemove }) => {
  const { removeSelectedItems, selectedItems, updateSelectedItems } = useDropdown();

  const handleRemove = () => {
    // 1. Удаляем данные текущего этапа
    removeSelectedItems(`old_apartment_house_address_${stageId}`);
    removeSelectedItems(`new_apartment_house_address_${stageId}`);

    // 2. Вызываем колбэк для удаления этапа из UI
    onRemove(stageId);

    // 3. Перенумеровываем оставшиеся данные в контексте
    const remainingData = Object.entries(selectedItems)
      .filter(([key]) => !key.includes(stageId))
      .sort(([keyA], [keyB]) => {
        const numA = parseInt(keyA.match(/\d+/)[0]);
        const numB = parseInt(keyB.match(/\d+/)[0]);
        return numA - numB;
      });

    // 4. Очищаем контекст
    Object.keys(selectedItems).forEach(key => removeSelectedItems(key));

    // 5. Добавляем данные с новыми индексами
    let newIndex = 1;
    const tempData = {};

    remainingData.forEach(([key, value]) => {
      const newKey = key.includes('old_apartment') 
        ? `old_apartment_house_address_${newIndex}`
        : `new_apartment_house_address_${newIndex}`;
      
      tempData[newKey] = value;
      
      if (key.includes('new_apartment')) {
        newIndex++;
      }
    });

    Object.entries(tempData).forEach(([key, value]) => {
      updateSelectedItems(key, value);
    });
  };

  return (
    <button 
      onClick={handleRemove}
      className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
    >
      Удалить
    </button>
  );
};

export default RemoveStageButton;