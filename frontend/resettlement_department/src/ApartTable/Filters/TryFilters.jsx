import React, { useEffect } from "react";
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
        maxFloor
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
                    <div className="mb-2">
                        <DropdownFilter 
                            item={'АО'} 
                            data={Object.keys(data)} 
                            func={handleFilterChange}
                            filterType={'district'} 
                            isFiltersReset={filtersResetFlag} 
                            filters={filters}
                        />
                    </div>
                    <div className="mb-2">
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
                    <div className="mb-2">
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
                    <div className="mb-2">
                        <div className="flex gap-4">
                            <div className="flex items-center gap-2">
                                <label>Площ. жил. от:</label>
                                <input
                                value={firstMinArea}
                                onChange={(e) => setFirstMinArea(e.target.value)}
                                className="w-14 px-2 py-1 border rounded"
                                placeholder=""
                                step="0.1"
                                />
                            </div>
                            <div className="flex items-center gap-2">
                                <label>до:</label>
                                <input
                                value={firstMaxArea}
                                onChange={(e) => setFirstMaxArea(e.target.value)}
                                className="w-14 px-2 py-1 border rounded"
                                placeholder=""
                                step="0.1"
                                />
                            </div>
                        </div>
                    </div>
                    <div className="mb-2">
                        <div className="flex gap-4">
                            <div className="flex items-center gap-2">
                                <label>Общ. площ. от:</label>
                                <input
                                value={secondMinArea}
                                onChange={(e) => setSecondMinArea(e.target.value)}
                                className="w-14 px-2 py-1 border rounded"
                                placeholder=""
                                step="0.1"
                                />
                            </div>
                            <div className="flex items-center gap-2">
                                <label>до:</label>
                                <input
                                value={secondMaxArea}
                                onChange={(e) => setSecondMaxArea(e.target.value)}
                                className="w-14 px-2 py-1 border rounded"
                                placeholder=""
                                step="0.1"
                                />
                            </div>
                        </div>
                    </div>
                    <div className="mb-2">
                        <div className="flex gap-4">
                            <div className="flex items-center gap-2">
                                <label>Жил. площ. от:</label>
                                <input
                                value={thirdMinArea}
                                onChange={(e) => setThirdMinArea(e.target.value)}
                                className="w-14 px-2 py-1 border rounded"
                                placeholder=""
                                step="0.1"
                                />
                            </div>
                            <div className="flex items-center gap-2">
                                <label>до:</label>
                                <input
                                value={thirdMaxArea}
                                onChange={(e) => setThirdMaxArea(e.target.value)}
                                className="w-14 px-2 py-1 border rounded"
                                placeholder=""
                                step="0.1"
                                />
                            </div>
                        </div>
                    </div>
                    <div className="mb-2">
                        <div className="flex gap-4">
                            <div className="flex items-center gap-2">
                                <label>Этаж от:</label>
                                <input
                                value={minFloor}
                                onChange={(e) => setMinFloor(e.target.value)}
                                className="w-14 px-2 py-1 border rounded"
                                placeholder=""
                                step="0.1"
                                />
                            </div>
                            <div className="flex items-center gap-2">
                                <label>до:</label>
                                <input
                                value={maxFloor}
                                onChange={(e) => setMaxFloor(e.target.value)}
                                className="w-14 px-2 py-1 border rounded"
                                placeholder=""
                                step="0.1"
                                />
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