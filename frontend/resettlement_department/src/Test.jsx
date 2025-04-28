import { useReactTable, flexRender, getCoreRowModel } from '@tanstack/react-table';
import { TableHead } from './PloshadkiTable/Table/Components';

// Функция преобразования строки children_controls в массив
const parseChildren = (controls) => {
  if (Array.isArray(controls)) return controls;
  try {
    return JSON.parse(controls.replace(/\\"/g, '"'));
  } catch (e) {
    console.error('Parse error:', e);
    return [];
  }
};

// Преобразование исходных данных в плоскую структуру
const flattenData = (dataArray) => {
  return dataArray.flatMap(parent => {
    const children = parseChildren(parent.children_controls);
    return children.map((child, index) => ({
      ...parent,
      ...child,
      _parentId: parent.sedo_id,
      _isFirst: index === 0,
      _totalChildren: children.length
    }));
  });
};

// Определение колонок
const columns = [
  {
    accessorKey: 'dgi_number',
    header: 'ДГИ номер',
    cell: ({ row }) => row.original._isFirst ? (
      <td rowSpan={row.original._totalChildren}>
        {row.getValue('dgi_number')}
      </td>
    ) : null
  },
  {
    accessorKey: 'date',
    header: 'Дата',
    cell: ({ row }) => row.original._isFirst ? (
      <td rowSpan={row.original._totalChildren}>
        {new Date(row.getValue('date')).toLocaleDateString()}
      </td>
    ) : null
  },
  {
    accessorKey: 'person',
    header: 'Ответственный'
  },
  {
    accessorKey: 'due_date',
    header: 'Срок исполнения'
  },
  {
    accessorKey: 'closed_date',
    header: 'Дата закрытия'
  }
];

const headers = ['ДГИ номер', 'Дата', 'Ответственный', 'Срок исполнения', 'Дата закрытия']

// Основной компонент таблицы
export default function ParentChildTable({ data }) {
  const flatData = flattenData(data);
  
  const table = useReactTable({
    data: flatData,
    columns,
    getCoreRowModel: getCoreRowModel()
  });

  return (
    <div className="relative flex flex-col lg:flex-row h-[calc(100vh-3.5rem)] gap-2 bg-neutral-100 w-full transition-all duration-300">
      <div className="relative flex h-[calc(100vh-3.5rem)] w-full">
        <div className="overflow-auto rounded-md border absolute left-0 h-full transition-all ease-in-out w-[calc(100%)] scrollbar-custom">
          <table className="text-sm caption-bottom w-full border-collapse bg-white transition-all duration-300">
            <TableHead headers={headers} />
            <tbody>
              {table.getRowModel().rows.map(row => (
                <tr className="bg-white border-b transition-colors" key={row.id}>
                  {row.getVisibleCells().map(cell => 
                    flexRender(cell.column.columnDef.cell, cell.getContext())
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};