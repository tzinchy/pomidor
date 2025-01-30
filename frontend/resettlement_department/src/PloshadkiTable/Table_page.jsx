import React, { useMemo, useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import Filters from '../Filters/Filters';
import Table from './Table/Table';
import Aside from "../Navigation/Aside";

// Кастомный хук для дебаунса
const useDebounce = (value, delay) => {
    const [debouncedValue, setDebouncedValue] = useState(value);
    
    useEffect(() => {
      const handler = setTimeout(() => {
        setDebouncedValue(value);
      }, delay);
      
      return () => {
        clearTimeout(handler);
      };
    }, [value, delay]);
  
    return debouncedValue;
  };

// Оптимизированный хук для работы с URL
const useUrlState = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  
  const params = useMemo(() => 
    Object.fromEntries(searchParams.entries()), 
  [searchParams]);

  const value = useMemo(() => ({
    okrugs: params.okrugs?.split(',') || [],
    districts: params.districts?.split(',') || [],
    deviation: params.deviation?.split(',') || [],
    otsel_type: params.otsel_type?.split(',') || [],
    relocationAge: params.relocationAge?.split(',') || [],
  }), [params]);

  const searchQuery = params.search || "";

  const updateUrl = React.useCallback((newParams) => {
    const updatedParams = { ...params, ...newParams };
    
    // Очистка пустых значений
    Object.entries(updatedParams).forEach(([key, val]) => {
      if (!val || (Array.isArray(val) && val.length === 0)) {
        delete updatedParams[key];
      } else if (Array.isArray(val)) {
        updatedParams[key] = val.join(',');
      }
    });

    setSearchParams(updatedParams);
  }, [params, setSearchParams]);

  return { value, searchQuery, updateUrl };
};

export default function TablePage() {
    const { value, searchQuery, updateUrl } = useUrlState();
    const [isFiltersReset, setIsFiltersReset] = useState(false);
    const [localSearch, setLocalSearch] = useState(searchQuery);
    const debouncedSearch = useDebounce(localSearch, 300);

  // Синхронизация дебаунс-поиска с URL
  useEffect(() => {
    updateUrl({ search: debouncedSearch });
  }, [debouncedSearch, updateUrl]);

  const handleSearchChange = (e) => {
    setLocalSearch(e.target.value);
  };

  const handleValueSelect = (type, selectedValues) => {
    setIsFiltersReset(false);
    updateUrl({ 
      [type]: selectedValues,
      page: undefined 
    });
  };

  const resetFilters = () => {
    setIsFiltersReset(true);
    setLocalSearch('');
    updateUrl({
      okrugs: undefined,
      districts: undefined,
      deviation: undefined,
      otsel_type: undefined,
      relocationAge: undefined,
      search: undefined,
    });
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
          currentSearch={localSearch}
        />
        <Table 
          filters={value} 
          searchQuery={debouncedSearch} 
        />
      </main>
    </div>
  );
}