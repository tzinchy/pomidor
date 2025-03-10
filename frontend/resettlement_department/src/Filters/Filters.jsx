import React, { useState } from "react";
import Dropdown from "./DropdownTry/Dropdown";
import ResetButton from "./ResetFilters";
import {areas, dateDiapazon, typePLoshad, otkl} from './FilterData';
import SearchInput from "./Search";

const ao =  ['AO', areas.map(area => area.label).flat()];

export default function Filters({handleValueSelect, resetFilters, isFiltersReset, onSearch }){
    return (
        <div className="flex w-full flex-wrap items-center justify-start gap-2">
            <SearchInput placeholder="Поиск по адресу" onSearch={onSearch}/>
            <Dropdown item={ao[0]} data={ao[1]} func={handleValueSelect} filterType={'okrugs'} isFiltersReset={isFiltersReset} />
            <Dropdown item={typePLoshad[0]} data={typePLoshad[1]} func={handleValueSelect} filterType={'otsel_type'} isFiltersReset={isFiltersReset} />
            <Dropdown item={dateDiapazon[0]} data={dateDiapazon[1]} func={handleValueSelect} filterType={'relocationAge'} isFiltersReset={isFiltersReset} />
            <Dropdown item={otkl[0]} data={otkl[1]} func={handleValueSelect} filterType={'deviation'} isFiltersReset={isFiltersReset} />
            <ResetButton reserFunc={resetFilters}/>
        </div>
    )
}