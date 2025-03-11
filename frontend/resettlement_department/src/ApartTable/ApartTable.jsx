import React, { useState, useRef, useMemo, useEffect, useCallback } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  flexRender,
} from '@tanstack/react-table';
import axios from "axios";
import { useVirtualizer } from '@tanstack/react-virtual';
import AdressCell from './Cells/AdressCell';
import FamilyCell from './Cells/Fio';
import PloshCell from './Cells/PloshCell';
import StatusCell from './Cells/StatusCell';
import Notes from './Cells/Notes';
import ApartDetails from './ApartDetails';
import { HOSTLINK } from '..';
import AllFilters from './Filters/AllFilters';

const ApartTable = ({ data, loading, selectedRow, setSelectedRow, isDetailsVisible, setIsDetailsVisible, apartType, 
  fetchApartmentDetails, apartmentDetails, collapsed, lastSelectedMunicipal, lastSelectedAddres, fetchApartments }) => {
  const [globalFilter, setGlobalFilter] = useState('');
  const [sorting, setSorting] = useState([]);
  const [rowSelection, setRowSelection] = useState({});
  const tableContainerRef = useRef(null);
  const [filteredApartments, setFilteredApartments] = useState(data);
  const [rooms, setRooms] = useState([]);

  // Получаем уникальные значения room_count
  const getUniqueRoomCounts = useMemo(() => {
    console.log(data);
    if (!filteredApartments) return [];
    
    return [...new Set(
      filteredApartments
        .map(apartment => parseInt(apartment.room_count, 10))
        .filter(value => !isNaN(value))
    )].sort((a, b) => a - b);
  }, [filteredApartments]);

  // Обновляем rooms при изменении filteredApartments
  useEffect(() => {
    setRooms(getUniqueRoomCounts);
  }, [getUniqueRoomCounts]);

  // 2. Добавляем эффект для синхронизации с исходными данными
  useEffect(() => {
    setFilteredApartments(data);
  }, [data]);
  
  const handleFilterChange = useCallback((filterType, selectedValues) => {
    if (!data || data.length === 0) return;
  
    const filterKey = filterType.toLowerCase();
    
    const filtered = selectedValues.length > 0 
      ? data.filter(item => {
          // Проверяем наличие "Не подобрано" в выбранных значениях
          const hasNotMatched = selectedValues.includes('Не подобрано');
          // Проверяем обычные значения статусов
          const hasRegularStatus = selectedValues.some(val => val !== 'Не подобрано' && item[filterKey] === val);
          
          // Если выбран "Не подобрано" - проверяем на null, иначе проверяем обычные статусы
          return (hasNotMatched && item[filterKey] === null) || hasRegularStatus;
        })
      : data;
    setFilteredApartments(filtered);
  }, [data]);

  const rematch = async () => {
    const apartmentIds = Object.keys(rowSelection).map(id => parseInt(id, 10));
    try {
      await axios.post(
        `${HOSTLINK}/tables/apartment/rematch`,
        JSON.stringify({ apartment_ids: apartmentIds }),
        { headers: { 'Content-Type': 'application/json' } }
      );
      fetchApartments(lastSelectedAddres, lastSelectedMunicipal);
    } catch (error) {
      console.error("Error rematch:", error.response?.data);
    }
  };

  const switchAparts = async () => {
    if ((Object.keys(rowSelection).length > 2) || (apartType === 'NewApartment')) return;
    
    try {
      await axios.post(
        `${HOSTLINK}/tables/switch_aparts`,
        {},
        {
          params: {
            first_apart_id: parseInt(Object.keys(rowSelection)[0]),
            second_apart_id: parseInt(Object.keys(rowSelection)[1])
          }
        }
      );
    } catch (error) {
      console.error("Error ", error.response?.data);
    }
  };

  const columns = useMemo(
    () => [
      {
        id: 'select',
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
        size: 20,
        enableSorting: false,
      },
      {
        header: 'Адрес',
        accessorKey: 'house_address',
        enableSorting: true,
        cell: ({ row }) => <AdressCell props={row.original} />,
        size: 200,
      },
      ...(apartType === 'FamilyStructure' ? [{
        header: 'ФИО',
        accessorKey: 'fio',
        enableSorting: true,
        cell: ({ row }) => <FamilyCell props={row.original} />,
        size: 150,
      }] : []),
      {
        header: 'Площадь, тип, этаж',
        accessorKey: 'full_living_area',
        cell: ({ row }) => <PloshCell props={row.original} />,
        size: 120,
      },
      {
        header: 'Статус',
        accessorKey: 'status',
        cell: ({ row }) => <StatusCell props={row.original} />,
        size: 120,
      },
      {
        header: 'Примечания',
        accessorKey: 'notes',
        cell: ({ row }) => <Notes props={row.original} />,
        size: 250,
      },
    ],
    [apartType]
  );

  const table = useReactTable({
    data: filteredApartments, // Используем отфильтрованные данные
    columns,
    state: {
      globalFilter,
      sorting,
      rowSelection,
    },
    onGlobalFilterChange: setGlobalFilter,
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onRowSelectionChange: setRowSelection,
    getRowId: (row) => apartType === 'OldApart' 
      ? row.affair_id?.toString() 
      : row.new_apart_id?.toString(),
  });

  const rowVirtualizer = useVirtualizer({
    count: table.getRowModel().rows.length,
    estimateSize: () => 65,
    getScrollElement: () => tableContainerRef.current,
    overscan: 10,
  });

  const handleClick = (index, visibility, val) => {
    const id = apartType === "OldApart" 
      ? val.affair_id 
      : val.new_apart_id;
      
    if (visibility && index !== selectedRow) {
      setSelectedRow(index);
      fetchApartmentDetails(id);
    } else if (!visibility) {
      setSelectedRow(index);
      setIsDetailsVisible(true);
      fetchApartmentDetails(id);
    }
  };

  return (
    <div className='bg-neutral-100'>
      <div className={`${collapsed ? 'ml-[25px]' : 'ml-[260px]'} flex flex-wrap items-center mb-2 justify-between`}>
          <AllFilters handleFilterChange={handleFilterChange} rooms={rooms}/>
        <div className='flex'>
          <button 
              onClick={rematch}
              className="bg-white hover:bg-gray-100 border border-dashed px-3 rounded justify-center whitespace-nowrap text-sm font-medium mx-2 h-8"
            >
              Переподбор
            </button>

            <button 
              onClick={switchAparts}
              className="bg-white hover:bg-gray-100 border border-dashed px-3 rounded justify-center whitespace-nowrap text-sm font-medium mx-2 h-8"
            >
              Поменять подобранные квартиры
            </button>
          <p className='ml-8 mr-2 text-gray-400'>{filteredApartments.length}</p>
        </div>
      </div>
      <div className="relative flex flex-col lg:flex-row h-[calc(100vh-4rem)] w-full transition-all duration-300">
        {loading ? (
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
        ) : (
          <div className="flex flex-1 overflow-hidden">
            {/* Таблица */}
            <div
              className={` rounded-md h-full transition-all duration-300 ease-in-out  ${isDetailsVisible ? 'w-[80vw]' : 'flex-grow'}`}
            >
              <div
                ref={tableContainerRef}
                className={`${collapsed ? 'ml-[25px]' : 'ml-[260px]'} overflow-auto rounded-md border h-[calc(100vh-1rem)] w-[calc(100% - 25px)] transition-all ease-in-out scrollbar-custom`}
              >
                <table className="text-sm w-full border-collapse backdrop-blur-md sticky top-0 z-30">
                  <thead className="border-b z-10 backdrop-blur-md shadow z-10">
                  {table.getHeaderGroups().map((headerGroup) => (
                    <tr key={headerGroup.id} className="hover:bg-muted/50 transition-colors">
                      {headerGroup.headers.map((header) => {
                        const isSelectColumn = header.id === 'select'; // Проверяем, является ли колонка первой (с чекбоксами)
                        
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
                        onClick={() => handleClick(row.id, isDetailsVisible, row.original)}
                      >
                        <table className="w-full h-full table-fixed border-collapse">
                          <tbody>
                            <tr
                              className={`bg-white hover:bg-gray-100 ${
                                row.id === selectedRow ? 'bg-zinc-100' : 'hover:bg-gray-100'
                              } ${
                                (selectedRow || selectedRow === 0) && row.id !== selectedRow
                                  ? ''
                                  : ''
                              }`}
                            >
                              {row.getVisibleCells().map((cell) => (
                                <td
                                  key={cell.id}
                                  className="px-2 border-b border-gray-200 text-sm text-gray-700 truncate"
                                  style={{ width: `${cell.column.columnDef.size}px` }}
                                >
                                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
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

            {/* ApartDetails */}
            {apartmentDetails && isDetailsVisible && (
              <div
                className={`ml-2 bg-white fixed inset-0 lg:static lg:inset-auto lg:overflow-auto lg:rounded-md lg:border lg:h-[calc(100vh-1rem)] transition-all duration-300 ease-in-out z-50 min-w-[650px] max-w-[650px]`}
              >
                <div className="fixed inset-0 bg-opacity-50 lg:bg-transparent lg:relative">
                  <div
                    className={`fixed min-w-[650px] max-w-[650px] h-[calc(100vh-1rem)] overflow-y-auto transform transition-transform duration-300 ease-in-out ${
                      isDetailsVisible ? 'translate-x-0' : 'translate-x-full'
                    }`}
                    style={{
                      WebkitOverflowScrolling: 'touch', // Поддержка мобильных устройств
                    }}
                  >
                    <div className="h-[calc(100vh-1rem)] flex flex-col">
                      <ApartDetails
                        apartmentDetails={apartmentDetails}
                        setIsDetailsVisible={setIsDetailsVisible}
                        apartType={apartType}
                        setSelectedRow={setSelectedRow}
                        className="flex-1" // Оставляем для гибкости внутри компонента
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ApartTable;