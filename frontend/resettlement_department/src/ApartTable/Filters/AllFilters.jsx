import React from "react";
import TryDropdown from "./DropdownFilter";

export default function AllFilters({handleFilterChange, rooms, matchCount}){
    const StatusFilters = ['Не подобрано', "Согласие", 'Отказ', "Суд", "Фонд компенсация", "Фонд докупка", "Ожидание",  'Ждёт одобрения']

    return (
        <div className="flex">
            <TryDropdown 
                item={'Статус'} 
                data={StatusFilters} 
                func={handleFilterChange}
                filterType={'status'} 
                isFiltersReset={false} 
            />
            <TryDropdown 
                item={'Комнаты'} 
                data={rooms} 
                func={handleFilterChange}
                filterType={'room_count'} 
                isFiltersReset={false} 
            />
            <TryDropdown 
                item={'Кол-во подборов'} 
                data={matchCount} 
                func={handleFilterChange}
                filterType={'selection_count'} 
                isFiltersReset={false} 
            />
        </div>
    )
}