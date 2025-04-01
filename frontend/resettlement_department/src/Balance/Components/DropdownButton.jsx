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
  const [apartmentRanges, setApartmentRanges] = useState({});
  const [expandedItems, setExpandedItems] = useState(new Set());
  const [selectedSections, setSelectedSections] = useState({});
  const dropdownRef = useRef(null);
  const { updateSelectedItems } = useDropdown();

  // Загрузка данных
  useEffect(() => {
    const fetchAddresses = async () => {
      try {
        const response = await fetch(`${HOSTLINK}/fisrt_matching/${type}/house_addresses`);
        if (!response.ok) throw new Error('Ошибка загрузки адресов');
        const data = await response.json();
        
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
  }, [type]);

  // Фильтрация элементов
  const filteredItems = useMemo(() => {
    if (!Array.isArray(addresses)) return [];
    return addresses.filter(item =>
      item.address.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [addresses, searchQuery]);

  // Добавление нового диапазона квартир
  const addApartmentRange = (itemId) => {
    setApartmentRanges(prev => ({
      ...prev,
      [itemId]: [
        ...(prev[itemId] || []),
        { from: '', to: '' }
      ]
    }));
  };

  // Удаление диапазона квартир
  const removeApartmentRange = (itemId, rangeIndex) => {
    setApartmentRanges(prev => {
      const newRanges = { ...prev };
      if (newRanges[itemId]) {
        newRanges[itemId] = newRanges[itemId].filter((_, idx) => idx !== rangeIndex);
        if (newRanges[itemId].length === 0) {
          delete newRanges[itemId];
        }
      }
      return newRanges;
    });
  };

  // Обновление диапазона квартир
  const updateApartmentRange = (itemId, rangeIndex, field, value) => {
    setApartmentRanges(prev => {
      const newRanges = { ...prev };
      if (!newRanges[itemId]) newRanges[itemId] = [];
      newRanges[itemId][rangeIndex][field] = value;
      return newRanges;
    });
  };

  // Обработчик выбора секции
  const toggleSectionSelection = (itemId, section) => {
    setSelectedSections(prev => {
      const newSelection = { ...prev };
      if (!newSelection[itemId]) {
        newSelection[itemId] = new Set();
      }
      
      if (newSelection[itemId].has(section)) {
        newSelection[itemId].delete(section);
        if (newSelection[itemId].size === 0) {
          delete newSelection[itemId];
        }
      } else {
        newSelection[itemId].add(section);
      }
      
      return newSelection;
    });
  };

  // Проверка выбрана ли секция
  const isSectionSelected = (itemId, section) => {
    return selectedSections[itemId]?.has(section) || false;
  };

  // Переключение видимости диапазонов для адреса
  const toggleRangeVisibility = (itemId, e) => {
    e.stopPropagation();
    setExpandedItems(prev => {
      const newSet = new Set(prev);
      newSet.has(itemId) ? newSet.delete(itemId) : newSet.add(itemId);
      return newSet;
    });
  };

  // Обработчик выбора элемента
  const handleItemToggle = (itemId) => {
    setLocalSelectedItems(prev => {
      const newSet = new Set(prev);
      
      if (type === 'new_apartment') {
        if (newSet.has(itemId)) {
          newSet.delete(itemId);
          setExpandedItems(prev => {
            const newExpanded = new Set(prev);
            newExpanded.delete(itemId);
            return newExpanded;
          });
        } else {
          newSet.add(itemId);
          if (!apartmentRanges[itemId]) {
            addApartmentRange(itemId);
          }
        }
      } else {
        newSet.has(itemId) ? newSet.delete(itemId) : newSet.add(itemId);
      }

      // Обновляем выбранные элементы
      const selectedItems = Array.from(newSet).map(id => {
        const item = addresses.find(item => item.id === id);
        return {
          ...item,
          apartmentRanges: apartmentRanges[id] || [],
          selectedSections: selectedSections[id] ? Array.from(selectedSections[id]) : []
        };
      });

      updateSelectedItems(id, selectedItems);
      return newSet;
    });
  };

  // Выбор/снятие всех элементов
  const toggleAll = () => {
    const allFilteredIds = new Set(filteredItems.map(item => item.id));
    setLocalSelectedItems(prev => {
      const newSet = prev.size === allFilteredIds.size ? new Set() : allFilteredIds;
      
      const selectedItems = Array.from(newSet).map(id => {
        const item = addresses.find(item => item.id === id);
        return {
          ...item,
          apartmentRanges: apartmentRanges[id] || [],
          selectedSections: selectedSections[id] ? Array.from(selectedSections[id]) : []
        };
      });

      updateSelectedItems(id, selectedItems);
      return newSet;
    });
  };

  // Секции для выбора
  const sections = ['A', 'B', 'C', 'D', 'E', 'F'];

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
              <div key={item.id}>
                <div className="flex items-center px-4 py-2 hover:bg-gray-100 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={localSelectedItems.has(item.id)}
                    onChange={() => handleItemToggle(item.id)}
                    className="mr-2 rounded"
                  />
                  <span className="text-sm flex-grow">{item.address}<br/><span className='text-gray-400'>{item.info}</span></span>
                  
                  {type === 'new_apartment' && localSelectedItems.has(item.id) && (
                    <button 
                      onClick={(e) => toggleRangeVisibility(item.id, e)}
                      className="ml-2 focus:outline-none"
                    >
                      <svg
                        className={`w-4 h-4 transform transition-transform ${expandedItems.has(item.id) ? 'rotate-180' : ''}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                  )}
                </div>

                {type === 'new_apartment' && expandedItems.has(item.id) && (
                  <div className="px-4 py-2 bg-gray-50 border-t">
                    {/* Блок с выбором секций */}
                    <div className="mb-3">
                      <p className="text-sm text-gray-600 mb-1">Выберите секции:</p>
                      <div className="flex flex-wrap gap-2">
                        {sections.map(section => (
                          <button
                            key={section}
                            onClick={() => toggleSectionSelection(item.id, section)}
                            className={`w-8 h-8 flex items-center justify-center border rounded-md transition-colors
                              ${isSectionSelected(item.id, section) 
                                ? 'bg-blue-500 text-white border-blue-600' 
                                : 'bg-white hover:bg-gray-100 border-gray-300'}`}
                          >
                            {section}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Блок с диапазонами квартир */}
                    <div className="mb-2">
                      <p className="text-sm text-gray-600 mb-1">Укажите диапазоны квартир:</p>
                      {apartmentRanges[item.id]?.map((range, rangeIndex) => (
                        <div key={rangeIndex} className="flex items-center mb-2">
                          <input
                            type="text"
                            placeholder="От"
                            value={range.from}
                            onChange={(e) => updateApartmentRange(item.id, rangeIndex, 'from', e.target.value)}
                            className="w-20 px-2 py-1 border rounded-md mr-2 focus:ring-1 focus:ring-blue-300 focus:border-blue-300"
                          />
                          <span className="mr-2 text-gray-500">—</span>
                          <input
                            type="text"
                            placeholder="До"
                            value={range.to}
                            onChange={(e) => updateApartmentRange(item.id, rangeIndex, 'to', e.target.value)}
                            className="w-20 px-2 py-1 border rounded-md mr-2 focus:ring-1 focus:ring-blue-300 focus:border-blue-300"
                          />
                          <button
                            onClick={() => removeApartmentRange(item.id, rangeIndex)}
                            className="px-2 py-1 border border-dashed border-gray-300 text-gray-500 rounded-md hover:bg-red-50 hover:text-red-500 hover:border-red-300 transition-colors"
                          >
                            Удалить
                          </button>
                        </div>
                      ))}
                    </div>

                    {/* Кнопка добавления нового диапазона */}
                    <button
                      onClick={() => addApartmentRange(item.id)}
                      className="px-3 py-1 text-sm border border-dashed border-gray-300 text-gray-500 rounded-md hover:bg-blue-50 hover:text-blue-500 hover:border-blue-300 transition-colors"
                    >
                      + Добавить диапазон
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}