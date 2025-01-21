import React, { useState } from "react";
import { useSearchParams } from "react-router-dom";
import Filters from '../Filters/Filters';
import Table from './Table/Table';
import Aside from "../Navigation/Aside";

export default function Table_page() {
    const [searchParams, setSearchParams] = useSearchParams();
    const [isFiltersReset, setIsFiltersReset] = useState(false);

    // Инициализация значений из URL
    const [value, setValue] = useState({
        'okrugs': searchParams.getAll("okrugs") || [],
        'districts': searchParams.getAll("districts") || [],
        'deviation': searchParams.getAll("deviation") || [],
        'otsel_type': searchParams.getAll("otsel_type") || [],
        'relocationAge': searchParams.getAll("relocationAge") || [],
    });
    const [searchQuery, setSearchQuery] = useState(searchParams.get("search") || "");

    const handleSearchChange = (e) => {
        const value = e.target.value;
        setSearchQuery(value);
        updateUrl({ search: value });
    };

    const handleValueSelect = (type, selectedValues) => {
        const updatedValue = {
            ...value,
            [type]: selectedValues,
        };
        setValue(updatedValue);
        setIsFiltersReset(false); // Сбрасываем состояние "сброс фильтров"
        updateUrl({ [type]: selectedValues });
    };

    const resetFilters = () => {
        // Сбрасываем локальное состояние и флаги
        const resetValue = {
            'okrugs': [],
            'districts': [],
            'deviation': [],
            'otsel_type': [],
            'relocationAge': [],
        };
        setValue(resetValue);
        setSearchQuery("");
        setIsFiltersReset(true);

        // Обновляем URL только после сброса
        setTimeout(() => setSearchParams({}), 0);
    };

    const updateUrl = (newParams) => {
        const currentParams = Object.fromEntries(searchParams.entries());
        const updatedParams = { ...currentParams, ...newParams };

        // Удаляем пустые значения
        Object.keys(updatedParams).forEach((key) => {
            if (!updatedParams[key] || updatedParams[key].length === 0) {
                delete updatedParams[key];
            }
        });

        setSearchParams(updatedParams);
    };

    return (
        <div className="bg-muted/60 flex min-h-screen w-full flex-col">
            <Aside />
            <main className="relative flex flex-1 flex-col gap-2 p-2 sm:pl-16 bg-neutral-100">
                <Filters
                    handleValueSelect={handleValueSelect}
                    resetFilters={resetFilters}
                    isFiltersReset={isFiltersReset}
                    onSearch={handleSearchChange}
                />
                <Table filters={value} searchQuery={searchQuery} />
            </main>
        </div>
    );
}
