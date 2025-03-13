import React, { useMemo, useState, useEffect, useCallback } from "react";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  flexRender,
} from "@tanstack/react-table";
import { HOSTLINK } from "..";
import AdressCell from "./Cells/AdressCell";
import PloshCell from "./Cells/PloshCell";
import DropdownFilter from "./Filters/DropdownFilter";

export default function ManualSelectionModal({ isOpen, onClose, apartmentId }) {
  const [data, setData] = useState([]); // Состояние для данных таблицы
  const [filteredApartments, setFilteredApartments] = useState([]); // Отфильтрованные данные
  const [isLoading, setIsLoading] = useState(false); // Состояние для загрузки
  const [error, setError] = useState(null); // Состояние для ошибок
  const [filters, setFilters] = useState({}); // Состояние для фильтров

  // Загрузка данных при открытии модального окна
  useEffect(() => {
    if (isOpen && apartmentId) {
      fetchData();
    }
  }, [isOpen, apartmentId]);

  // Функция для выполнения GET-запроса
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
      setData(result); // Обновляем данные таблицы
      setFilteredApartments(result); // Инициализируем отфильтрованные данные
      console.log("Данные загружены:", result);
    } catch (error) {
      console.error("Ошибка:", error);
      setError("Не удалось загрузить данные. Попробуйте снова.");
    } finally {
      setIsLoading(false);
    }
  };

  // Обработчик изменения фильтров
  const handleFilterChange = useCallback((filterType, selectedValues) => {
    setFilters((prevFilters) => {
      // Если selectedValues пуст, удаляем ключ filterType из объекта
      if (selectedValues.length === 0) {
        const { [filterType]: _, ...rest } = prevFilters;
        return rest;
      }
      // Иначе обновляем значение для filterType
      return {
        ...prevFilters,
        [filterType]: selectedValues,
      };
    });
  }, []);

    // Используем useEffect для отслеживания изменений filters
    useEffect(() => {
      console.log('filters updated:', filters);
      console.log("filerd data", filteredApartments);
    }, [filters]);

  // Применение фильтров к данным
  useEffect(() => {
    if (!data || data.length === 0) return;

    let filtered = data;

    // Применяем каждый фильтр
    Object.entries(filters).forEach(([filterType, selectedValues]) => {
      if (selectedValues.length > 0) {
        const filterKey = filterType.toLowerCase();

        filtered = filtered.filter((item) => {
          // Проверяем наличие "Не подобрано" в выбранных значениях
          const hasNotMatched = selectedValues.includes("Не подобрано");
          // Проверяем обычные значения статусов
          const hasRegularStatus = selectedValues.some(
            (val) => val !== "Не подобрано" && item[filterKey] === val
          );

          // Если выбран "Не подобрано" - проверяем на null, иначе проверяем обычные статусы
          return (hasNotMatched && item[filterKey] === null) || hasRegularStatus;
        });
      }
    });

    setFilteredApartments(filtered);
  }, [data, filters]);

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
  });

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-6xl max-h-[90vh] overflow-auto">
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
          <DropdownFilter
            item="Комнаты"
            data={[1, 2, 3]}
            func={handleFilterChange}
            filterType="room_count"
            isFiltersReset={false}
          />
        </div>

        {/* Сообщение о загрузке или ошибке */}
        {isLoading && <div className="text-center py-4">Загрузка данных...</div>}
        {error && <div className="text-center text-red-500 py-4">{error}</div>}

        {/* Таблица */}
        {!isLoading && !error && (
          <div className="overflow-x-auto">
            <table className="w-full table-fixed">
              <thead>
                {table.getHeaderGroups().map((headerGroup) => (
                  <tr key={headerGroup.id}>
                    {headerGroup.headers.map((header) => (
                      <th
                        key={header.id}
                        className="px-4 py-2 text-left font-bold bg-gray-100"
                        style={{ width: `${header.getSize()}px` }} // Жесткая ширина столбца
                      >
                        {flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <tbody>
                {table.getRowModel().rows.map((row) => (
                  <tr key={row.id} className="border-b">
                    {row.getVisibleCells().map((cell) => (
                      <td
                        key={cell.id}
                        className="px-4 py-2 truncate" // Обрезаем текст, если он не помещается
                        style={{ width: `${cell.column.getSize()}px` }} // Жесткая ширина ячейки
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
    </div>
  );
}