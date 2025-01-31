import React, { useState, useMemo, useRef, useEffect } from 'react';
import { useDropdown } from './DropdownContext';
import { HOSTLINK } from '../../index';

export default function DropdownButton({ placeholder = "Выберите адрес", id, type }) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [localSelectedItems, setLocalSelectedItems] = useState(new Set());
  const [addresses, setAddresses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const dropdownRef = useRef(null);
  const { updateSelectedItems } = useDropdown();

  // Загрузка данных
  useEffect(() => {
    const fetchAddresses = async () => {
      try {
        const response = await fetch(`${HOSTLINK}/fisrt_matching/${type}/house_addresses`);
        if (!response.ok) throw new Error('Ошибка загрузки адресов');
        const data = await response.json();
        
        // Преобразуем данные в массив объектов
        const formattedData = data.map(([address, info], index) => ({
          id: index,
          address,
          info
        }));
        
        setAddresses(formattedData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchAddresses();
  }, []);

  // Фильтрация элементов
  const filteredItems = useMemo(() => {
    if (!Array.isArray(addresses)) return [];
    return addresses.filter(item =>
      item.address.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [addresses, searchQuery]);

  // Обработчик выбора элемента
  const handleItemToggle = (itemId) => {
    setLocalSelectedItems(prev => {
      const newSet = new Set(prev);
      newSet.has(itemId) ? newSet.delete(itemId) : newSet.add(itemId);
      updateSelectedItems(
        id, 
        Array.from(newSet).map(id => addresses.find(item => item.id === id))
      );
      return newSet;
    });
  };

  // Выбор/снятие всех элементов
  const toggleAll = () => {
    const allFilteredIds = new Set(filteredItems.map(item => item.id));
    setLocalSelectedItems(prev => {
      const newSet = prev.size === allFilteredIds.size ? new Set() : allFilteredIds;
      updateSelectedItems(
        id,
        Array.from(newSet).map(id => addresses.find(item => item.id === id))
      );
      return newSet;
    });
  };

  // Остальной код без изменений
  // ... (handleClickOutside, rendering)

  return (
    <div className="relative w-[40%]" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-2 text-left bg-white border rounded-md shadow-sm hover:bg-gray-50 flex justify-between items-center"
      >
        <span>
          {localSelectedItems.size > 0 
            ? `${localSelectedItems.size} выбрано` 
            : placeholder}
        </span>
        <svg 
          className={`w-5 h-5 transform transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute z-10 w-full mt-1 bg-white border rounded-md shadow-lg">
          <div className="p-2 border-b">
            <input
              type="text"
              placeholder="Поиск..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-2 py-1 border rounded-md focus:outline-none focus:ring-2"
            />
          </div>

          <div className="max-h-60 overflow-y-auto">
            <label className="flex items-center px-4 py-2 hover:bg-gray-100 cursor-pointer border-b">
              <input
                type="checkbox"
                checked={localSelectedItems.size === filteredItems.length && filteredItems.length > 0}
                onChange={toggleAll}
                className="mr-2 rounded"
              />
              <span className="text-sm font-medium">Выбрать все</span>
            </label>

            {filteredItems.map(item => (
              <label 
                key={item.id}
                className="flex items-center px-4 py-2 hover:bg-gray-100 cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={localSelectedItems.has(item.id)}
                  onChange={() => handleItemToggle(item.id)}
                  className="mr-2 rounded"
                />
                <span className="text-sm">{item.address}<br/><span className='text-gray-400'>{item.info}</span></span>
              </label>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};