import React, { useState, useMemo, useRef, useEffect } from 'react';
import { useDropdown } from './DropdownContext';

const DropdownButton = ({ 
  items = [], // Теперь это массив строк
  placeholder = "Выберите элементы",
  id // Уникальный идентификатор для каждого DropdownButton
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [localSelectedItems, setLocalSelectedItems] = useState(new Set());
  const dropdownRef = useRef(null);
  const { updateSelectedItems } = useDropdown();

  // Фильтрация элементов
  const filteredItems = useMemo(() => {
    if (!Array.isArray(items)) return [];
    return items.filter(item =>
      item.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [items, searchQuery]);

  // Обработчик выбора элемента
  const handleItemToggle = (item) => {
    setLocalSelectedItems(prev => {
      const newSet = new Set(prev);
      newSet.has(item) ? newSet.delete(item) : newSet.add(item);
      updateSelectedItems(id, Array.from(newSet)); // Обновляем контекст
      return newSet;
    });
  };

  // Выбор/снятие всех элементов
  const toggleAll = () => {
    const allFilteredItems = new Set(filteredItems);
    setLocalSelectedItems(prev => {
      const newSet = prev.size === allFilteredItems.size ? new Set() : allFilteredItems;
      updateSelectedItems(id, Array.from(newSet)); // Обновляем контекст
      return newSet;
    });
  };

  // Закрытие при клике вне компонента
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Кнопка */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-2 text-left bg-white border rounded-md shadow-sm hover:bg-gray-50  flex justify-between items-center"
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

      {/* Выпадающий список */}
      {isOpen && (
        <div className="absolute z-10 w-full mt-1 bg-white border rounded-md shadow-lg">
          {/* Поиск */}
          <div className="p-2 border-b">
            <input
              type="text"
              placeholder="Поиск..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-2 py-1 border rounded-md focus:outline-none focus:ring-2"
            />
          </div>

          {/* Список элементов */}
          <div className="max-h-60 overflow-y-auto">
            {/* Выбрать все */}
            <label className="flex items-center px-4 py-2 hover:bg-gray-100 cursor-pointer border-b">
              <input
                type="checkbox"
                checked={localSelectedItems.size === filteredItems.length && filteredItems.length > 0}
                onChange={toggleAll}
                className="mr-2 rounded"
              />
              <span className="text-sm font-medium">Выбрать все</span>
            </label>

            {/* Элементы списка */}
            {filteredItems.map((item, index) => (
              <label 
                key={index} // Используем индекс как ключ, так как строки могут повторяться
                className="flex items-center px-4 py-2 hover:bg-gray-100 cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={localSelectedItems.has(item)}
                  onChange={() => handleItemToggle(item)}
                  className="mr-2 rounded"
                />
                <span className="text-sm">{item}</span>
              </label>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DropdownButton;