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

export default function ManualSelectionModal({ isOpen, onClose, apartmentId, fetchApartments, getFilteData }) {
  const [data, setData] = useState([]); // Состояние для данных таблицы
  const [filteredApartments, setFilteredApartments] = useState([]); // Отфильтрованные данные
  const [isLoading, setIsLoading] = useState(false); // Состояние для загрузки
  const [error, setError] = useState(null); // Состояние для ошибок
  const [searchQuery, setSearchQuery] = useState(""); // Состояние для поискового запроса
  const [minArea, setMinArea] = useState(""); // Минимальная площадь
  const [maxArea, setMaxArea] = useState(""); // Максимальная площадь
  const [rowSelection, setRowSelection] = useState({}); // Состояние для выбранных строк
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isFiltering, setIsFiltering] = useState(false); // Состояние для индикатора загрузки фильтрации
  const [filterWindow, setFilterWindow] = useState(false);
  const [filters, setFilters] = useState({}); // Состояние для фильтров
  const [filtersData, setFiltersData] = useState({}); // Состояние для фильтров
  const [filtersResetFlag, setFiltersResetFlag] = useState(false);

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
        `${HOSTLINK}/tables/apartment/${apartmentId}/void_aparts`
      );
  
      if (!response.ok) {
        throw new Error("Ошибка при загрузке данных");
      }
  
      const result = await response.json();
      setData(result);
      setFilteredApartments(result);
      setFiltersData(getFilteData(result));
    } catch (error) {
      console.error("Ошибка:", error);
      setError("Не удалось загрузить данные. Попробуйте снова.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!data || data.length === 0) return;
  
    setIsFiltering(true);
    let filtered = data;
  
    if (minArea || maxArea) {
      filtered = filtered.filter((item) => {
        const area = parseFloat(item.full_living_area);
        const min = parseFloat(minArea);
        const max = parseFloat(maxArea);
  
        let valid = true;
        if (!isNaN(min)) valid = valid && area >= min;
        if (!isNaN(max)) valid = valid && area <= max;
        return valid;
      });
    }
  
    Object.entries(filters).forEach(([filterType, selectedValues]) => {
      if (selectedValues.length > 0) {
        const filterKey = filterType.toLowerCase();
        filtered = filtered.filter((item) => {
          return selectedValues.some(val => item[filterKey] === val);
        });
      }
    });
  
    if (searchQuery) {
      filtered = filtered.filter((item) =>
        item.house_address.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
  
    setFilteredApartments(filtered);
    setIsFiltering(false);
  }, [data, filters, searchQuery, minArea, maxArea]);

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
      fetchApartments();
    }
  };

  if (!isOpen) return null;

return (
  <div className="fixed inset-0 z-40 flex items-center justify-center bg-black bg-opacity-50">
    <div className="bg-white rounded-lg p-6 w-full max-w-6xl max-h-[90vh] flex flex-col">
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

      {/* Фильтры */}
      <div className="flex mb-2">
        {/* Поисковая строка */}
        <div className="mb-4">
          <input
            type="text"
            placeholder="Поиск по адресу..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex gap-4 mx-4">
          <div className="flex items-center gap-2">
            <label>Площадь от:</label>
            <input
              value={minArea}
              onChange={(e) => setMinArea(e.target.value)}
              className="w-14 px-2 py-1 border rounded"
              placeholder="мин"
              step="0.1"
            />
          </div>
          <div className="flex items-center gap-2">
            <label>до:</label>
            <input
              value={maxArea}
              onChange={(e) => setMaxArea(e.target.value)}
              className="w-14 px-2 py-1 border rounded"
              placeholder="макс"
              step="0.1"
            />
          </div>
        </div>
      </div>

      <div className="mb-4">
        <button
          onClick={handleManualMatching}
          disabled={isSubmitting}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
        >
          {isSubmitting ? "Отправка..." : "Сопоставить выбранное"}
        </button>
        <button
          onClick={() => setFilterWindow(true)}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Фильтры
        </button>
      </div>

      {/* Сообщение о загрузке или ошибке */}
      {(isLoading || isFiltering) && (
        <div className="text-center py-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
        </div>
      )}
      {error && <div className="text-center text-red-500 py-4">{error}</div>}

      {/* Таблица с собственным скроллом */}
      {!isLoading && !isFiltering && !error && (
        <div className="overflow-auto scrollbar-custom">
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
    />
  </div>
);
}