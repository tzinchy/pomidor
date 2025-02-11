import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  flexRender,
} from '@tanstack/react-table';
import { useVirtualizer } from '@tanstack/react-virtual';
import { HOSTLINK } from '.';
import AdressCell from './ApartTable/Cells/AdressCell';
import FamilyCell from './ApartTable/Cells/Fio';
import PloshCell from './ApartTable/Cells/PloshCell';
import StatusCell from './ApartTable/Cells/StatusCell';
import Notes from './ApartTable/Cells/Notes';

const paramsSerializer = {
  indexes: null,
  encode: (value) => encodeURIComponent(value),
};

const fetchApartments = async (municipal_districts) => {
  try {
    const response = await axios.get(`${HOSTLINK}/tables/apartments`, {
      params: {
        apart_type: 'FamilyStructure',
        house_addresses: [],
        districts: [],
        municipal_districts: municipal_districts,
      },
      paramsSerializer,
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching apartments:', error.response?.data);
    throw error;
  }
};

const Try = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

  const columns = React.useMemo(
    () => [
      {
        header: 'Адрес дома',
        accessorKey: 'house_address',
        enableSorting: true,
        cell: ({ row }) => <AdressCell props={row.original} />,
        size: 200,
      },
      {
        header: 'ФИО',
        accessorKey: 'fio',
        enableSorting: true,
        cell: ({ row }) => <FamilyCell props={row.original} />,
        size: 100,
      },
      {
        header: 'Площадь, тип, этаж',
        accessorKey: 'full_living_area',
        cell: ({ row }) => <PloshCell props={row.original} />,
        size: 150,
      },
      {
        header: 'Статус',
        accessorKey: 'status',
        cell: ({ row }) => <StatusCell props={row.original} />,
        size: 100,
      },
      {
        header: 'Примечания',
        accessorKey: 'notes',
        cell: ({ row }) => <Notes props={row.original} />,
        size: 400,
      },
    ],
    []
  );

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const municipal_districts = ['Восточное Измайлово'];
        const fetchedData = await fetchApartments(municipal_districts);
        setData(fetchedData);
        console.log(fetchedData);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="App">
      <h1 className="text-2xl font-bold text-center my-4">Таблица квартир</h1>
      <Table columns={columns} data={data} loading={loading} />
    </div>
  );
};

const Table = ({ columns, data, loading }) => {
  const [globalFilter, setGlobalFilter] = useState('');
  const [sorting, setSorting] = useState([]);
  const tableContainerRef = useRef(null);

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

  const rowVirtualizer = useVirtualizer({
    count: table.getRowModel().rows.length,
    estimateSize: () => 65,
    getScrollElement: () => tableContainerRef.current,
    overscan: 10,
  });

  return (
    <div className="relative flex flex-col lg:flex-row h-[calc(100vh-1rem)] gap-2 bg-neutral-100 w-full transition-all duration-300">
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-[#01c5ad] border-solid"></div>
        </div>
      ) : (
        <div className={`overflow-auto rounded-md border h-full w-full transition-all duration-300 ease-in-out`}>
          <div
            ref={tableContainerRef}
            className="overflow-auto rounded-md border absolute left-0 h-[calc(100vh-1.5rem)] w-full transition-all ease-in-out scrollbar-custom"
          >
            <table className="text-base caption-bottom w-full border-collapse bg-white">
              <thead className="sticky top-0 bg-white z-10 backdrop-blur-md">
                {table.getHeaderGroups().map((headerGroup) => (
                  <tr key={headerGroup.id} className='hover:bg-muted/50 transition-colors'>
                    {headerGroup.headers.map((header) => (
                      <th
                        key={header.id}
                        onClick={header.column.getToggleSortingHandler()}
                        className="py-3 border-b-2 border-gray-300 text-left text-base font-semibold text-gray-600 tracking-wider cursor-pointer hover:bg-gray-50"
                        style={{ width: `${header.column.columnDef.size}px` }}
                      >
                        {console.log(header.column.columnDef.size)}
                        <div className="flex">
                          {flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                          {header.column.getIsSorted() === 'asc' ? (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-chevron-up h-4 w-4 -translate-x-[-25%] transition-transform scale-100"><path d="m18 15-6-6-6 6"></path></svg>) : 
                          header.column.getIsSorted() === 'desc' ? (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-chevron-up h-4 w-4 -translate-x-[-25%] transition-transform rotate-180 scale-100"><path d="m18 15-6-6-6 6"></path></svg>) : (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-chevrons-up-down text-muted-foreground/40 group-hover:text-muted-foreground ml-1 h-4 w-4 transition-transform scale-100"><path d="m7 15 5 5 5-5"></path><path d="m7 9 5-5 5 5"></path></svg>)}
                        </div>
                        
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
            </table>

            <div
              style={{
                height: `${rowVirtualizer.getTotalSize()}px`,
                position: 'relative',
              }}
            >
              {rowVirtualizer.getVirtualItems().map((virtualRow) => {
                const row = table.getRowModel().rows[virtualRow.index];
                return (
                  <div
                    key={row.id}
                    style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      width: '100%',
                      height: `${virtualRow.size}px`,
                      transform: `translateY(${virtualRow.start}px)`,
                    }}
                  >
                    <table className="w-full h-full table-fixed border-collapse">
                      <tbody>
                        <tr className="">
                          {row.getVisibleCells().map((cell) => (
                            <td
                              key={cell.id}
                              className=" border-b border-gray-200 text-base text-gray-700 truncate"
                              style={{ width: `${cell.column.columnDef.size}px` }}
                            >
                              {flexRender(
                                cell.column.columnDef.cell,
                                cell.getContext()
                              )}
                            </td>
                          ))}
                        </tr>
                      </tbody>
                    </table>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Table;