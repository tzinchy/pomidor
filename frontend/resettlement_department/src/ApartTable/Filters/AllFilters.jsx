import React, { useState } from "react";
import DropdownFilter from "./DropdownFilter";
import MunicipalDropdownFilter from "./MunicipalDropdownFilter";
import SearchTry from "./SearchTry";

export default function AllFilters({ 
    handleFilterChange, 
    rooms, 
    matchCount, 
    apartType, 
    filtersResetFlag, 
    handleResetFilters, 
    isQueueChecked, 
    setIsQueueChecked, 
    filters, 
    filterData,
    isOpen,
    setIsOpen,
    setFirstMinArea,
    setFirstMaxArea,
    firstMinArea,
    firstMaxArea,
    setSecondMinArea,
    setSecondMaxArea,
    secondMinArea,
    secondMaxArea,
    setThirdMinArea,
    setThirdMaxArea,
    thirdMinArea,
    thirdMaxArea,
    setMinFloor,
    setMaxFloor,
    minFloor,
    maxFloor,
    setSearchApartQuery,
    searchApartQuery,
    setSearchFioQuery,
    searchFioQuery,
    setSearchNotesQuery,
    searchNotesQuery,
    typeOfSettlement,
    minPeople,
    setMinPeople,
    maxPeople,
    setMaxPeople,
}) {
    const StatusFilters = ['Не подобрано', "Согласие", 'Отказ', "Суд", "Фонд компенсация", "Фонд докупка", "Ожидание", 'Ждёт одобрения'];

    const handleQueueChange = (e) => {
        const isChecked = e.target.checked;
        setIsQueueChecked(isChecked);
        handleFilterChange('is_queue', isChecked ? [1] : [0, 1]);
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[105] flex bg-black bg-opacity-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-6xl max-h-[50%] flex flex-col">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-bold">Фильтры</h2>
                    <button
                        onClick={() => {setIsOpen(!isOpen)}}
                        className="text-gray-500 hover:text-gray-700"
                        >
                        <span className="text-2xl">×</span>
                    </button>
                </div>
                <div className="flex flex-wrap gap-2 items-center">
                    {/* Поиск (если раскомментировать) */}
                    {/*<SearchTry placeholder={'Поиск по адресу'} setSearchQuery={setSearchQuery} />*/}
                    
                    {/* Фильтр АО */}
                    <div className="flex-shrink-0">
                        <DropdownFilter 
                            item={'АО'} 
                            data={Object.keys(filterData)} 
                            func={handleFilterChange}
                            filterType={'district'} 
                            isFiltersReset={filtersResetFlag} 
                            filters={filters}
                        />
                    </div>
                    
                    {/* Фильтр Район */}
                    <div className="flex-shrink-0">
                        <MunicipalDropdownFilter
                            item={'Район'} 
                            data={filterData} 
                            func={handleFilterChange}
                            filterType={'municipal_district'} 
                            isFiltersReset={filtersResetFlag} 
                            filters={filters}
                            showAddresses={false}
                        />
                    </div>
                    
                    {/* Фильтр Дом */}
                    <div className="flex-shrink-0">
                        <MunicipalDropdownFilter 
                            item={'Дом'} 
                            data={filterData} 
                            func={handleFilterChange}
                            filterType={'house_address'} 
                            isFiltersReset={filtersResetFlag} 
                            filters={filters}
                            showAddresses={true}
                        />
                    </div>
                    
                    {/* Фильтр Статус */}
                    <div className="flex-shrink-0">
                        <DropdownFilter 
                            item={'Статус'} 
                            data={StatusFilters} 
                            func={handleFilterChange}
                            filterType={'status'} 
                            isFiltersReset={filtersResetFlag} 
                            filters={filters}
                        />
                    </div>
                    
                    {/* Фильтр Комнаты */}
                    <div className="flex-shrink-0">
                        <DropdownFilter 
                            item={'Комнаты'} 
                            data={rooms} 
                            func={handleFilterChange}
                            filterType={'room_count'} 
                            isFiltersReset={filtersResetFlag} 
                            filters={filters}
                        />
                    </div>
                    
                    {/* Фильтр Кол-во подборов (только для OldApart) */}
                    {apartType === 'OldApart' && (
                        <div className="flex-shrink-0">
                            <DropdownFilter 
                                item={'Кол-во подборов'} 
                                data={matchCount} 
                                func={handleFilterChange}
                                filterType={'selection_count'} 
                                isFiltersReset={filtersResetFlag} 
                                filters={filters}
                            />
                        </div>
                    )}

                    <div className="flex-shrink-0">
                        <DropdownFilter 
                            item={'Тип пользования'} 
                            data={typeOfSettlement} 
                            func={handleFilterChange}
                            filterType={'type_of_settlement'} 
                            isFiltersReset={filtersResetFlag} 
                            filters={filters}
                        />
                    </div>
                    
                    {/* Чекбокс Очередники (только для OldApart) */}
                    {apartType === 'OldApart' && (
                        <div className="flex-shrink-0">
                            <label className="font-medium flex items-center bg-white border border-dashed border-input hover:bg-gray-100 rounded-md px-3 h-8 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={isQueueChecked}
                                    onChange={handleQueueChange}
                                    className="mr-2"
                                />
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
                                    className="lucide lucide-list-ordered mr-2 h-4 w-4"
                                >
                                    <line x1="10" y1="6" x2="21" y2="6"></line>
                                    <line x1="10" y1="12" x2="21" y2="12"></line>
                                    <line x1="10" y1="18" x2="21" y2="18"></line>
                                    <path d="M4 6h1v4"></path>
                                    <path d="M4 10h2"></path>
                                    <path d="M6 18H4c0-1 2-2 2-3s-1-1.5-2-1"></path>
                                </svg>
                                Очередники
                            </label>
                        </div>
                    )}
                    
                    <div className="grid grid-cols-5 gap-4">
                        {/* Площадь жилая */}
                        <div className="flex items-center gap-2">
                            <label className="w-24">Площ. жил.:</label>
                            <div className="flex gap-2 flex-1">
                                <input
                                    value={firstMinArea}
                                    onChange={(e) => setFirstMinArea(e.target.value)}
                                    className="w-full px-2 py-1 border rounded"
                                    placeholder="от"
                                    step="0.1"
                                />
                                <input
                                    value={firstMaxArea}
                                    onChange={(e) => setFirstMaxArea(e.target.value)}
                                    className="w-full px-2 py-1 border rounded"
                                    placeholder="до"
                                    step="0.1"
                                />
                            </div>
                        </div>

                        {/* Общая площадь */}
                        <div className="flex items-center gap-2">
                            <label className="w-24">Общ. площ.:</label>
                            <div className="flex gap-2 flex-1">
                                <input
                                    value={secondMinArea}
                                    onChange={(e) => setSecondMinArea(e.target.value)}
                                    className="w-full px-2 py-1 border rounded"
                                    placeholder="от"
                                    step="0.1"
                                />
                                <input
                                    value={secondMaxArea}
                                    onChange={(e) => setSecondMaxArea(e.target.value)}
                                    className="w-full px-2 py-1 border rounded"
                                    placeholder="до"
                                    step="0.1"
                                />
                            </div>
                        </div>

                        {/* Жилая площадь */}
                        <div className="flex items-center gap-2">
                            <label className="w-24">Жил. площ.:</label>
                            <div className="flex gap-2 flex-1">
                                <input
                                    value={thirdMinArea}
                                    onChange={(e) => setThirdMinArea(e.target.value)}
                                    className="w-full px-2 py-1 border rounded"
                                    placeholder="от"
                                    step="0.1"
                                />
                                <input
                                    value={thirdMaxArea}
                                    onChange={(e) => setThirdMaxArea(e.target.value)}
                                    className="w-full px-2 py-1 border rounded"
                                    placeholder="до"
                                    step="0.1"
                                />
                            </div>
                        </div>

                        {/* Этаж */}
                        <div className="flex items-center gap-2">
                            <label className="w-24">Этаж:</label>
                            <div className="flex gap-2 flex-1">
                                <input
                                    value={minFloor}
                                    onChange={(e) => setMinFloor(e.target.value)}
                                    className="w-full px-2 py-1 border rounded"
                                    placeholder="от"
                                    step="1"
                                />
                                <input
                                    value={maxFloor}
                                    onChange={(e) => setMaxFloor(e.target.value)}
                                    className="w-full px-2 py-1 border rounded"
                                    placeholder="до"
                                    step="1"
                                />
                            </div>
                        </div>

                        {apartType === 'OldApart' && (
                            <div className="flex items-center gap-2">
                                <label className="w-24">Кол-во людей</label>
                                <div className="flex gap-2 flex-1">
                                    <input
                                        value={minPeople}
                                        onChange={(e) => setMinPeople(e.target.value)}
                                        className="w-full px-2 py-1 border rounded"
                                        placeholder="от"
                                        step="1"
                                    />
                                    <input
                                        value={maxPeople}
                                        onChange={(e) => setMaxPeople(e.target.value)}
                                        className="w-full px-2 py-1 border rounded"
                                        placeholder="до"
                                        step="1"
                                    />
                                </div>
                            </div>
                        )}
                    </div>
                </div>
                <div className="flex mt-4 gap-2">
                    <div className="mb-4">
                        <div className="relative">
                            <input
                                type="text"
                                value={searchApartQuery} // Используем searchQuery напрямую
                                onChange={(e) => setSearchApartQuery(e.target.value)} // Обновляем состояние в родителе
                                placeholder="Поиск по номеру квартиры"
                                className="w-[250px] px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                            {searchApartQuery && (
                                <button
                                    onClick={() => setSearchApartQuery("")} // Сбрасываем поиск в родителе
                                    className="relative right-5 text-gray-400 hover:text-gray-600"
                                >
                                    <svg
                                        xmlns="http://www.w3.org/2000/svg"
                                        width="16"
                                        height="16"
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        strokeWidth="2"
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        className="lucide lucide-x"
                                    >
                                        <path d="M18 6 6 18" />
                                        <path d="m6 6 12 12" />
                                    </svg>
                                </button>
                            )}
                        </div>
                    </div>
                    {apartType === 'OldApart' && (
                        <div className="mb-4">
                            <div className="relative">
                                <input
                                    type="text"
                                    value={searchFioQuery} // Используем searchQuery напрямую
                                    onChange={(e) => setSearchFioQuery(e.target.value)} // Обновляем состояние в родителе
                                    placeholder="Поиск по ФИО"
                                    className="w-[250px] px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                                {searchFioQuery && (
                                    <button
                                        onClick={() => setSearchFioQuery("")} // Сбрасываем поиск в родителе
                                        className="relative right-5 text-gray-400 hover:text-gray-600"
                                    >
                                        <svg
                                            xmlns="http://www.w3.org/2000/svg"
                                            width="16"
                                            height="16"
                                            viewBox="0 0 24 24"
                                            fill="none"
                                            stroke="currentColor"
                                            strokeWidth="2"
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            className="lucide lucide-x"
                                        >
                                            <path d="M18 6 6 18" />
                                            <path d="m6 6 12 12" />
                                        </svg>
                                    </button>
                                )}
                            </div>
                        </div>
                    )}
                    <div className="mb-4">
                        <div className="relative">
                            <input
                                type="text"
                                value={searchNotesQuery} // Используем searchQuery напрямую
                                onChange={(e) => setSearchNotesQuery(e.target.value)} // Обновляем состояние в родителе
                                placeholder="Поиск по примечаниям"
                                className="w-[250px] px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                            {searchNotesQuery && (
                                <button
                                    onClick={() => setSearchNotesQuery("")} // Сбрасываем поиск в родителе
                                    className="relative right-5 text-gray-400 hover:text-gray-600"
                                >
                                    <svg
                                        xmlns="http://www.w3.org/2000/svg"
                                        width="16"
                                        height="16"
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        strokeWidth="2"
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        className="lucide lucide-x"
                                    >
                                        <path d="M18 6 6 18" />
                                        <path d="m6 6 12 12" />
                                    </svg>
                                </button>
                            )}
                        </div>
                    </div>
                </div>
                <div className="flex-shrink-0 mt-2">
                    <button
                        onClick={handleResetFilters}
                        className="hover:bg-gray-200 inline-flex items-center justify-center whitespace-nowrap text-sm font-medium hover:bg-gray-100 rounded-md px-3 h-8 border-dashed"
                    >
                        Сброс
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
                            className="lucide lucide-x ml-2 h-4 w-4"
                        >
                            <path d="M18 6 6 18" />
                            <path d="m6 6 12 12" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    );
}