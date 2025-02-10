import React, { useState, useEffect, useRef  } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  flexRender,
} from '@tanstack/react-table';
import { useVirtualizer  } from '@tanstack/react-virtual';

const Try = () => {
  // Состояние для данных, загрузки и фильтра
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

  const columns = React.useMemo(
    () => [
      {
        header: 'Name',
        accessorKey: 'name',
        enableSorting: true,
        size: 200, // Устанавливаем фиксированную ширину для столбца
      },
      {
        header: 'Age',
        accessorKey: 'age',
        enableSorting: true,
        size: 100, // Устанавливаем фиксированную ширину для столбца
      },
      {
        header: 'Address',
        accessorKey: 'address',
        size: 300, // Устанавливаем фиксированную ширину для столбца
      },
    ],
    []
  );

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true); // Начинаем загрузку данных
      try {
        // Здесь имитируем запрос на сервер (вы можете заменить это на реальный запрос)
        const fetchedData = await new Promise((resolve) =>
          setTimeout(() => resolve([
            { name: 'John Doe', age: 28, address: '123 Main St' },
            { name: 'Jane Doe', age: 32, address: '456 Elm St' },
            { name: 'Sam Smith', age: 25, address: '789 Oak St' },
            { name: 'Alice Johnson', age: 30, address: '321 Pine St' },
            { name: 'Bob Lee', age: 22, address: '567 Birch St' },
            { name: 'Charlie Brown', age: 35, address: '234 Cedar St' },
            { name: 'David White', age: 40, address: '890 Maple St' },
            { name: 'Eve Adams', age: 27, address: '678 Oak Ave' },
          ]), 200) // Задержка в 2 секунды
        );
        setData(fetchedData);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false); // Заканчиваем загрузку данных
      }
    };

    fetchData();
  }, []);

  return (
    <div className="App">
      <h1 className="text-2xl font-bold text-center my-4">User Table</h1>
      <Table columns={columns} data={data} loading={loading} />
    </div>
  );
};

const Table = ({ columns, data, loading }) => {
  const [globalFilter, setGlobalFilter] = useState('');
  const [sorting, setSorting] = useState([]);

  const table = useReactTable({
    data,
    columns,
    state: {
      globalFilter,
      sorting,
    },
    onGlobalFilterChange: setGlobalFilter,
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  const tableContainerRef = useRef(null);

  // Виртуализация строк
  const rowVirtualizer = useVirtualizer({
    count: table.getRowModel().rows.length,
    estimateSize: () => 48, // Высота строки в пикселях
    getScrollElement: () => tableContainerRef.current,
    overscan: 10, // Количество дополнительных строк для рендеринга
  });

  // Рассчитываем одинаковую ширину для всех столбцов
  const columnWidth = `${100 / columns.length}%`;

  return (
    <div className="p-4">
      <input
        type="text"
        value={globalFilter}
        onChange={(e) => setGlobalFilter(e.target.value)}
        placeholder="Search..."
        className="mb-4 p-2 border rounded"
      />
      
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-[#01c5ad] border-solid"></div>
        </div>
      ) : (
        <div
          ref={tableContainerRef}
          className="min-w-full bg-white border overflow-auto"
          style={{ height: '600px' }} // Фиксированная высота контейнера
        >
          <table className="w-full table-fixed"> {/* Добавлен table-fixed */}
            <thead className="sticky top-0 bg-white z-10">
              {table.getHeaderGroups().map((headerGroup) => (
                <tr key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <th
                      key={header.id}
                      onClick={header.column.getToggleSortingHandler()}
                      className="px-6 py-3 border-b-2 border-gray-300 text-left text-sm font-semibold text-gray-600 uppercase tracking-wider cursor-pointer hover:bg-gray-50"
                      style={{ width: columnWidth }} // Одинаковая ширина для всех столбцов
                    >
                      {flexRender(
                        header.column.columnDef.header,
                        header.getContext()
                      )}
                      <span className="ml-2">
                        {header.column.getIsSorted() === 'asc' ? '🔼' : header.column.getIsSorted() === 'desc' ? '🔽' : null}
                      </span>
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody
              style={{
                height: `${rowVirtualizer.getTotalSize()}px`,
                position: 'relative',
              }}
            >
              {rowVirtualizer.getVirtualItems().map((virtualRow) => {
                const row = table.getRowModel().rows[virtualRow.index];
                return (
                  <tr
                    key={row.id}
                    style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      width: '100%',
                      height: `${virtualRow.size}px`,
                      transform: `translateY(${virtualRow.start}px)`,
                    }}
                    className="hover:bg-gray-100"
                  >
                    {row.getVisibleCells().map((cell) => (
                      <td
                        key={cell.id}
                        className="px-6 py-4 border-b border-gray-200 text-sm text-gray-700 truncate w-full" // Добавлен truncate
                         // Одинаковая ширина для всех ячеек
                      >
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext()
                        )}
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};


export default Try;
