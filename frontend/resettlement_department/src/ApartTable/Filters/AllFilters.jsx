import React, { useState } from "react";
import DropdownFilter from "./DropdownFilter";
import MunicipalDropdownFilter from "./MunicipalDropdownFilter";
import SearchTry from "./SearchTry";

export default function AllFilters({ handleFilterChange, rooms, matchCount, apartType, filtersResetFlag, handleResetFilters, isQueueChecked, setIsQueueChecked, setSearchQuery, filters, filterData }) {
    const StatusFilters = ['Не подобрано', "Согласие", 'Отказ', "Суд", "Фонд компенсация", "Фонд докупка", "Ожидание", 'Ждёт одобрения'];

    const handleQueueChange = (e) => {
        const isChecked = e.target.checked;
        setIsQueueChecked(isChecked);
        handleFilterChange('is_queue', isChecked ? [1] : [0, 1]);
    };

    return (
        <div className="flex">
            {/*<SearchTry placeholder={'Поиск по адреу'} setSearchQuery={setSearchQuery} />*/}
            <DropdownFilter 
                item={'АО'} 
                data={Object.keys(filterData)} 
                func={handleFilterChange}
                filterType={'district'} 
                isFiltersReset={filtersResetFlag} 
            />
            <MunicipalDropdownFilter
                item={'Район'} 
                data={filterData} 
                func={handleFilterChange}
                filterType={'municipal_district'} 
                isFiltersReset={filtersResetFlag} 
                filters={filters}
                showAddresses={false}
            />
            <MunicipalDropdownFilter 
                item={'Дом'} 
                data={filterData} 
                func={handleFilterChange}
                filterType={'house_address'} 
                isFiltersReset={filtersResetFlag} 
                filters={filters}
                showAddresses={true}
            />
            <DropdownFilter 
                item={'Статус'} 
                data={StatusFilters} 
                func={handleFilterChange}
                filterType={'status'} 
                isFiltersReset={filtersResetFlag} 
            />
            <DropdownFilter 
                item={'Комнаты'} 
                data={rooms} 
                func={handleFilterChange}
                filterType={'room_count'} 
                isFiltersReset={filtersResetFlag} 
            />
            <DropdownFilter 
                item={'Кол-во подборов'} 
                data={matchCount} 
                func={handleFilterChange}
                filterType={'selection_count'} 
                isFiltersReset={filtersResetFlag} 
            />
            {apartType === 'OldApart' ? (
                <div className="flex">
                    <label className="font-medium flex items-center mr-4 bg-white border border-dashed border-input hover:bg-gray-100 rounded-md px-3 h-8 cursor-pointer">
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
            ) : null}
            {/* Кнопка "Сбросить фильтры" */}
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
    );
}