import {
createColumnHelper,
flexRender,
getCoreRowModel,
useReactTable,
getSortedRowModel,
} from '@tanstack/react-table';
import { useState, useEffect } from 'react';
import { HOSTLINK } from '.';

// 1. Определяем структуру данных
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

// 4. Создаем компонент таблицы
function DataTable() {
    const [data1, setData] = useState([])

    useEffect(() => { 
        fetch(`${HOSTLINK}/history`)
        .then((res) => res.json())
        .then((fetchedData) => {
            setData(fetchedData);
        });
    }, []);

    console.log('HISTORY', data1);

    const [data] = useState(() => [...defaultData]);
    const [sorting, setSorting] = useState([]);

    const table = useReactTable({
        data,
        columns,
        state: {
        sorting,
        },
        onSortingChange: setSorting,
        getCoreRowModel: getCoreRowModel(),
        getSortedRowModel: getSortedRowModel(),
    });

    return (
        <div className="p-2">
        <table className="w-full border-collapse">
            <thead>
            {table.getHeaderGroups().map(headerGroup => (
                <tr key={headerGroup.id}>
                {headerGroup.headers.map(header => (
                    <th 
                    key={header.id}
                    className="border-b p-2 text-left cursor-pointer hover:bg-gray-50"
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
                    </th>
                ))}
                </tr>
            ))}
            </thead>
            <tbody>
            {table.getRowModel().rows.map(row => (
                <tr key={row.id} className="hover:bg-gray-50">
                {row.getVisibleCells().map(cell => (
                    <td key={cell.id} className="border-b p-2">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                ))}
                </tr>
            ))}
            </tbody>
        </table>
        </div>
    );
}

// 5. Использование компонента
export default function Try() {
    return (
        <div className="p-4">
        <h1 className="text-2xl font-bold mb-4">Список пользователей</h1>
        <DataTable />
        </div>
    );
}