import { useState, useEffect, useMemo } from "react";
import axios from "axios";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  flexRender,
} from '@tanstack/react-table';
import { HOSTLINK } from "../..";

export default function CinTable() {
    const [cinData, setCinData] = useState([]);
    const [sorting, setSorting] = useState([]);
    const [columnFilters, setColumnFilters] = useState([]);
    
    const columns = useMemo(() => [
        {
            accessorKey: 'old_address',
            header: 'Адрес отселения',
        },
        {
            accessorKey: 'cin_address',
            header: 'Адрес ЦИНа',
        },
        {
            accessorKey: 'cin_schedule',
            header: 'График работы ЦИН',
        },
        {
            accessorKey: 'start_date',
            header: 'Дата начала работы',
        },
        {
            accessorKey: 'phone_osmotr',
            header: 'Телефон для осмотра',
        },
        {
            accessorKey: 'phone_otvet',
            header: 'Телефон для ответа',
        },
        {
            accessorKey: 'dep_schedule',
            header: 'График работы Департамента в ЦИНе',
        },
        {
            accessorKey: 'otdel',
            header: 'Адрес Отдела',
        },
    ], []);

    useEffect(() => { 
        fetch(`${HOSTLINK}/cin`)
        .then((res) => res.json())
        .then((fetchedData) => {
            setCinData(fetchedData);
            console.log(fetchedData);
        });
    }, []);

    const table = useReactTable({
        data: cinData,
        columns,
        state: {
            sorting,
            columnFilters,
        },
        onSortingChange: setSorting,
        onColumnFiltersChange: setColumnFilters,
        getCoreRowModel: getCoreRowModel(),
        getSortedRowModel: getSortedRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
    });
    
    return (
        <div className="relative flex flex-col lg:flex-row h-[96.8vh] gap-2 bg-neutral-100 w-full transition-all duration-300">
            <div className="relative flex w-full">
                <div className="overflow-auto rounded-md border absolute left-0 h-full transition-all ease-in-out w-[calc(100%)] scrollbar-custom">
                    <table className="text-sm caption-bottom w-full border-collapse bg-white transition-all duration-300">
                        <thead className="border-b shadow text-sm w-full border-collapse backdrop-blur-md sticky top-0 z-30">
                            {table.getHeaderGroups().map(headerGroup => (
                                <tr key={headerGroup.id}>
                                    {headerGroup.headers.map(header => (
                                        <th 
                                            key={header.id} 
                                            className="px-2 py-3 border-b-2 border-gray-300 text-left text-sm font-semibold text-gray-600 tracking-wider cursor-pointer hover:bg-gray-50"
                                            onClick={header.column.getToggleSortingHandler()}
                                        >
                                            <div className="flex items-center">
                                                {flexRender(header.column.columnDef.header, header.getContext())}
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
                                            </div>
                                        </th>
                                    ))}
                                </tr>
                            ))}
                        </thead>
                        <tbody>
                            {table.getRowModel().rows.length ? (
                                table.getRowModel().rows.map(row => (
                                    <tr key={row.id} className="border-b hover:bg-gray-50">
                                        {row.getVisibleCells().map(cell => (
                                            <td key={cell.id} className="p-4 pl-8">
                                                {flexRender(
                                                    cell.column.columnDef.cell,
                                                    cell.getContext()
                                                )}
                                            </td>
                                        ))}
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={columns.length} className="h-24 text-center">
                                        <div className="flex flex-1 justify-center h-64">
                                            <div className="relative flex flex-col place-items-center py-4 text-gray-500">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-cat stroke-muted-foreground h-12 w-12 stroke-1">
                                                    <path d="M12 5c.67 0 1.35.09 2 .26 1.78-2 5.03-2.84 6.42-2.26 1.4.58-.42 7-.42 7 .57 1.07 1 2.24 1 3.44C21 17.9 16.97 21 12 21s-9-3-9-7.56c0-1.25.5-2.4 1-3.44 0 0-1.89-6.42-.5-7 1.39-.58 4.72.23 6.5 2.23A9.04 9.04 0 0 1 12 5Z"></path>
                                                    <path d="M8 14v.5"></path>
                                                    <path d="M16 14v.5"></path>
                                                    <path d="M11.25 16.25h1.5L12 17l-.75-.75Z"></path>
                                                </svg>
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}