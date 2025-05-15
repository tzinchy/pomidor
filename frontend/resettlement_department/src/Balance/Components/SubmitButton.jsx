import React, { useState } from 'react';
import { useDropdown } from './DropdownContext';
import { HOSTLINK } from '../..';

const SubmitButton = ({ onResponse, type }) => {
  const { selectedItems } = useDropdown();
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const handleSubmit = async () => {
    try {
      // Пропускаем проверку выбранных элементов только для type === 'last'
      if (type !== 'last') {
        const hasSelectedItems = Object.values(selectedItems).some(
          items => items && items.length > 0
        );
        
        if (!hasSelectedItems) {
          setErrorMessage('Пожалуйста, выберите хотя бы один пункт');
          return;
        }
      }
      
      setErrorMessage(null);
      setLoading(true);

       // Calculate total selected items
       const totalSelected = selectedItems["new_apartment_house_address_2"]

      const requestBody = {
        "old_apartment_house_address": [],
        "new_apartment_house_address": [],
        "is_date": type === 'last' ? true : false
      };
      
      // Добавляем адреса только если type не 'last' или есть выбранные элементы
      if (type !== 'last' || Object.values(selectedItems).some(items => items && items.length > 0)) {
        Object.keys(selectedItems).forEach(dropdownId => {
          const addresses = selectedItems[dropdownId].map(item => item.address);
          
          if (dropdownId.includes('old_apartment_house_address')) {
            requestBody["old_apartment_house_address"] = [...requestBody["old_apartment_house_address"], ...addresses];
          } else if (dropdownId.includes('new_apartment_house_address')) {
            requestBody["new_apartment_house_address"] = [...requestBody["new_apartment_house_address"], selectedItems["new_apartment_house_address_1"]];
          }
        });
      }
      console.log('selectedItems', selectedItems);
      
      const response = totalSelected ? (await fetch(`${HOSTLINK}/wave/process_waves`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(selectedItems)
      })) : (await fetch(`${HOSTLINK}/fisrt_matching/matching`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      }));

      if (!response.ok) {
        throw new Error(`Ошибка HTTP: ${response.status}`);
      }

      const result = await response.json();
      onResponse(result, null);
      
    } catch (err) {
      onResponse(null, err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="m-4">
      <button
        onClick={handleSubmit}
        disabled={loading}
        className={`px-4 py-2 border rounded-md ${
          loading 
            ? 'bg-gray-300 cursor-not-allowed' 
            : 'hover:bg-gray-50 bg-white'
        }`}
      >
        {loading ? 'Отправка данных...' : (type === 'last' ? 'Подобрать последнее' : 'Подобрать данные')}
      </button>
      {errorMessage && (
        <div className="mt-2 text-red-500 text-sm">
          {errorMessage}
        </div>
      )}
    </div>
  );
};

export default SubmitButton;