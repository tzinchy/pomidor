import DropdownFilter from "../../ApartTable/Filters/DropdownFilter";
import MunicipalDropdownFilter from "../../ApartTable/Filters/MunicipalDropdownFilter";
import ResetButton from "../../Filters/ResetFilters";

export default function CinFilters({ filterData, handleFilterChange, filtersResetFlag, filters, handleResetFilters }){
    return (
        <div className="flex w-full flex-wrap items-center justify-start gap-2">
            <DropdownFilter 
                item={'АО'} 
                data={Object.keys(filterData)} 
                func={handleFilterChange}
                filterType={'district'} 
                isFiltersReset={filtersResetFlag} 
                filters={filters}
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
            <ResetButton reserFunc={handleResetFilters}/>
        </div>
    )
}