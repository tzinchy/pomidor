import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  useReactTable,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
} from '@tanstack/react-table';
import { useState, useEffect, useMemo } from 'react';
import Header from './Balance/Components/Header';
import { HOSTLINK } from '.';
  
  const defaultData = [
    {
        id: 1,
        name: 'Алексей Петров',
        age: 28,
        email: 'alex@example.com',
        status: 'Активен',
    },
    {
        id: 2,
        name: 'Мария Иванова',
        age: 34,
        email: 'maria@example.com',
        status: 'Неактивен',
    },
    // ... больше данных
];

// 2. Создаем хелпер для колонок
const columnHelper = createColumnHelper();

// 3. Определяем колонки таблицы
const columns = [
    columnHelper.accessor('id', {
        header: 'ID',
        cell: info => info.getValue(),
        enableSorting: false,
    }),
    columnHelper.accessor('name', {
        header: 'Имя',
        cell: info => info.getValue(),
        sortingFn: 'text',
    }),
    columnHelper.accessor('age', {
        header: 'Возраст',
        cell: info => info.getValue(),
        sortingFn: 'basic',
    }),
    columnHelper.accessor('email', {
        header: 'Email',
        cell: info => info.getValue(),
    }),
    columnHelper.accessor('status', {
        header: 'Статус',
        cell: info => (
        <span className={`px-2 py-1 rounded ${
            info.getValue() === 'Активен' 
            ? 'bg-green-100 text-green-800' 
            : 'bg-red-100 text-red-800'
        }`}>
            {info.getValue()}
        </span>
        ),
    }),
];
  
  function DataTable() {
    const [data, setData] = useState(() => [...defaultData]);
    const [sorting, setSorting] = useState([]);
    const [columnFilters, setColumnFilters] = useState([]);
    const [globalFilter, setGlobalFilter] = useState('');
    const [columnSizing, setColumnSizing] = useState({});
    const [openFilterDropdown, setOpenFilterDropdown] = useState(null);

    const columnValues = useMemo(() => {
        const values = {};
        columns.forEach(column => {
          const accessor = column.accessorKey || column.id;
          
          // Получаем все значения для колонки
          const allValues = data.map(item => {
            const value = item[accessor];
            // Если значение - массив, возвращаем его, иначе создаем массив с одним элементом
            return Array.isArray(value) ? value : [value];
          }).flat();
      
          values[accessor] = [...new Set(allValues)];
        });
        return values;
      }, [data, columns]);

    const table = useReactTable({
        data,
        columns,
        state: {
        sorting,
        columnFilters,
        globalFilter,
        columnSizing,
        },
        // Добавляем настройки пагинации по умолчанию
        initialState: {
        pagination: {
            pageSize: 10, // Устанавливаем размер страницы
        },
        },
        onSortingChange: setSorting,
        onColumnFiltersChange: setColumnFilters,
        onGlobalFilterChange: setGlobalFilter,
        onColumnSizingChange: setColumnSizing,
        getCoreRowModel: getCoreRowModel(),
        getSortedRowModel: getSortedRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
    });
  
    // Обработчик фильтрации
    const handleFilterChange = (columnId, value) => {
        const newFilters = columnFilters.filter(f => f.id !== columnId);
        if (value) {
        newFilters.push({ id: columnId, value });
        }
        setColumnFilters(newFilters);
    };

    // Рендер выпадающего фильтра
    const renderFilterDropdown = (header) => {
        const columnId = header.column.id;
        const currentFilter = columnFilters.find(f => f.id === columnId)?.value;

        return (
        <div className="relative">
            <button
            onClick={(e) => {
                e.stopPropagation();
                setOpenFilterDropdown(openFilterDropdown === columnId ? null : columnId);
            }}
            className="mt-1 p-1 text-xs border rounded w-full text-left hover:bg-gray-100"
            >
            {currentFilter || `Фильтр ${header.column.columnDef.header}`}
            </button>

            {openFilterDropdown === columnId && (
            <div 
                className="absolute z-10 mt-1 w-full bg-white border rounded shadow-lg max-h-40 overflow-y-auto"
                onClick={(e) => e.stopPropagation()}
            >
                {columnValues[columnId].map(value => (
                <div
                    key={value}
                    className={`px-2 py-1 cursor-pointer hover:bg-blue-50 ${
                    currentFilter === value ? 'bg-blue-100' : ''
                    }`}
                    onClick={() => {
                    handleFilterChange(columnId, currentFilter === value ? null : value);
                    setOpenFilterDropdown(null);
                    }}
                >
                    {value}
                </div>
                ))}
            </div>
            )}
        </div>
        );
    };
  
    return (
      <div className="p-2">
        <Header />
        {/* Глобальный фильтр */}
        <div className="mb-4">
          <input
            type="text"
            placeholder="Поиск по всей таблице..."
            value={globalFilter}
            onChange={e => setGlobalFilter(e.target.value)}
            className="w-full p-2 border rounded"
          />
        </div>
  
        <table className="w-full border-collapse">
          <thead>
            {table.getHeaderGroups().map(headerGroup => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map(header => (
                  <th 
                    key={header.id}
                    className="border-b p-2 text-left relative group"
                    style={{ width: header.getSize() }}
                  >
                    {/* Заголовок с сортировкой */}
                    <div 
                      className="cursor-pointer hover:bg-gray-50 pr-4"
                      onClick={header.column.getToggleSortingHandler()}
                    >
                      {flexRender(
                        header.column.columnDef.header,
                        header.getContext()
                      )}
                      {{
                        asc: ' ↑',
                        desc: ' ↓',
                      }[header.column.getIsSorted()] ?? null}
                    </div>
  
                    {/* Фильтр для колонки */}
                    {header.column.getCanFilter() && renderFilterDropdown(header)}
                    {/* Изменение размера колонки */}
                    <div
                      onMouseDown={header.getResizeHandler()}
                      onTouchStart={header.getResizeHandler()}
                      className={`absolute right-0 top-0 h-full w-1 bg-gray-200 cursor-col-resize hover:bg-blue-400 ${
                        header.column.getIsResizing() ? 'bg-blue-400' : ''
                      }`}
                    />
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.length > 0 ? (
                table.getRowModel().rows.map(row => (
                    <tr key={row.id} className="hover:bg-gray-50">
                    {row.getVisibleCells().map(cell => (
                        <td 
                        key={cell.id} 
                        className="border-b p-2"
                        style={{ width: cell.column.getSize() }}
                        >
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                        </td>
                    ))}
                    </tr>
                ))
                ) : (
                // Добавляем сообщение при отсутствии данных
                <tr>
                    <td colSpan={columns.length} className="text-center py-4">
                    Нет данных для отображения
                    </td>
                </tr>
                )}
            </tbody>
        </table>
  
        {/* Пагинация */}
        <div className="flex items-center gap-4 mt-4">
          <button
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
            className="px-3 py-1 border rounded disabled:opacity-50"
          >
            Назад
          </button>
          <span>
            Страница {table.getState().pagination.pageIndex + 1} из{' '}
            {table.getPageCount()}
          </span>
          <button
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
            className="px-3 py-1 border rounded disabled:opacity-50"
          >
            Вперед
          </button>
        </div>
      </div>
    );
  }
  
  export default function Try() {
    return (
      <div className="p-4">
        <h1 className="text-2xl font-bold mb-4">Список пользователей</h1>
        <DataTable />
      </div>
    );
  }