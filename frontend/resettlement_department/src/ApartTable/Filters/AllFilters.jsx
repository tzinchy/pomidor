import React from "react";
import TryDropdown from "./DropdownFilter";
import { StatusFilters } from "./FiltersData";

export default function AllFilters({handleFilterChange, rooms}){
    return (
        <div className="flex">
            <TryDropdown 
                item={StatusFilters[0]} 
                data={StatusFilters[1]} 
                func={handleFilterChange} // Исправлено: Передаем обработчик фильтрации
                filterType={'status'} 
                isFiltersReset={false} 
            />
            <TryDropdown 
                item={'Комнаты'} 
                data={rooms} 
                func={handleFilterChange} // Исправлено: Передаем обработчик фильтрации
                filterType={'room_count'} 
                isFiltersReset={false} 
            />
            <TryDropdown 
                item={StatusFilters[0]} 
                data={StatusFilters[1]} 
                func={handleFilterChange} // Исправлено: Передаем обработчик фильтрации
                filterType={'status'} 
                isFiltersReset={false} 
            />
        </div>
    )
}