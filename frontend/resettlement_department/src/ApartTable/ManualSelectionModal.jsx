import React, { useMemo, useState, useEffect, useCallback } from "react";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  flexRender
} from "@tanstack/react-table";
import { HOSTLINK } from "..";
import AdressCell from "./Cells/AdressCell";
import PloshCell from "./Cells/PloshCell";
import TryFilters from "./Filters/TryFilters";

export default function ManualSelectionModal({ isOpen, onClose, apartmentId, fetchApartments, getFilteData, lastSelectedAddres, lastSelectedMunicipal }) {
  const [data, setData] = useState([]); // Состояние для данных таблицы
  const [filteredApartments, setFilteredApartments] = useState([]); // Отфильтрованные данные
  const [isLoading, setIsLoading] = useState(false); // Состояние для загрузки
  const [error, setError] = useState(null); // Состояние для ошибок
  const [rowSelection, setRowSelection] = useState({}); // Состояние для выбранных строк
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isFiltering, setIsFiltering] = useState(false); // Состояние для индикатора загрузки фильтрации
  const [filterWindow, setFilterWindow] = useState(false);
  const [filters, setFilters] = useState({}); // Состояние для фильтров
  const [filtersData, setFiltersData] = useState({}); // Состояние для фильтров
  const [filtersResetFlag, setFiltersResetFlag] = useState(false);
  const [firstMinArea, setFirstMinArea] = useState("");
  const [firstMaxArea, setFirstMaxArea] = useState("");
  const [secondMinArea, setSecondMinArea] = useState(""); 
  const [secondMaxArea, setSecondMaxArea] = useState(""); 
  const [thirdMinArea, setThirdMinArea] = useState(""); 
  const [thirdMaxArea, setThirdMaxArea] = useState(""); 
  const [minFloor, setMinFloor] = useState("");
  const [maxFloor, setMaxFloor] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  // Состояние для хранения выбранных фильтров
  const [selectedFilters, setSelectedFilters] = useState({
    district: [],
    municipal_district: [],
    house_address: []
  });

  const handleFilterChange = useCallback((filterType, selectedValues) => {
    setSelectedFilters(prev => ({
      ...prev,
      [filterType]: selectedValues
    }));
    
    setFilters(prevFilters => {
      if (selectedValues.length === 0) {
        const { [filterType]: _, ...rest } = prevFilters;
        return rest;
      }
      return {
        ...prevFilters,
        [filterType]: selectedValues,
      };
    });
  }, []);

  const handleResetFilters = () => {
    setSelectedFilters({
      district: [],
      municipal_district: [],
      house_address: []
    });
    setFilters({});
    setFiltersResetFlag(prev => !prev);
    // Сбрасываем все площади
    setFirstMinArea("");
    setFirstMaxArea("");
    setSecondMinArea("");
    setSecondMaxArea("");
    setThirdMinArea("");
    setThirdMaxArea("");
    setMinFloor("");
    setMaxFloor("");
    setSearchQuery("");
  };

  useEffect(() => {
    if (isOpen && apartmentId) {
      fetchData();
    }
  }, [isOpen, apartmentId]);

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
  
    try {
      const response = await fetch(
        `${HOSTLINK}/tables/apartment/${apartmentId}/void_aparts`, {credentials: "include"}
      );
  
      if (!response.ok) {
        throw new Error("Ошибка при загрузке данных");
      }
  
      const result = await response.json();
      setData(result);
      setFilteredApartments(result);
      setFiltersData(getFilteData(result));
      console.log(result);
    } catch (error) {
      console.error("Ошибка:", error);
      setError("Не удалось загрузить данные. Попробуйте снова.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      // Применяем поиск с задержкой
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  useEffect(() => {
    if (!data || data.length === 0) return;
  
    setIsFiltering(true);
    let filtered = data;
  
    // Фильтрация по searchQuery (apart_number)
    if (searchQuery) {
      filtered = filtered.filter((item) => {
        return String(item.apart_number || '')?.toLowerCase().includes(searchQuery.toLowerCase());
      });
    }
  
    // Фильтрация по full_living_area (firstMinArea/firstMaxArea)
    if (firstMinArea || firstMaxArea) {
      filtered = filtered.filter((item) => {
        const area = parseFloat(item.full_living_area);
        const min = parseFloat(firstMinArea);
        const max = parseFloat(firstMaxArea);
  
        let valid = true;
        if (!isNaN(min)) valid = valid && area >= min;
        if (!isNaN(max)) valid = valid && area <= max;
        return valid;
      });
    }
  
    // Фильтрация по total_living_area (secondMinArea/secondMaxArea)
    if (secondMinArea || secondMaxArea) {
      filtered = filtered.filter((item) => {
        const area = parseFloat(item.total_living_area);
        const min = parseFloat(secondMinArea);
        const max = parseFloat(secondMaxArea);
  
        let valid = true;
        if (!isNaN(min)) valid = valid && area >= min;
        if (!isNaN(max)) valid = valid && area <= max;
        return valid;
      });
    }
  
    // Фильтрация по living_area (thirdMinArea/thirdMaxArea)
    if (thirdMinArea || thirdMaxArea) {
      filtered = filtered.filter((item) => {
        const area = parseFloat(item.living_area);
        const min = parseFloat(thirdMinArea);
        const max = parseFloat(thirdMaxArea);
  
        let valid = true;
        if (!isNaN(min)) valid = valid && area >= min;
        if (!isNaN(max)) valid = valid && area <= max;
        return valid;
      });
    }

    // Фильтрация по этажу
    if (minFloor || maxFloor) {
      filtered = filtered.filter((item) => {
        const floor = parseFloat(item.floor);
        const min = parseFloat(minFloor);
        const max = parseFloat(maxFloor);
  
        let valid = true;
        if (!isNaN(min)) valid = valid && floor >= min;
        if (!isNaN(max)) valid = valid && floor <= max;
        return valid;
      });
    }
  
    // Фильтрация по выбранным значениям в dropdown
    Object.entries(filters).forEach(([filterType, selectedValues]) => {
      if (selectedValues.length > 0) {
        const filterKey = filterType.toLowerCase();
        filtered = filtered.filter((item) => {
          return selectedValues.some(val => item[filterKey] === val);
        });
      }
    });
  
    setFilteredApartments(filtered);
    setIsFiltering(false);
  }, [data, filters, firstMinArea, firstMaxArea, secondMinArea, secondMaxArea, thirdMinArea, thirdMaxArea, minFloor, maxFloor, searchQuery]);
  
  const isEmptyResults = !isLoading && !isFiltering && !error && filteredApartments.length === 0;

  // Колонки для таблицы
  const columns = useMemo(
    () => [
      {
        id: "select",
        header: ({ table }) => (
          <input
            type="checkbox"
            checked={table.getIsAllRowsSelected()}
            onChange={table.getToggleAllRowsSelectedHandler()}
            className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
          />
        ),
        cell: ({ row }) => (
          <input
            type="checkbox"
            checked={row.getIsSelected()}
            onChange={row.getToggleSelectedHandler()}
            className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
          />
        ),
        size: 10,
        enableSorting: false,
      },
      {
        header: "Адрес",
        accessorKey: "apart_number",
        enableSorting: true,
        cell: ({ row }) => <AdressCell props={row.original} />,
        size: 150, // Начальная ширина столбца
      },
      {
        header: '№ Кв.',
        accessorKey: 'apart_number',
        enableSorting: true,
        cell: ({ row }) => 
          <div className="text-xs">
            {row.original['apart_number']}
          </div>,
        size: 30,
      },
      {
        header: "Площадь, тип, этаж",
        accessorKey: "full_living_area",
        cell: ({ row }) => <PloshCell props={row.original} />,
        size: 100, // Начальная ширина столбца
      },
    ],
    []
  );

  // Создаем таблицу
  const table = useReactTable({
    data: filteredApartments,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      rowSelection, // Передаем состояние выбранных строк
    },
    onRowSelectionChange: setRowSelection, // Обновляем состояние при изменении
  });

  const handleManualMatching = async () => {
    if (!apartmentId) return;
  
    const selectedRows = table.getSelectedRowModel().rows;
    const selectedIds = selectedRows.map((row) => parseInt(row.original.new_apart_id)); // Преобразуем ID в числа
    console.log('selectedIds', selectedIds);
  
    if (selectedIds.length === 0) {
      alert("Выберите хотя бы одну строку");
      return;
    }
  
    setIsSubmitting(true);
    try {
      // Отправляем один запрос с массивом выбранных ID
      const response = await fetch(
        `${HOSTLINK}/tables/apartment/${apartmentId}/manual_matching?apart_type=OldApart`,
        {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            new_apart_ids: selectedIds, // Массив выбранных ID
            apart_type: "OldApart", // Или другое значение, в зависимости от логики
          }),
        }
      );
  
      if (!response.ok) {
        throw new Error("Ошибка при сопоставлении");
      }

      onClose(); // Закрываем модальное окно
    } catch (error) {
      console.error("Ошибка:", error);
      alert("Ошибка при сопоставлении");
    } finally {
      setIsSubmitting(false);
      setRowSelection({}); // Сбрасываем выбор
      fetchApartments(lastSelectedAddres, lastSelectedMunicipal);
    }
  };

  if (!isOpen) return null;

