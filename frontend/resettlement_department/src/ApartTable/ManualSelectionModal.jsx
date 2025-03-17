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

export default function ManualSelectionModal({ isOpen, onClose, apartmentId }) {
  const [data, setData] = useState([]); // Состояние для данных таблицы
  const [filteredApartments, setFilteredApartments] = useState([]); // Отфильтрованные данные
  const [isLoading, setIsLoading] = useState(false); // Состояние для загрузки
  const [error, setError] = useState(null); // Состояние для ошибок
  const [filters, setFilters] = useState({}); // Состояние для фильтров
  const [searchQuery, setSearchQuery] = useState(""); // Состояние для поискового запроса
  const [minArea, setMinArea] = useState(""); // Минимальная площадь
  const [maxArea, setMaxArea] = useState(""); // Максимальная площадь
  const [rowSelection, setRowSelection] = useState({}); // Состояние для выбранных строк
  const [isSubmitting, setIsSubmitting] = useState(false);

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

  // Применение фильтров и поиска к данным
  useEffect(() => {
    if (!data || data.length === 0) return;

    let filtered = data;

    // Применяем фильтр по площади
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

    // Применяем поисковый запрос
    if (searchQuery) {
      filtered = filtered.filter((item) =>
        item.house_address.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    setFilteredApartments(filtered); // Обновляем отфильтрованные данные
  }, [data, filters, searchQuery, minArea, maxArea]); // Добавлены minArea и maxArea в зависимости

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

  // Обработчик для кнопки "Сопоставить выбранное"
  const handleManualMatching = async () => {
    if (!apartmentId) return;
    
    const selectedRows = table.getSelectedRowModel().rows;
    const selectedIds = selectedRows.map((row) => row.original.new_apart_id);

    if (selectedIds.length === 0) {
      alert("Выберите хотя бы одну строку");
      return;
    }

    setIsSubmitting(true);
    try {
      // Отправляем запрос для каждого выбранного ID
      const requests = selectedIds.map(newApartId =>
        fetch(`${HOSTLINK}/tables/apartment/${apartmentId}/manual_matching`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            new_apart_id: newApartId,
            apart_type: "OldApart" // Или другое значение, в зависимости от логики
          })
        })
      );

      // Ожидаем выполнения всех запросов
      const responses = await Promise.all(requests);
      
      // Проверяем статусы ответов
      const errors = responses.filter(response => !response.ok);
      if (errors.length > 0) {
        throw new Error("Некоторые запросы не удались");
      }

      alert("Сопоставление успешно выполнено!");
      onClose(); // Закрываем модальное окно
    } catch (error) {
      console.error("Ошибка:", error);
      alert("Ошибка при сопоставлении");
    } finally {
      setIsSubmitting(false);
      setRowSelection({}); // Сбрасываем выбор
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

        {/* Фильтры */}
        <div className="flex mb-2">
          <div className="flex gap-4 mb-4">
            <div className="flex items-center gap-2">
              <label>Площадь от:</label>
              <input
                type="number"
                value={minArea}
                onChange={(e) => setMinArea(e.target.value)}
                className="w-24 px-2 py-1 border rounded"
                placeholder="мин"
                step="0.1"
              />
            </div>
            <div className="flex items-center gap-2">
              <label>до:</label>
              <input
                type="number"
                value={maxArea}
                onChange={(e) => setMaxArea(e.target.value)}
                className="w-24 px-2 py-1 border rounded"
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
        </div>

        {/* Сообщение о загрузке или ошибке */}
        {isLoading && <div className="text-center py-4">Загрузка данных...</div>}
        {error && <div className="text-center text-red-500 py-4">{error}</div>}

        {/* Таблица с собственным скроллом */}
        {!isLoading && !error && (
          <div className="overflow-auto scrollbar-custom">
            <table className="w-full table-fixed">
              <thead className="sticky top-0 backdrop-blur-md">
                {table.getHeaderGroups().map((headerGroup) => (
                  <tr key={headerGroup.id}>
                    {headerGroup.headers.map((header) => (
                      <th
                        key={header.id}
                        className="px-4 py-2 text-left font-bold"
                        style={{ width: `${header.getSize()}px` }}
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
    </div>
  );
}