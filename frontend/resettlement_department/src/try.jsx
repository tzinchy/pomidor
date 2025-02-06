import React, { useState, useEffect } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  flexRender,
} from '@tanstack/react-table';

const Try = () => {
  // Состояние для данных, загрузки и фильтра
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [globalFilter, setGlobalFilter] = useState('');
  const [sorting, setSorting] = useState([]);

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
          ]), 5000) // Задержка в 2 секунды
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
        <table className="min-w-full bg-white border">
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    onClick={header.column.getToggleSortingHandler()}
                    className="px-6 py-3 border-b-2 border-gray-300 text-left text-sm font-semibold text-gray-600 uppercase tracking-wider cursor-pointer hover:bg-gray-50"
                    style={{ width: header.column.columnDef.size }} // Применяем фиксированную ширину
                  >
                    {flexRender(
                      header.column.columnDef.header,
                      header.getContext()
                    )}
                    <span className="ml-2">
                      {header.column.getIsSorted() === 'asc' ? (
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          className="w-4 h-4 inline-block text-gray-600"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            d="M19 9l-7 7-7-7"
                          />
                        </svg>
                      ) : header.column.getIsSorted() === 'desc' ? (
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          className="w-4 h-4 inline-block text-gray-600"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            d="M5 15l7-7 7 7"
                          />
                        </svg>
                      ) : null}
                    </span>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row) => (
              <tr key={row.id} className="hover:bg-gray-100">
                {row.getVisibleCells().map((cell) => (
                  <td
                    key={cell.id}
                    className="px-6 py-4 border-b border-gray-200 text-sm text-gray-700"
                  >
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default Try;
