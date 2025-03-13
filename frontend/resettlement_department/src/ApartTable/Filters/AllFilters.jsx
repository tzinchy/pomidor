import React, { useState } from "react";
import DropdownFilter from "./DropdownFilter";

export default function AllFilters({handleFilterChange, rooms, matchCount, apartType}){
    const StatusFilters = ['Не подобрано', "Согласие", 'Отказ', "Суд", "Фонд компенсация", "Фонд докупка", "Ожидание", 'Ждёт одобрения'];
    const [isQueueChecked, setIsQueueChecked] = useState(false); // Состояние для чек-бокса "Очередники"

    // Обработчик изменения состояния чек-бокса
    const handleQueueChange = (e) => {
        const isChecked = e.target.checked;
        setIsQueueChecked(isChecked);
        handleFilterChange('is_queue', isChecked ? [1] : [0, 1]);
    };

    return (
        <div className="flex">
            <DropdownFilter 
                item={'Статус'} 
                data={StatusFilters} 
                func={handleFilterChange}
                filterType={'status'} 
                isFiltersReset={false} 
            />
            <DropdownFilter 
                item={'Комнаты'} 
                data={rooms} 
                func={handleFilterChange}
                filterType={'room_count'} 
                isFiltersReset={false} 
            />
            <DropdownFilter 
                item={'Кол-во подборов'} 
                data={matchCount} 
                func={handleFilterChange}
                filterType={'selection_count'} 
                isFiltersReset={false} 
            />
            {apartType === 'OldApart' ? (<div className="flex">
                <label className="flex items-center mr-4 bg-white border border-dashed border-input hover:bg-gray-100 rounded-md px-3 h-8 cursor-pointer">
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
            </div>) : null}
        </div>
    )
}