return (
  <div className="fixed inset-0 z-40 flex items-center justify-center bg-black bg-opacity-50">
    <div className="bg-gray-50 rounded-lg p-6 w-full max-w-6xl max-h-[90vh] flex flex-col">
      {/* Заголовок и кнопка закрытия */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Ручной подбор</h2>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-gray-700"
        >
          <span className="text-2xl">×</span>
        </button>
      </div>

      <div className="flex justify-between items-center mb-4">
        <button
          onClick={handleManualMatching}
          disabled={isSubmitting}
          className="bg-white border px-4 py-2 rounded hover:bg-gray-100 mr-2"
        >
          {isSubmitting ? "Отправка..." : "Подобрать"}
        </button>
        <button
          onClick={() => setFilterWindow(true)}
          className=""
        >
          <div className="relative">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              className="filter-icon"
            >
              <path
                d="M22 3H2L10 12.46V19L14 21V12.46L22 3Z"
                stroke="url(#filterGradient)"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <defs>
                <linearGradient
                  id="filterGradient"
                  x1="2"
                  y1="3"
                  x2="22"
                  y2="3"
                  gradientUnits="userSpaceOnUse"
                >
                  <stop stopColor="#3B82F6" />
                  <stop offset="1" stopColor="#8B5CF6" />
                </linearGradient>
              </defs>
            </svg>
          </div>
        </button>
      </div>

      {/* Сообщение о загрузке или ошибке */}
      {(isLoading || isFiltering) && (
        <div className="text-center py-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
        </div>
      )}
      {error && <div className="text-center text-red-500 py-4">{error}</div>}

      {/* Сообщение, если нет результатов */}
      {isEmptyResults && (
        <div className="bg-white p-8 text-center rounded-lg">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#9CA3AF"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="mx-auto mb-4"
          >
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            <line x1="11" y1="8" x2="11" y2="14"></line>
            <line x1="8" y1="11" x2="14" y2="11"></line>
          </svg>
          <h3 className="text-lg font-medium text-gray-500 mb-2">Ничего не найдено</h3>
          <p className="text-gray-400">Попробуйте изменить параметры фильтрации</p>
          <button
            onClick={handleResetFilters}
            className="mt-4 px-4 py-2 bg-gray-100 text-gray-600 rounded-md hover:bg-gray-200 transition-colors"
          >
            Сбросить фильтры
          </button>
        </div>
      )}

      {/* Таблица с собственным скроллом */}
      {!isLoading && !isFiltering && !error && (
        <div className="bg-white overflow-auto scrollbar-custom">
          <table className="w-full table-fixed">
            <thead className="sticky top-0 backdrop-blur-md">
              {table.getHeaderGroups().map((headerGroup) => (
                <tr key={headerGroup.id} className="hover:bg-muted/50 transition-colors">
                  {headerGroup.headers.map((header) => {
                    const isSelectColumn = header.id === 'select';
                    
                    return (
                      <th
                        key={header.id}
                        onClick={!isSelectColumn ? header.column.getToggleSortingHandler() : undefined}
                        className="px-4 py-2 border-b-2 border-gray-300 text-left text-sm font-semibold text-gray-600 tracking-wider cursor-pointer hover:bg-gray-50"
                        style={{ width: `${header.column.columnDef.size}px` }}
                      >
                        <div className="flex items-center">
                          {flexRender(header.column.columnDef.header, header.getContext())}
                          
                          {!isSelectColumn && (
                            <>
                              {header.column.getIsSorted() === 'asc' ? (
                                <svg
                                  xmlns="http://www.w3.org/2000/svg"
                                  width="24"
                                  height="24"
                                  viewBox="0 0 24 24"
                                  fill="none"
                                  stroke="currentColor"
                                  strokeWidth="2"
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  className="lucide lucide-chevron-up h-4 w-4 -translate-x-[-25%] transition-transform scale-100"
                                >
                                  <path d="m18 15-6-6-6 6"></path>
                                </svg>
                              ) : header.column.getIsSorted() === 'desc' ? (
                                <svg
                                  xmlns="http://www.w3.org/2000/svg"
                                  width="24"
                                  height="24"
                                  viewBox="0 0 24 24"
                                  fill="none"
                                  stroke="currentColor"
                                  strokeWidth="2"
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  className="lucide lucide-chevron-up h-4 w-4 -translate-x-[-25%] transition-transform rotate-180 scale-100"
                                >
                                  <path d="m18 15-6-6-6 6"></path>
                                </svg>
                              ) : (
                                <svg
                                  xmlns="http://www.w3.org/2000/svg"
                                  width="24"
                                  height="24"
                                  viewBox="0 0 24 24"
                                  fill="none"
                                  stroke="currentColor"
                                  strokeWidth="2"
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  className="lucide lucide-chevrons-up-down text-muted-foreground/40 group-hover:text-muted-foreground ml-1 h-4 w-4 transition-transform scale-100"
                                >
                                  <path d="m7 15 5 5 5-5"></path>
                                  <path d="m7 9 5-5 5 5"></path>
                                </svg>
                              )}
                            </>
                          )}
                        </div>
                      </th>
                    );
                  })}
                </tr>
              ))}
            </thead>
            <tbody>
              {table.getRowModel().rows.map((row) => (
                <tr key={row.id} className="border-b">
                  {row.getVisibleCells().map((cell) => (
                    <td
                      key={cell.id}
                      className="px-4 py-2 truncate"
                      style={{ width: `${cell.column.getSize()}px` }}
                    >
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
    <TryFilters 
      isOpen={filterWindow} 
      onClose={() => {setFilterWindow(false)}} 
      handleFilterChange={handleFilterChange} 
      data={filtersData}
      filters={filters}
      filtersResetFlag={filtersResetFlag}
      handleResetFilters={handleResetFilters}
      // Площади
      setFirstMinArea={setFirstMinArea}
      setFirstMaxArea={setFirstMaxArea}
      firstMinArea={firstMinArea}
      firstMaxArea={firstMaxArea}
      setSecondMinArea={setSecondMinArea}
      setSecondMaxArea={setSecondMaxArea}
      secondMinArea={secondMinArea}
      secondMaxArea={secondMaxArea}
      setThirdMinArea={setThirdMinArea}
      setThirdMaxArea={setThirdMaxArea}
      thirdMinArea={thirdMinArea}
      thirdMaxArea={thirdMaxArea}
      setMinFloor={setMinFloor}
      setMaxFloor={setMaxFloor}
      minFloor={minFloor}
      maxFloor={maxFloor}
      setSearchQuery={setSearchQuery}
      searchQuery={searchQuery}
    />
  </div>
);
}