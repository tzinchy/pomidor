import { useState, useEffect, useCallback } from "react";
import Aside from "../Navigation/Aside";
import CinTable from "./CinTable/CinTable";
import { HOSTLINK } from "..";
import CinFilters from "./CinFilters/CinFilters";
import ChangeCin from "./CinTable/ChangeCin";

export default function CinPage(){
    const [cinData, setCinData] = useState([]);
    const [filterData, setFilterData] = useState([]);
    const [filters, setFilters] = useState([]);
    const [filtersResetFlag, setFiltersResetFlag] = useState(false);
    const [filteredApartments, setFilteredApartments] = useState([]);

    const fetchData = async () => {
            try {
                const response = await fetch(`${HOSTLINK}/cin`, {
    credentials: 'include',});
                const fetchedData = await response.json();
                setCinData(fetchedData);
            } catch (error) {
                console.log('Error fetching cin: ', error);
            }
        };
        
    useEffect(() => { 
        fetchData();
    }, []);

    // Применение всех фильтров к данным
    useEffect(() => {
        if (!cinData || cinData.length === 0) return;

        let filtered = cinData;

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
    }, [cinData, filters]); 

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
                <div className="flex text-sm">
                    <CinFilters filterData={filterData} handleFilterChange={handleFilterChange} filtersResetFlag={filtersResetFlag} filters={filters} handleResetFilters={handleResetFilters} />
                    <ChangeCin fetchTableData={fetchData} type="create" />
                </div>
                <CinTable cinData={filteredApartments} fetchData={fetchData}/>
            </main>
        </div>
    )
}