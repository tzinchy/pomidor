import React, { useEffect, useState } from "react";
import DropdownFilter from "./DropdownFilter";
import MunicipalDropdownFilter from "./MunicipalDropdownFilter";

export default function TryFilters({ 
    data, 
    isOpen, 
    onClose, 
    handleFilterChange, 
    filtersResetFlag, 
    filters, 
    handleResetFilters, 
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
    setSearchQuery,
    searchQuery,
    entranceSearchQuery,
    setEntranceSearchQuery
}){


    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-40 flex bg-black bg-opacity-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-6xl max-h-[50%] flex flex-col">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-bold">Фильтры</h2>
                    <button
                    onClick={onClose}
                    className="text-gray-500 hover:text-gray-700"
                    >
                    <span className="text-2xl">×</span>
                    </button>
                </div>
                <div>
                    <div className="flex flex-wrap gap-2 items-center mb-4">
                    <div className="flex-shrink-0">
                        <DropdownFilter 
                            item={'АО'} 
                            data={Object.keys(data)} 
                            func={handleFilterChange}
                            filterType={'district'} 
                            isFiltersReset={filtersResetFlag} 
                            filters={filters}
                        />
                    </div>
                    <div className="flex-shrink-0">
                        <MunicipalDropdownFilter
                            item={'Район'} 
                            data={data} 
                            func={handleFilterChange}
                            filterType={'municipal_district'} 
                            isFiltersReset={filtersResetFlag} 
                            filters={filters}
                            showAddresses={false}
                        />
                    </div>
                    <div className="flex-shrink-0">
                        <MunicipalDropdownFilter 
                            item={'Дом'} 
                            data={data} 
                            func={handleFilterChange}
                            filterType={'house_address'} 
                            isFiltersReset={filtersResetFlag} 
                            filters={filters}
                            showAddresses={true}
                        />
                    </div>
                </div>
                <div className="grid grid-cols-1 gap-4">
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
                    {/* Добавляем поисковую строку */}
                    <div className="mb-4">
                        <div className="relative">
                            <input
                                type="text"
                                value={searchQuery} // Используем searchQuery напрямую
                                onChange={(e) => setSearchQuery(e.target.value)} // Обновляем состояние в родителе
                                placeholder="Поиск по номеру квартиры"
                                className="w-[250px] px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                            {searchQuery && (
                                <button
                                    onClick={() => setSearchQuery("")} // Сбрасываем поиск в родителе
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

                    <div className="mb-4">
                        <div className="relative">
                            <input
                                type="text"
                                value={entranceSearchQuery} // Используем searchQuery напрямую
                                onChange={(e) => setEntranceSearchQuery(e.target.value)} // Обновляем состояние в родителе
                                placeholder="Поиск по номеру подъезда"
                                className="w-[250px] px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                            {searchQuery && (
                                <button
                                    onClick={() => setEntranceSearchQuery("")} // Сбрасываем поиск в родителе
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
    )
}