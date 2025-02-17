import React, { useState } from 'react';
import { useDropdown } from './DropdownContext';
import { HOSTLINK } from '../..';

const SubmitButton = ({ onResponse, type }) => {
  const { selectedItems } = useDropdown();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    try {
      setLoading(true);
      
      const requestBody = {
        "old_apartment_district": [],
        "old_apartment_municipal_district": [],
        "old_apartment_house_address": [],
        "new_apartment_district": [],
        "new_apartment_municipal_district": [],
        "new_apartment_house_address": [],
        "is_date": type == 'last' ? true : false
      };
      
      // Проходим по выбранным элементам и добавляем только адреса в соответствующие массивы
      Object.keys(selectedItems).forEach(dropdownId => {
        const addresses = selectedItems[dropdownId].map(item => item.address); // Получаем только адреса
      
        if (dropdownId.includes('family_structure_district')) {
          requestBody["family_structure_district"] = [];
        } else if (dropdownId.includes('family_structure_municipal_district')) {
          requestBody["family_structure_municipal_district"] = [];
        } else if (dropdownId.includes('family_structure_house_address')) {
          requestBody["family_structure_house_address"] = [...requestBody["family_structure_house_address"], ...addresses];
        } else if (dropdownId.includes('new_apartment_district')) {
          requestBody["new_apartment_district"] = [];
        } else if (dropdownId.includes('new_apartment_municipal_district')) {
          requestBody["new_apartment_municipal_district"] = [];
        } else if (dropdownId.includes('new_apartment_house_address')) {
          requestBody["new_apartment_house_address"] = [...requestBody["new_apartment_house_address"], ...addresses];
        }
      });
      
      console.log(requestBody);
      
      const response = await fetch(`${HOSTLINK}/fisrt_matching/matching`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

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
        {loading ? 'Отправка данных...' : (type == 'last' ? 'Подобрать последнее' : 'Подобрать данные')}
      </button>
    </div>
  );
};

export default SubmitButton;