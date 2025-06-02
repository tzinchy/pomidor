import React, { useState, useRef, useMemo, useEffect, useCallback } from 'react';
import { Menu, Transition } from '@headlessui/react';
import { Fragment } from 'react';
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
import NotesCell from './Cells/Notes';
import ApartDetails from './ApartDetails';
import { HOSTLINK } from '..';
import AllFilters from './Filters/AllFilters';
import ProgressStatusBar from './Try';
import StageCell from './Cells/StageCell';

// Добавьте SVG для иконки меню
const MenuIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-menu">
    <line x1="4" y1="12" x2="20" y2="12" />
    <line x1="4" y1="6" x2="20" y2="6" />
    <line x1="4" y1="18" x2="20" y2="18" />
  </svg>
);

const ApartTable = ({ data, loading, selectedRow, setSelectedRow, isDetailsVisible, setIsDetailsVisible, apartType, 
  fetchApartmentDetails, apartmentDetails, collapsed, lastSelectedMunicipal, lastSelectedAddres, fetchApartments, filters, setFilters, rowSelection, setRowSelection,
  setApartType, setLoading, setCollapsed}) => {
  const [globalFilter, setGlobalFilter] = useState('');
  const [sorting, setSorting] = useState([]);
  const tableContainerRef = useRef(null);
  const [filteredApartments, setFilteredApartments] = useState(data);
  const [matchCount, setMatchCount] = useState([]);
  const [selectedRowId, setSelectedRowId] = useState();
  const [rooms, setRooms] = useState([]);
  const [filtersResetFlag, setFiltersResetFlag] = useState(false);
  const [isQueueChecked, setIsQueueChecked] = useState(false);
  const [filterData, setFilterData] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [firstMinArea, setFirstMinArea] = useState("");
  const [firstMaxArea, setFirstMaxArea] = useState("");
  const [secondMinArea, setSecondMinArea] = useState(""); 
  const [secondMaxArea, setSecondMaxArea] = useState(""); 
  const [thirdMinArea, setThirdMinArea] = useState(""); 
  const [thirdMaxArea, setThirdMaxArea] = useState(""); 
  const [minFloor, setMinFloor] = useState("");
  const [maxFloor, setMaxFloor] = useState("");
  const [searchApartQuery, setSearchApartQuery] = useState("");
  const [searchFioQuery, setSearchFioQuery] = useState("");
  const [searchNotesQuery, setSearchNotesQuery] = useState("");
  const [typeOfSettlement, setTypeOfSettlement] = useState([]);
  const [minPeople, setMinPeople] = useState([]);
  const [maxPeople, setMaxPeople] = useState([]);
  const [filterStatuses, setFilterStatuses] = useState([]);
  const [allStatuses, setAllStatuses] = useState(null)

  const statuses = apartType === 'OldApart' ? ["Согласие", "Суд", "МФР Компенсация", "МФР Докупка", "Ждёт одобрения",  "Подготовить смотровой", "Ожидание", "МФР (вне района)", "МФР Компенсация (вне района)", "Подборов не будет"] : ["Резерв", "Блок", "Свободная", "Передано во вне"];
  
  // Получаем уникальные значения room_count
  const getUniqueValues = useMemo(() => {
    if (!data) return [];

    return (x) => {
        return [...new Set(
          data
            .map(apartment => parseInt(apartment[x], 10)) // Используем параметр x
            .filter(value => !isNaN(value))
        )].sort((a, b) => a - b);
    };
  }, [data]);

  // Получаем уникальные строковые значения
  const getUniqueStringValues = useMemo(() => {
    if (!data) return [];
  
    return (x) => {
      return [...new Set(
        data
          .map(apartment => {
            // Получаем и обрабатываем значение свойства
            let value = apartment[x]?.toString().trim();
            
            // Специальная обработка для статусов
            if (x === "status" && !value) {
              value = apartType === "OldApart" ? "Не подобрано" : "Свободная";
            }
            
            return value;
          })
          // Фильтрация пустых и неопределенных значений
          .filter(value => value && value !== "undefined")
      )].sort((a, b) => a.localeCompare(b)); // Сортировка по алфавиту
    };
  }, [data]);


  // Обновляем rooms при изменении filteredApartments
  useEffect(() => {
    setRooms(getUniqueValues('room_count'));
    setMatchCount(getUniqueValues('selection_count'));
    setTypeOfSettlement(getUniqueStringValues('type_of_settlement'));
    setFilterStatuses(getUniqueStringValues('status'));
    console.log('filterStatuses', filterStatuses);
  }, [getUniqueValues]);


  const getFilteData = (data) => {
    if (!data) return {};
  
    const result = {};
  
    data.forEach(apartment => {
      const { district, municipal_district, house_address } = apartment;
  
      if (!district || !municipal_district || !house_address) return;
  
      if (!result[district]) {
        result[district] = {};
      }
  
      if (!result[district][municipal_district]) {
        result[district][municipal_district] = new Set();
      }
  
      result[district][municipal_district].add(house_address);
    });
  
    // Преобразуем Set в массив для удобства
    for (const district in result) {
      for (const municipal_district in result[district]) {
        result[district][municipal_district] = Array.from(result[district][municipal_district]);
      }
    }
  
    return result;
  };

  const countStatuses = (data) => {
    return data.reduce((acc, item) => {
      const status = item.status;
      if (status) {
        acc[status] = (acc[status] || 0) + 1;
      }
      return acc;
    }, {});
  };

  // 2. Добавляем эффект для синхронизации с исходными данными
  useEffect(() => {
    setFilteredApartments(data);
    setFilterData(getFilteData(data));
    setAllStatuses(countStatuses(data))
    console.log(data);
  }, [data]);
  
  const handleFilterChange = useCallback((filterType, selectedValues) => {
    // Обновляем состояние фильтров
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

  // Используем useEffect для отслеживания изменений filters
  useEffect(() => {
    console.log('filters updated:', filters);
  }, [filters]);

  // Применение всех фильтров к данным
  useEffect(() => {
    if (!data || data.length === 0) return;

    let filtered = data;

    if (searchApartQuery) {
      filtered = filtered.filter((item) => 
        apartType === 'OldApart'
          ? item.apart_number?.toLowerCase().includes(searchApartQuery.toLowerCase())
          : String(item.apart_number || '').toLowerCase().includes(searchApartQuery.toLowerCase())
      );
    }

    if (searchFioQuery) {
      filtered = filtered.filter((item) => {
          return (
              item.fio?.toLowerCase().includes(searchFioQuery.toLowerCase())
          );
      });
    }

    if (searchNotesQuery) {
      filtered = filtered.filter((item) => {
          return (
              item.notes?.toLowerCase().includes(searchNotesQuery.toLowerCase())
          );
      });
    }

    // Фильтрация по full_living_area (firstMinArea/firstMaxArea)
    if (firstMinArea || firstMaxArea) {
      filtered = filtered.filter((item) => {
        const area = parseFloat(item.full_living_area);
        const min = parseFloat(firstMinArea);
        const max = parseFloat(firstMaxArea);
  
        let valid = true;
        if (!isNaN(min)) valid = valid && area >= min;
        if (!isNaN(max)) valid = valid && area <= max;
        return valid;
      });
    }
  
    // Фильтрация по total_living_area (secondMinArea/secondMaxArea)
    if (secondMinArea || secondMaxArea) {
      filtered = filtered.filter((item) => {
        const area = parseFloat(item.total_living_area);
        const min = parseFloat(secondMinArea);
        const max = parseFloat(secondMaxArea);
  
        let valid = true;
        if (!isNaN(min)) valid = valid && area >= min;
        if (!isNaN(max)) valid = valid && area <= max;
        return valid;
      });
    }
  
    // Фильтрация по living_area (thirdMinArea/thirdMaxArea)
    if (thirdMinArea || thirdMaxArea) {
      filtered = filtered.filter((item) => {
        const area = parseFloat(item.living_area);
        const min = parseFloat(thirdMinArea);
        const max = parseFloat(thirdMaxArea);
  
        let valid = true;
        if (!isNaN(min)) valid = valid && area >= min;
        if (!isNaN(max)) valid = valid && area <= max;
        return valid;
      });
    }

    // Фильтрация по этажу
    if (minFloor || maxFloor) {
      filtered = filtered.filter((item) => {
        const floor = parseFloat(item.floor);
        const min = parseFloat(minFloor);
        const max = parseFloat(maxFloor);
  
        let valid = true;
        if (!isNaN(min)) valid = valid && floor >= min;
        if (!isNaN(max)) valid = valid && floor <= max;
        return valid;
      });
    }
    
    if (minPeople || maxPeople) {
      filtered = filtered.filter((item) => {
        const people = parseFloat(item.people_v_dele);
        const min = parseFloat(minPeople);
        const max = parseFloat(maxPeople);
  
        let valid = true;
        if (!isNaN(min)) valid = valid && people >= min;
        if (!isNaN(max)) valid = valid && people <= max;
        return valid;
      });
    }
    

      // Применяем каждый фильтр
      Object.entries(filters).forEach(([filterType, selectedValues]) => {
        if (selectedValues.length > 0) {
          const filterKey = filterType.toLowerCase();

          filtered = filtered.filter((item) => {
            // Проверяем все выбранные значения фильтра
            for (const val of selectedValues) {
                // Если это специальное значение ("Не подобрано" или "Свободная")
                if (val === "Не подобрано" || val === "Свободная") {
                    // Проверяем либо точное совпадение, либо null
                    if (item[filterKey] === val || item[filterKey] === null) {
                        return true;
                    }
                } 
                // Для обычных значений
                else if (item[filterKey] === val) {
                    return true;
                }
            }
            return false;
          });
        }
      });

      setFilteredApartments(filtered);
  }, [data, filters, firstMinArea, firstMaxArea, secondMinArea, secondMaxArea, thirdMinArea, thirdMaxArea, minFloor, maxFloor, minPeople, maxPeople, searchApartQuery, searchFioQuery, searchNotesQuery]);

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
        {
          first_apart_id: parseInt(Object.keys(rowSelection)[0]),
          second_apart_id: parseInt(Object.keys(rowSelection)[1])
        }
      );
    } catch (error) {
      console.error("Error ", error.response?.data);
    }
  };

  const setStatusForMany = async (status) => {
    const apartmentIds = Object.keys(rowSelection).map(id => parseInt(id, 10));
    console.log('setStatusForMany', apartmentIds, status, apartType)
    
    try {
      await axios.patch(
        `${HOSTLINK}/tables/apartment/set_status_for_many`,
        { 
          apart_ids: apartmentIds,
          status: status 
        },
        { 
          headers: { 'Content-Type': 'application/json' },
          params: {
            apart_type: apartType
          }
        }
      );
      
      fetchApartments(lastSelectedAddres, lastSelectedMunicipal);
    } catch (error) {
      console.error("Error setting status:", error.response?.data);
    }
  };

  const setSpecialNeedsForMany = async (marker) => {
    const apartmentIds = Object.keys(rowSelection).map(id => parseInt(id, 10));
    console.log('setSpecialNeedsForMany', apartmentIds, marker, apartType)
    
    try {
      await axios.patch(
        `${HOSTLINK}/tables/apartment/set_special_needs_for_many`,
        { 
          apart_ids: apartmentIds,
          is_special_needs_marker: marker 
        }
      );
      
      fetchApartments(lastSelectedAddres, lastSelectedMunicipal);
    } catch (error) {
      console.error("Error setting status:", error.response?.data);
    }
  };

  const handleNotesSave = async (rowData, newNotes) => {
    try {
      await axios.patch(
        `${HOSTLINK}/apartment/${rowData.id}/notes`,
        { notes: newNotes }
      );
      // Обновить данные таблицы после успешного сохранения
      fetchApartments(lastSelectedAddres, lastSelectedMunicipal);
    } catch (error) {
      console.error("Ошибка при сохранении:", error);
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
            onClick={(e) => e.stopPropagation()}
            className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
          />
        ),
        cell: ({ row }) => (
          <input
            type="checkbox"
            checked={row.getIsSelected()}
            onChange={row.getToggleSelectedHandler()}
            onClick={(e) => e.stopPropagation()}
            className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
          />
        ),
        size: 30,
        enableSorting: false,
      },
      {
        header: 'Адрес',
        accessorKey: 'house_address',
        enableSorting: true,
        cell: ({ row }) => <AdressCell props={row.original} />,
        size: 200,
      },
      {
        header: '№ Кв.',
        accessorKey: 'apart_number',
        enableSorting: true,
        cell: ({ row }) => 
          <div className="text-xs">
            {row.original['apart_number']}
          </div>,
        size: 60,
      },
      ...(apartType === 'OldApart' ? [{
        header: 'ФИО',
        accessorKey: 'fio',
        enableSorting: true,
        cell: ({ row }) => <FamilyCell props={row.original} />,
        size: 100,
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
      ...(apartType === 'OldApart' ? [{
        header: 'Этап работы',
        accessorKey: 'classificator.stageName',
        cell: ({ row }) => <StageCell props={row.original} />,
        size: 140,
      }] : []),
      {
        header: "Примечания",
        accessorKey: "notes",
        cell: ({ row }) => (
          <NotesCell
            props={row.original}
            apartType={apartType}
            onSave={(rowData, newNotes) => handleNotesSave(rowData, newNotes)}
          />
        ),
        size: 230,
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
      setSelectedRowId(id);
    } else if (!visibility) {
      setSelectedRow(index);
      setCollapsed(true);
      setIsDetailsVisible(true);
      fetchApartmentDetails(id);
      setSelectedRowId(id);
    }
  };

  const handleResetFilters = () => {
    setFilters({});
    setIsQueueChecked(false);
    setFiltersResetFlag(prev => !prev); // Инвертируем флаг
    setFirstMinArea("");
    setFirstMaxArea("");
    setSecondMinArea("");
    setSecondMaxArea("");
    setThirdMinArea("");
    setThirdMaxArea("");
    setMinFloor("");
    setMaxFloor("");
    setSearchApartQuery("");
    setSearchFioQuery("");
    setSearchNotesQuery("");
    setTypeOfSettlement("");
    setMinPeople("");
    setMaxPeople("");
  };

  const changeApartType= (apType) => {
    if (apType !== apartType){
      setIsDetailsVisible(false); 
      setSelectedRow(false); 
      setApartType(apType); 
      setLoading(true); 
      setFilters({}); 
      setRowSelection({}); 
      setFiltersResetFlag(prev => !prev);
    }
  }
  

  return (
    <div className='bg-neutral-100 h-[calc(100vh-4rem)]'>
      <div className={`${collapsed ? 'ml-[25px]' : 'ml-[260px]'} flex flex-wrap items-center mb-2 justify-between`}>
      <div className='flex w-[30%] items-center justify-between'>
      <button
          onClick={() => setIsOpen(!isOpen)}
          className=""
        >
          <div className="relative">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              className="filter-icon"
            >
              <path
                d="M22 3H2L10 12.46V19L14 21V12.46L22 3Z"
                stroke="url(#filterGradient)"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <defs>
                <linearGradient
                  id="filterGradient"
                  x1="2"
                  y1="3"
                  x2="22"
                  y2="3"
                  gradientUnits="userSpaceOnUse"
                >
                  <stop stopColor="#3B82F6" />
                  <stop offset="1" stopColor="#8B5CF6" />
                </linearGradient>
              </defs>
            </svg>
          </div>
        </button>

        
          <AllFilters 
            handleFilterChange={handleFilterChange} 
            rooms={rooms} 
            matchCount={matchCount} 
            apartType={apartType} 
            filtersResetFlag={filtersResetFlag} 
            handleResetFilters={handleResetFilters}
            isQueueChecked={isQueueChecked}
            setIsQueueChecked={setIsQueueChecked}
            filters={filters}
            filterData={filterData}
            isOpen={isOpen}
            setIsOpen={setIsOpen}
            setFirstMinArea={setFirstMinArea}
            setFirstMaxArea={setFirstMaxArea}
            firstMinArea={firstMinArea}
            firstMaxArea={firstMaxArea}
            setSecondMinArea={setSecondMinArea}
            setSecondMaxArea={setSecondMaxArea}
            secondMinArea={secondMinArea}
            secondMaxArea={secondMaxArea}
            setThirdMinArea={setThirdMinArea}
            setThirdMaxArea={setThirdMaxArea}
            thirdMinArea={thirdMinArea}
            thirdMaxArea={thirdMaxArea}
            setMinFloor={setMinFloor}
            setMaxFloor={setMaxFloor}
            minFloor={minFloor}
            maxFloor={maxFloor}
            setSearchApartQuery={setSearchApartQuery}
            searchApartQuery={searchApartQuery}
            setSearchFioQuery={setSearchFioQuery}
            searchFioQuery={searchFioQuery}
            setSearchNotesQuery={setSearchNotesQuery}
            searchNotesQuery={searchNotesQuery}
            typeOfSettlement={typeOfSettlement}
            minPeople={minPeople}
            setMinPeople={setMinPeople}
            maxPeople={maxPeople} 
            setMaxPeople={setMaxPeople}
            filterStatuses={filterStatuses}
          />

          {allStatuses ? (
            <ProgressStatusBar data={allStatuses} />
          ) : (
            <div>Загрузка данных...</div>
          )}
        </div>
        
        <div className='flex items-center'>
            <Menu as="div" className="relative inline-block text-left z-[102]">
            <div>
              <Menu.Button className="bg-white hover:bg-gray-100 border border-dashed px-3 rounded whitespace-nowrap text-sm font-medium mx-2 h-8 flex items-center">
                <MenuIcon />
              </Menu.Button>
            </div>
            <Transition
              as={Fragment}
              enter="transition ease-out duration-100"
              enterFrom="transform opacity-0 scale-95"
              enterTo="transform opacity-100 scale-100"
              leave="transition ease-in duration-75"
              leaveFrom="transform opacity-100 scale-100"
              leaveTo="transform opacity-0 scale-95"
            >
              <Menu.Items 
                className="absolute right-0 mt-2 w-56 origin-top-right divide-y divide-gray-100 rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
                static // Добавляем static чтобы меню не закрывалось при взаимодействии с вложенными элементами
              >
                {apartType === 'OldApart' && (
                  <div className="px-1 py-1">
                  <Menu.Item>
                    {({ active }) => (
                      <button
                        onClick={rematch}
                        className={`${
                          active ? 'bg-gray-100' : ''
                        } group flex w-full rounded-md px-2 py-2 text-sm text-gray-900`}
                      >
                        Переподбор
                      </button>
                    )}
                  </Menu.Item>
                  <Menu.Item>
                    {({ active }) => (
                      <button
                        onClick={switchAparts}
                        className={`${
                          active ? 'bg-gray-100' : ''
                        } group flex w-full rounded-md px-2 py-2 text-sm text-gray-900`}
                      >
                        Поменять квартиры
                      </button>
                    )}
                  </Menu.Item>
                  <Menu.Item>
                    {({ active }) => (
                      <button
                        onClick={(e) => {setSpecialNeedsForMany(1)}}
                        className={`${
                          active ? 'bg-gray-100' : ''
                        } group flex w-full rounded-md px-2 py-2 text-sm text-gray-900`}
                      >
                        Проставить инвалидность
                      </button>
                    )}
                  </Menu.Item>
                  <Menu.Item>
                    {({ active }) => (
                      <button
                        onClick={(e) => {setSpecialNeedsForMany(0)}}
                        className={`${
                          active ? 'bg-gray-100' : ''
                        } group flex w-full rounded-md px-2 py-2 text-sm text-gray-900`}
                      >
                        Снять инвалидность
                      </button>
                    )}
                  </Menu.Item>
                  <Menu.Item>
                    {({ active }) => (
                      <button
                        onClick={(e) => {console.log('rowSelection', Object.keys(rowSelection).map(id => parseInt(id, 10)))}}
                        className={`${
                          active ? 'bg-gray-100' : ''
                        } group flex w-full rounded-md px-2 py-2 text-sm text-gray-900`}
                      >
                        Переподобранные квартиры
                      </button>
                    )}
                  </Menu.Item>
                  <Menu.Item>
                    {({ active }) => (
                      <button
                        onClick={(e) => {console.log('rowSelection', Object.keys(rowSelection).map(id => parseInt(id, 10)))}}
                        className={`${
                          active ? 'bg-gray-100' : ''
                        } group flex w-full rounded-md px-2 py-2 text-sm text-gray-900`}
                      >
                        Console
                      </button>
                    )}
                  </Menu.Item>
                  </div>
                )}
                <div className="px-1 py-1">
                  {/* Подменю статусов */}
                  <Menu>
                    {({ open }) => (
                      <div className="relative">
                        <Menu.Button
                          className={`${
                            open ? 'bg-gray-100' : ''
                          } group flex w-full rounded-md px-2 py-2 text-sm text-gray-900 justify-between items-center`}
                        >
                          <span>Изменить статус</span>
                        </Menu.Button>
                        
                        <Transition
                          show={open}
                          as={Fragment}
                          enter="transition ease-out duration-100"
                          enterFrom="transform opacity-0 scale-95"
                          enterTo="transform opacity-100 scale-100"
                          leave="transition ease-in duration-75"
                          leaveFrom="transform opacity-100 scale-100"
                          leaveTo="transform opacity-0 scale-95"
                        >
                          <Menu.Items 
                            static
                            className="absolute w-56 origin-top-left divide-y divide-gray-100 rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-10"
                          >
                            <div className="px-1 py-1">
                              {statuses.map((status) => (
                                <Menu.Item key={status}>
                                  {({ active }) => (
                                    <button
                                      onClick={(e) => {
                                        e.preventDefault();
                                        e.stopPropagation();
                                        setStatusForMany(status, apartType);
                                      }}
                                      className={`${
                                        active ? 'bg-gray-100' : ''
                                      } group flex w-full rounded-md px-2 py-2 text-sm text-gray-900`}
                                    >
                                      {status}
                                    </button>
                                  )}
                                </Menu.Item>
                              ))}
                            </div>
                          </Menu.Items>
                        </Transition>
                      </div>
                    )}
                  </Menu>
                </div>
              </Menu.Items>
            </Transition>
          </Menu>
          <p className='ml-8 mr-2 text-gray-400'>{filteredApartments.length}</p>
        </div>
      </div>
      <div className="relative flex flex-col lg:flex-row  w-full transition-all duration-300">
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
            {filteredApartments.length === 0 ? (
              <div className="flex-1 flex flex-col items-center justify-center bg-white rounded-md border p-8">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="48"
                  height="48"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="#9CA3AF"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="mx-auto mb-4"
                >
                  <circle cx="11" cy="11" r="8"></circle>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                  <line x1="11" y1="8" x2="11" y2="14"></line>
                  <line x1="8" y1="11" x2="14" y2="11"></line>
                </svg>
                <h3 className="text-lg font-medium text-gray-500 mb-2">Ничего не найдено</h3>
                <p className="text-gray-400 mb-4">Попробуйте изменить параметры фильтрации</p>
                <button
                  onClick={handleResetFilters}
                  className="px-4 py-2 bg-gray-100 text-gray-600 rounded-md hover:bg-gray-200 transition-colors"
                >
                  Сбросить фильтры
                </button>
              </div>
          ) : (
            <div className="flex flex-1 overflow-hidden">
            {/* Таблица */}
            <div
              className={` rounded-md h-[calc(100vh-4.7rem)] transition-all duration-300 ease-in-out  ${isDetailsVisible ? 'w-[55vw]' : 'flex-grow'}`}
            >
              <div
                ref={tableContainerRef}
                className={`${collapsed ? 'ml-[25px]' : 'ml-[260px]'} overflow-auto rounded-md border h-full w-[calc(100% - 25px)] transition-all ease-in-out scrollbar-custom`}
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
                                  className={`px-2 border-b border-gray-200 text-xs text-gray-700 truncate`}
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
                className={`ml-2 fixed inset-0 lg:static lg:inset-auto lg:overflow-auto lg:rounded-md lg:border transition-all duration-300 ease-in-out z-50 min-w-[650px] max-w-[650px]`}
              >
                <div className="fixed inset-0 bg-opacity-50 lg:bg-transparent lg:relative">
                  <div
                    className={`fixed min-w-[40.5vw] max-w-[40.5vw] h-[calc(100vh-4.7rem)] overflow-y-auto transform transition-transform duration-300 ease-in-out ${
                      isDetailsVisible ? 'translate-x-0' : 'translate-x-full'
                    }`}
                    style={{
                      WebkitOverflowScrolling: 'touch', // Поддержка мобильных устройств
                    }}
                  >
                    <div className="h-[calc(100vh-4.7rem)] flex flex-col">
                      <ApartDetails
                        apartmentDetails={apartmentDetails}
                        setIsDetailsVisible={setIsDetailsVisible}
                        apartType={apartType}
                        setSelectedRow={setSelectedRow}
                        selectedRowId={selectedRowId}
                        fetchApartments={fetchApartments}
                        lastSelectedAddres={lastSelectedAddres}
                        lastSelectedMunicipal={lastSelectedMunicipal}
                        fetchApartmentDetails={fetchApartmentDetails}
                        getFilteData={getFilteData}
                        className="flex-1" // Оставляем для гибкости внутри компонента
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>)}
          </div>
        )}
      </div>
    </div>
  );
};

export default ApartTable;