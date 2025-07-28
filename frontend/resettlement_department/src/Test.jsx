import { 
  useReactTable, 
  flexRender, 
  getCoreRowModel, 
  getSortedRowModel 
} from '@tanstack/react-table';
import { useState, useMemo } from 'react';

// Функция для преобразования строки в массив
const parseChildren = (controls) => {
  if (Array.isArray(controls)) return controls;
  if (!controls) return [];
  
  try {
    const cleanedString = controls
      .replace(/^"+|"+$/g, '') // Удаляем кавычки в начале/конце
      .replace(/\\"/g, '"'); // Убираем экранирование
    return JSON.parse(cleanedString);
  } catch (e) {
    console.error('Parse error:', e);
    return [];
  }
};

// Преобразование данных с сохранением ссылок на оригинальные данные
const processData = (data) => {
  return data.flatMap(item => {
    const children = parseChildren(item.children_controls);
    return children.length > 0 
      ? children.map((child, idx) => ({
          ...item,
          ...child,
          _original: item, // Сохраняем ссылку на оригинальный элемент
          _isFirst: idx === 0,
          _groupSize: children.length
        }))
      : [{...item, _isFirst: true, _groupSize: 1}];
  });
};

const filterByPerson = (data, selectedPerson) => {
  if (!selectedPerson) return data; // Если не выбран person, возвращаем все данные
  
  return data.filter(item => {
    try {
      const children = parseChildren(item.children_controls);
      return children.some(child => child.person === selectedPerson);
    } catch (e) {
      console.error('Filter error:', e);
      return false;
    }
  });
};

// Основной компонент таблицы
export default function ParentChildTable({ data }) {
  const [sorting, setSorting] = useState([]);
  const [selectedPerson, setSelectedPerson] = useState(null);
  
  // Мемоизированные данные
  const flatData = useMemo(() => processData(data), [data]);
  
  // Фильтрация данных по выбранному person
  const filteredData = useMemo(() => {
    return selectedPerson 
      ? filterByPerson(flatData, selectedPerson)
      : flatData;
  }, [flatData, selectedPerson]);
  
  // Получаем уникальные значения person для выпадающего списка
  const personOptions = useMemo(() => {
    const persons = new Set();
    data.forEach(item => {
      const children = parseChildren(item.children_controls);
      children.forEach(child => {
        if (child.person) persons.add(child.person);
      });
    });
    return Array.from(persons).sort();
  }, [data]);
  
  const columns = useMemo(() => [
    {
      accessorKey: 'dgi_number',
      enableSorting: true,
      header: 'ДГИ номер',
      cell: ({ row }) => row.original._isFirst && (
        <td rowSpan={row.original._groupSize} className="px-4 py-2">
          {row.getValue('dgi_number')}
        </td>
      ),
      size: 50,
    },
    {
      accessorKey: 'date',
      enableSorting: true,
      header: 'Дата',
      cell: ({ row }) => row.original._isFirst && (
        <td rowSpan={row.original._groupSize} className="px-4 py-2">
          {new Date(row.getValue('date')).toLocaleDateString()}
        </td>
      ),
      size: 50,
    },
    {
      accessorKey: 'description',
      enableSorting: true,
      header: 'Описание',
      cell: ({ row }) => row.original._isFirst && (
        <td rowSpan={row.original._groupSize} className="px-4 py-2">
          {row.getValue('description')}
        </td>
      ),
      size: 700,
    },
    {
      accessorKey: 'executor_due_date',
      enableSorting: true,
      header: 'Дата исполнения',
      cell: ({ row }) => row.original._isFirst && (
        <td rowSpan={row.original._groupSize} className="px-4 py-2">
          {row.getValue('executor_due_date') ? new Date(row.getValue('executor_due_date')).toLocaleDateString() : ''}
        </td>
      ),
      size: 50,
    },
    {
      accessorKey: 'boss_due_date',
      enableSorting: true,
      header: 'Дата начальника???',
      cell: ({ row }) => row.original._isFirst && (
        <td rowSpan={row.original._groupSize} className="px-4 py-2">
          {row.getValue('boss_due_date') ? new Date(row.getValue('boss_due_date')).toLocaleDateString() : ''}
        </td>
      ),
      size: 50,
    },
    {
      accessorKey: 'boss2_due_date',
      enableSorting: true,
      header: 'Дата начальника2???',
      cell: ({ row }) => row.original._isFirst && (
        <td rowSpan={row.original._groupSize} className="px-4 py-2">
          {row.getValue('boss2_due_date') ? new Date(row.getValue('boss2_due_date')).toLocaleDateString() : ''}
        </td>
      ),
      size: 50,
    },
    {
      accessorKey: 'boss3_due_date',
      enableSorting: true,
      header: 'Дата начальника3???',
      cell: ({ row }) => row.original._isFirst && (
        <td rowSpan={row.original._groupSize} className="px-4 py-2">
          {row.getValue('boss3_due_date') ? new Date(row.getValue('boss3_due_date')).toLocaleDateString() : ''}
        </td>
      ),
      size: 50,
    },
    {
      accessorKey: 'person',
      enableSorting: false,
      header: 'Ответственный',
      cell: ({ row }) => <td className="px-4 py-2">{row.getValue('person')}</td>,
      size: 50,
    },
    {
      accessorKey: 'due_date',
      enableSorting: false,
      header: 'Дата',
      cell: ({ row }) => <td className="px-4 py-2">
        {row.getValue('due_date')}
      </td>,
      size: 50,
    },
    {
      accessorKey: 'closed_date',
      enableSorting: false,
      header: 'Дата закрытия',
      cell: ({ row }) => <td className="px-4 py-2">
        {row.getValue('closed_date')}
      </td>,
      size: 50,
    }
  ], []);


  const table = useReactTable({
    data: filteredData,
    columns,
    state: {
      sorting,
    },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    debugTable: false, // Отключите в продакшене
  });

  return (
    <div className="relative flex flex-col h-[calc(100vh-3.5rem)] bg-neutral-100 w-full">
      <div className="p-4">
        <select 
          value={selectedPerson || ''}
          onChange={(e) => setSelectedPerson(e.target.value || null)}
          className="p-2 border rounded"
        >
          <option value="">Все ответственные</option>
          {personOptions.map(person => (
            <option key={person} value={person}>{person}</option>
          ))}
        </select>
      </div>
      
      <div className="overflow-auto rounded-md border h-full scrollbar-custom">
        <table className="text-sm w-full border-collapse bg-white">
          <thead className="bg-gray-50 sticky top-0">
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id} className="hover:bg-muted/50 transition-colors">
                {headerGroup.headers.map((header) => {
                  const isSelectColumn = !['dgi_number', 'date', 'description', "executor_due_date", "boss_due_date", "boss2_due_date", "boss3_due_date"].includes(header.id); 
                  
                  return (
                    <th
                      key={header.id}
                      onClick={!isSelectColumn ? header.column.getToggleSortingHandler() : undefined} // Отключаем сортировку для первой колонки
                      className="px-2 py-3 border-b-2 border-gray-300 text-left text-sm font-semibold text-gray-600 tracking-wider cursor-pointer hover:bg-gray-50"
                      style={{ width: `${header.column.columnDef.size}px` }}
                    >
                      <div className="flex items-center">
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        
                        {/* Показываем иконки сортировки только для колонок, не являющихся первой */}
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
            {table.getRowModel().rows.map(row => (
              <tr key={row.id} className="bg-white border-b hover:bg-gray-50">
                {row.getVisibleCells().map(cell => 
                  flexRender(cell.column.columnDef.cell, cell.getContext())
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};