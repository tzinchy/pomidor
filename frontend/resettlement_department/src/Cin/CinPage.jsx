import { useState, useEffect, useCallback } from "react";
import Aside from "../Navigation/Aside";
import CinTable from "./CinTable/CinTable";
import { HOSTLINK } from "..";
import CinFilters from "./CinFilters/CinFilters";

export default function CinPage(){
    const [cinData, setCinData] = useState([]);
    const [filterData, setFilterData] = useState([]);
    const [filters, setFilters] = useState([]);
    const [filtersResetFlag, setFiltersResetFlag] = useState(false);

    useEffect(() => { 
        const fetchData = async () => {
            try {
                const response = await fetch(`${HOSTLINK}/cin`);
                const fetchedData = await response.json();
                setCinData(fetchedData);
            } catch (error) {
                console.log('Error fetching cin: ', error);
            }
        };
        
        fetchData();
    }, []);

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

    const handleResetFilters = () => {
        setFilters({});
        setFiltersResetFlag(prev => !prev); // Инвертируем флаг
    };

    useEffect(() => {
        setFilterData(getFilteData(cinData));
    }, [cinData])

    return (
        <div className="bg-muted/60 flex min-h-screen w-full flex-col">
            <Aside />
            <main className="relative flex flex-1 flex-col gap-2 p-2 sm:pl-16 bg-neutral-100">
                <CinFilters filterData={filterData} handleFilterChange={handleFilterChange} filtersResetFlag={filtersResetFlag} filters={filters} />
                <CinTable cinData={cinData} />
            </main>
        </div>
    )
}