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
  const [expandedItems, setExpandedItems] = useState(new Set());
  const [availableSections, setAvailableSections] = useState({});
  const [selectedSections, setSelectedSections] = useState({});
  const [sectionRanges, setSectionRanges] = useState({});
  const dropdownRef = useRef(null);
  const { updateSelectedItems } = useDropdown();

  // Загрузка данных адресов
  useEffect(() => {
    const fetchAddresses = async () => {
      try {
        const response = await fetch(`${HOSTLINK}/fisrt_matching/${type}/house_addresses`);
        if (!response.ok) throw new Error('Ошибка загрузки адресов');
        const data = await response.json();
        
        const formattedData = data.map(([address, info], index) => ({
          id: index,
          address,
          info,
          originalData: { address, info }
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

  // Загрузка секций при выборе адреса
  const fetchSections = async (item) => {
    try {
      const response = await fetch(`${HOSTLINK}/tables/get_entrance_ranges?house_address=${encodeURIComponent(item.originalData.address)}`);
      if (!response.ok) throw new Error('Ошибка загрузки секций');
      const data = await response.json();
      
      // Преобразуем данные в формат { section: { min, max } }
      const sectionsData = {};
      for (const [section, range] of Object.entries(data)) {
        const [min, max] = range.split('-').map(Number);
        sectionsData[section] = { min, max };
      }
      
      setAvailableSections(prev => ({
        ...prev,
        [item.id]: sectionsData
      }));
      
      return sectionsData;
    } catch (err) {
      console.error('Ошибка при загрузке секций:', err);
      return {};
    }
  };

  // Фильтрация элементов
  const filteredItems = useMemo(() => {
    if (!Array.isArray(addresses)) return [];
    return addresses.filter(item =>
      item.address.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [addresses, searchQuery]);

  // Обработчик выбора секции с немедленным обновлением
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
        
        // Инициализируем диапазон, если его нет
        setSectionRanges(prevRanges => {
          const newRanges = { ...prevRanges };
          if (!newRanges[itemId]) newRanges[itemId] = {};
          if (!newRanges[itemId][section]) {
            newRanges[itemId][section] = {
              from: availableSections[itemId]?.[section]?.min || '',
              to: availableSections[itemId]?.[section]?.max || ''
            };
          }
          return newRanges;
        });
      }
      
      // Обновляем выбранные элементы сразу после изменения
      const selectedItems = Array.from(localSelectedItems).map(id => {
        const item = addresses.find(item => item.id === id);
        const sections = newSelection[id] ? Array.from(newSelection[id]) : [];
        const ranges = sectionRanges[id] || {};
        
        return {
          ...item,
          sections: sections.map(s => ({
            section: s,
            range: ranges[s] || {
              from: availableSections[id]?.[s]?.min || '',
              to: availableSections[id]?.[s]?.max || ''
            }
          }))
        };
      });
      
      console.log('selectedItems', selectedItems);
      updateSelectedItems(id, selectedItems);
      
      return newSelection;
    });
  };

  // Обновленный обработчик изменения диапазона
const updateSectionRange = (itemId, section, field, value) => {
  setSectionRanges(prev => {
    const newRanges = { ...prev };
    if (!newRanges[itemId]) newRanges[itemId] = {};
    if (!newRanges[itemId][section]) {
      newRanges[itemId][section] = { 
        from: availableSections[itemId]?.[section]?.min || '',
        to: availableSections[itemId]?.[section]?.max || '' 
      };
    }
    newRanges[itemId][section][field] = value;
    
    // Немедленно обновляем выбранные элементы
    const selectedItems = Array.from(localSelectedItems).map(id => {
      const item = addresses.find(item => item.id === id);
      const sections = selectedSections[id] ? Array.from(selectedSections[id]) : [];
      const ranges = id === itemId ? newRanges[id] : sectionRanges[id] || {};
      
      return {
        ...item,
        sections: sections.map(s => ({
          section: s,
          range: ranges[s] || {
            from: availableSections[id]?.[s]?.min || '',
            to: availableSections[id]?.[s]?.max || ''
          }
        }))
      };
    });
    
    updateSelectedItems(id, selectedItems);
    
    return newRanges;
  });
};

  // Обработчик выбора элемента
  const handleItemToggle = async (item) => {
    const itemId = item.id;
    setLocalSelectedItems(prev => {
      const newSet = new Set(prev);
      
      if (newSet.has(itemId)) {
        newSet.delete(itemId);
        setExpandedItems(prev => {
          const newExpanded = new Set(prev);
          newExpanded.delete(itemId);
          return newExpanded;
        });
      } else {
        newSet.add(itemId);
        // Загружаем секции при выборе адреса
        fetchSections(item);
      }

      // Обновляем выбранные элементы
      const selectedItems = Array.from(newSet).map(id => {
        const item = addresses.find(item => item.id === id);
        const sections = selectedSections[id] ? Array.from(selectedSections[id]) : [];
        const ranges = sectionRanges[id] || {};
        
        return {
          ...item,
          sections: sections.map(section => ({
            section,
            range: ranges[section] || [availableSections[id]?.[section]?.min || '', availableSections[id]?.[section]?.max || '']
          }))
        };
      });
      console.log('selectedItems', selectedItems);

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
        const sections = selectedSections[id] ? Array.from(selectedSections[id]) : [];
        const ranges = sectionRanges[id] || {};
        
        return {
          ...item,
          sections: sections.map(section => ({
            section,
            range: ranges[section] || {
              from: availableSections[id]?.[section]?.min || '',
              to: availableSections[id]?.[section]?.max || ''
            }
          }))
        };
      });

      updateSelectedItems(id, selectedItems);
      return newSet;
    });
  };

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
                    onChange={() => handleItemToggle(item)}
                    className="mr-2 rounded"
                  />
                  <span className="text-sm flex-grow">{item.address}<br/><span className='text-gray-400'>{item.info}</span></span>
                  
                  {type === 'new_apartment' && localSelectedItems.has(item.id) && (
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        setExpandedItems(prev => {
                          const newSet = new Set(prev);
                          newSet.has(item.id) ? newSet.delete(item.id) : newSet.add(item.id);
                          return newSet;
                        });
                      }}
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
                      <p className="text-sm text-gray-600 mb-2">Выберите секции:</p>
                      <div className="space-y-2">
                        {availableSections[item.id] ? (
                          Object.entries(availableSections[item.id]).map(([section, range]) => (
                            <div key={section} className="border rounded-md overflow-hidden">
                              <div 
                                className={`flex items-center px-3 py-2 cursor-pointer ${selectedSections[item.id]?.has(section) ? 'bg-blue-50' : 'bg-white'}`}
                                onClick={(e) => toggleSectionSelection(item.id, section)}
                              >
                                <span className={`w-6 h-6 flex items-center justify-center border rounded-md mr-2 ${selectedSections[item.id]?.has(section) ? 'bg-blue-500 text-white border-blue-600' : 'bg-white border-gray-300'}`}>
                                  {section === 'unknown' ? '-' : section}
                                </span>
                                <span className="text-sm">
                                  Квартиры: {range.min}-{range.max}
                                </span>
                              </div>
                              
                              {selectedSections[item.id]?.has(section) && (
                                <div className="px-3 py-2 bg-white border-t">
                                  <div className="flex items-center mb-2">
                                    <span className="text-sm text-gray-600 mr-2">Диапазон:</span>
                                    <input
                                      type="number"
                                      placeholder="От"
                                      value={sectionRanges[item.id]?.[section]?.from ?? range.min}
                                      onChange={(e) => updateSectionRange(item.id, section, 'from', e.target.value)}
                                      className="w-20 px-2 py-1 border rounded-md mr-2 focus:ring-1 focus:ring-blue-300 focus:border-blue-300"
                                      min={range.min}
                                      max={range.max}
                                    />
                                    <span className="mr-2 text-gray-500">—</span>
                                    <input
                                      type="number"
                                      placeholder="До"
                                      value={sectionRanges[item.id]?.[section]?.to ?? range.max}
                                      onChange={(e) => updateSectionRange(item.id, section, 'to', e.target.value)}
                                      className="w-20 px-2 py-1 border rounded-md focus:ring-1 focus:ring-blue-300 focus:border-blue-300"
                                      min={range.min}
                                      max={range.max}
                                    />
                                  </div>
                                </div>
                              )}
                            </div>
                          ))
                        ) : (
                          <p className="text-sm text-gray-400">Загрузка секций...</p>
                        )}
                      </div>
                    </div>
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