import React from 'react';
import { useDropdown } from './DropdownContext';

const SubmitButton = () => {
  const { selectedItems } = useDropdown();

  const handleClick = () => {
    console.log("Выбранные элементы:", selectedItems);
  };

  return (
    <button
      onClick={handleClick}
      className="mt-4 px-4 py-2 border rounded-md hover:bg-gray-50"
    >
      Подобрать данные
    </button>
  );
};

export default SubmitButton;