import React, { useMemo, useState, useEffect, useCallback, useRef } from "react";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  flexRender
} from "@tanstack/react-table";
import { useVirtualizer } from '@tanstack/react-virtual';
import { HOSTLINK } from "..";
import AdressCell from "./Cells/AdressCell";
import PloshCell from "./Cells/PloshCell";
import TryFilters from "./Filters/TryFilters";

// Мемоизированные компоненты ячеек
const MemoizedAdressCell = React.memo(AdressCell);
const MemoizedPloshCell = React.memo(PloshCell);

// Кастомный хук для дебаунсинга
const useDebounce = (value, delay) => {
  const [debouncedValue, setDebouncedValue] = useState(value);
  
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);
    
    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);
  
  return debouncedValue;
};

export default function ManualSelectionModal({ isOpen, onClose, apartmentId, fetchApartments, getFilteData, lastSelectedAddres, lastSelectedMunicipal }) {
  const [data, setData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [rowSelection, setRowSelection] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [filterWindow, setFilterWindow] = useState(false);
  const [filters, setFilters] = useState({});
  const [filtersData, setFiltersData] = useState({});
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
  const [entrancSearchQuery, setEntranceSearchQuery] = useState("");
  const [selectedFilters, setSelectedFilters] = useState({
    district: [],
    municipal_district: [],
    house_address: []
  });

  // Дебаунсированные значения для фильтров
  const debouncedSearchQuery = useDebounce(searchQuery, 300);
  const debouncedEntrancSearchQuery = useDebounce(entrancSearchQuery, 300);
  const debouncedFirstMinArea = useDebounce(firstMinArea, 300);
  const debouncedFirstMaxArea = useDebounce(firstMaxArea, 300);
  const debouncedSecondMinArea = useDebounce(secondMinArea, 300);
  const debouncedSecondMaxArea = useDebounce(secondMaxArea, 300);
  const debouncedThirdMinArea = useDebounce(thirdMinArea, 300);
  const debouncedThirdMaxArea = useDebounce(thirdMaxArea, 300);
  const debouncedMinFloor = useDebounce(minFloor, 300);
  const debouncedMaxFloor = useDebounce(maxFloor, 300);

  const tableContainerRef = useRef(null);

  // Мемоизированные колонки
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
        accessorKey: "house_address",
        enableSorting: true,
        cell: ({ row }) => <MemoizedAdressCell props={row.original} />,
        size: 350,
      },
      {
        header: '№ Кв.',
        accessorKey: 'apart_number',
        enableSorting: true,
        cell: ({ row }) => 
          <div className="text-xs">
            {row.original['apart_number']}
          </div>,
        size: 100,
      },
      {
        header: "Площадь, тип, этаж",
        accessorKey: "full_living_area",
        cell: ({ row }) => <MemoizedPloshCell props={row.original} />,
        size: 350,
      },
    ],
    []
  );

  // Мемоизированный обработчик фильтров
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

  // Мемоизированный сброс фильтров
  const handleResetFilters = useCallback(() => {
    setSelectedFilters({
      district: [],
      municipal_district: [],
      house_address: []
    });
    setFilters({});
    setFiltersResetFlag(prev => !prev);
    setFirstMinArea("");
    setFirstMaxArea("");
    setSecondMinArea("");
    setSecondMaxArea("");
    setThirdMinArea("");
    setThirdMaxArea("");
    setMinFloor("");
    setMaxFloor("");
    setSearchQuery("");
  }, []);

  // Загрузка данных с оптимизацией
  const fetchData = useCallback(async () => {
    if (!isOpen || !apartmentId) return;
    
    setIsLoading(true);
    setError(null);
  
    try {
      const response = await fetch(
        `${HOSTLINK}/tables/apartment/${apartmentId}/void_aparts`, {
          credentials: 'include',
        }
      );
  
      if (!response.ok) {
        throw new Error("Ошибка при загрузке данных");
      }
  
      const result = await response.json();
      setData(result);
      setFiltersData(getFilteData(result));
    } catch (error) {
      console.error("Ошибка:", error);
      setError("Не удалось загрузить данные. Попробуйте снова.");
    } finally {
      setIsLoading(false);
    }
  }, [isOpen, apartmentId, getFilteData]);

  useEffect(() => {
    if (isOpen && apartmentId) {
      fetchData();
    }
  }, [isOpen, apartmentId, fetchData]);

  // Мемоизированная фильтрация данных
  const filteredApartments = useMemo(() => {
    if (!data || data.length === 0) return [];
    
    let filtered = data;

    // Фильтрация по поисковому запросу
    if (debouncedSearchQuery) {
      filtered = filtered.filter((item) => {
        return String(item.apart_number || '')?.toLowerCase().includes(debouncedSearchQuery.toLowerCase());
      });
    }

    // Фильтрация по поисковому запросу
    if (debouncedEntrancSearchQuery) {
      filtered = filtered.filter((item) => {
        return String(item.entrance_number || '')?.toLowerCase().includes(debouncedEntrancSearchQuery.toLowerCase());
      });
    }

    // Фильтрация по площадям
    if (debouncedFirstMinArea || debouncedFirstMaxArea) {
      filtered = filtered.filter((item) => {
        const area = parseFloat(item.full_living_area);
        const min = parseFloat(debouncedFirstMinArea);
        const max = parseFloat(debouncedFirstMaxArea);

        let valid = true;
        if (!isNaN(min)) valid = valid && area >= min;
        if (!isNaN(max)) valid = valid && area <= max;
        return valid;
      });
    }

    if (debouncedSecondMinArea || debouncedSecondMaxArea) {
      filtered = filtered.filter((item) => {
        const area = parseFloat(item.total_living_area);
        const min = parseFloat(debouncedSecondMinArea);
        const max = parseFloat(debouncedSecondMaxArea);

        let valid = true;
        if (!isNaN(min)) valid = valid && area >= min;
        if (!isNaN(max)) valid = valid && area <= max;
        return valid;
      });
    }

    if (debouncedThirdMinArea || debouncedThirdMaxArea) {
      filtered = filtered.filter((item) => {
        const area = parseFloat(item.living_area);
        const min = parseFloat(debouncedThirdMinArea);
        const max = parseFloat(debouncedThirdMaxArea);

        let valid = true;
        if (!isNaN(min)) valid = valid && area >= min;
        if (!isNaN(max)) valid = valid && area <= max;
        return valid;
      });
    }

    // Фильтрация по этажу
    if (debouncedMinFloor || debouncedMaxFloor) {
      filtered = filtered.filter((item) => {
        const floor = parseFloat(item.floor);
        const min = parseFloat(debouncedMinFloor);
        const max = parseFloat(debouncedMaxFloor);

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

    return filtered;
  }, [
    data, 
    filters, 
    debouncedSearchQuery,
    debouncedEntrancSearchQuery,
    debouncedFirstMinArea, 
    debouncedFirstMaxArea, 
    debouncedSecondMinArea, 
    debouncedSecondMaxArea, 
    debouncedThirdMinArea, 
    debouncedThirdMaxArea,
    debouncedMinFloor,
    debouncedMaxFloor
  ]);

  // Создаем таблицу с мемоизацией
  const table = useReactTable({
    data: filteredApartments,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    state: {
      rowSelection,
    },
    onRowSelectionChange: setRowSelection,
  });

  // Виртуализатор строк
  const rowVirtualizer = useVirtualizer({
    count: table.getRowModel().rows.length,
    getScrollElement: () => tableContainerRef.current,
    estimateSize: () => 75, // Высота строки
    overscan: 10,
  });

  // Мемоизированный обработчик ручного сопоставления
  const handleManualMatching = useCallback(async () => {
    if (!apartmentId) return;
  
    const selectedRows = table.getSelectedRowModel().rows;
    const selectedIds = selectedRows.map((row) => parseInt(row.original.new_apart_id));
  
    if (selectedIds.length === 0) {
      alert("Выберите хотя бы одну строку");
      return;
    }
  
    setIsSubmitting(true);
    try {
      const response = await fetch(
        `${HOSTLINK}/tables/apartment/${apartmentId}/manual_matching?apart_type=OldApart`,
        {
          method: "POST",
          credentials: 'include',
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            new_apart_ids: selectedIds,
            apart_type: "OldApart",
          }),
        }
      );
  
      if (!response.ok) {
        throw new Error("Ошибка при сопоставлении");
      }

      onClose();
    } catch (error) {
      console.error("Ошибка:", error);
      alert("Ошибка при сопоставлении");
    } finally {
      setIsSubmitting(false);
      setRowSelection({});
      fetchApartments(lastSelectedAddres, lastSelectedMunicipal);
    }
  }, [apartmentId, table, onClose, fetchApartments, lastSelectedAddres, lastSelectedMunicipal]);

  // Компонент строки для виртуализированного списка
  const Row = useCallback(({ index, style }) => {
    const row = table.getRowModel().rows[index];
    return (
      <div 
        style={style} 
        className="flex items-center border-b relative"
      >
        {row.getVisibleCells().map((cell) => (
          <div
            key={cell.id}
            className="px-4 py-2 truncate flex-shrink-0"
            style={{ width: `${cell.column.getSize()}px` }}
          >
            {flexRender(
              cell.column.columnDef.cell,
              cell.getContext()
            )}
          </div>
        ))}
      </div>
    );
  }, [table]);

  if (!isOpen) return null;

  const isEmptyResults = !isLoading && !error && filteredApartments.length === 0;

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-gray-50 rounded-lg p-6 w-full max-w-6xl max-h-[90vh] flex flex-col">
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

        {isLoading && (
          <div className="text-center py-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
          </div>
        )}
        {error && <div className="text-center text-red-500 py-4">{error}</div>}

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

        {!isLoading && !error && filteredApartments.length > 0 && (
          <div className="bg-white overflow-hidden scrollbar-custom flex-1">
            <table className="w-full table-fixed">
              <thead className="sticky top-0 backdrop-blur-md">
                {table.getHeaderGroups().map((headerGroup) => (
                  <tr key={headerGroup.id} className="hover:bg-muted/50 transition-colors h-10">
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
            </table>
            <div
              ref={tableContainerRef}
              className="scrollbar-custom"
              style={{
                height: '800px',
                overflowY: 'auto',
              }}
            >
              <div
                style={{
                  height: `${rowVirtualizer.getTotalSize()}px`,
                  width: '100%',
                  position: 'relative',
                }}
              >
                {rowVirtualizer.getVirtualItems().map((virtualRow) => {
                  const row = table.getRowModel().rows[virtualRow.index];
                  return (
                    <div
                      key={virtualRow.key}
                      className="flex absolute left-0 w-full border-b items-center"
                      style={{
                        height: `${virtualRow.size}px`,
                        transform: `translateY(${virtualRow.start}px)`,
                      }}
                    >
                      {row.getVisibleCells().map((cell) => (
                        <div
                          key={cell.id}
                          className="px-4 py-2 truncate flex-shrink-0"
                          style={{ width: `${cell.column.getSize()}px` }}
                        >
                          {flexRender(
                            cell.column.columnDef.cell,
                            cell.getContext()
                          )}
                        </div>
                      ))}
                    </div>
                  );
                })}
              </div>
            </div>
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
        entrancSearchQuery={entrancSearchQuery}
        setEntranceSearchQuery={setEntranceSearchQuery}
      />
    </div>
  );
}