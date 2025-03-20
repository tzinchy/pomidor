import React, { useState, useRef, useEffect } from "react";

export default function MunicipalDropdownFilter({ item, data, func, filterType, isFiltersReset }) {
    const [dropdownState, setDropdownState] = useState(false);
    const [selectedValues, setSelectedValues] = useState([]);
    const [searchQuery, setSearchQuery] = useState("");
    const container = useRef(null);

    useEffect(() => {
        if (isFiltersReset) {
            setSelectedValues([]);
            func(filterType, []);
        }
    }, [isFiltersReset, filterType, func]);

    const handleClickOutside = (e) => {
        if (container.current && !container.current.contains(e.target)) {
            setDropdownState(false);
        }
    };

    const toggleValue = (value) => {
        setSelectedValues((prev) => {
            const isSelected = prev.includes(value);
            const newValues = isSelected
                ? prev.filter((v) => v !== value)
                : [...prev, value];

            func(filterType, newValues);
            return newValues;
        });
    };

    const isSelected = (value) => selectedValues.includes(value);

    useEffect(() => {
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    // Фильтрация данных на основе поискового запроса
    const filteredData = data
        .map((area) => ({
            ...area,
            items: area.items.filter((item) =>
                item.label.toLowerCase().includes(searchQuery.toLowerCase())
            ),
        }))
        .filter((area) => area.items.length > 0); // Убираем области, в которых нет подходящих элементов

    return (
        <div className="relative flex items-center mr-4" ref={container}>
            <button
                onClick={() => setDropdownState(!dropdownState)}
                type="button"
                aria-haspopup="dialog"
                className="bg-white font-medium inline-flex items-center justify-center whitespace-nowrap text-sm ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-gray-100 rounded-md px-3 h-8 border-dashed"
            >
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
                    className="lucide lucide-circle-plus mr-2 h-4 w-4"
                >
                    <circle cx="12" cy="12" r="10"></circle>
                    <path d="M8 12h8"></path>
                    <path d="M12 8v8"></path>
                </svg>
                {item}
                {selectedValues.length > 0 && (
                    <>
                        <span className="mx-2">|</span>
                        <div className="flex items-center space-x-1">
                            {selectedValues.length > 2 ? (
                                <span className="bg-gray-100 text-sm px-2 py-1 rounded">
                                    {selectedValues.length} выбрано
                                </span>
                            ) : (
                                selectedValues.map((value) => (
                                    <span
                                        key={value}
                                        className="bg-gray-100 text-sm px-2 py-1 rounded"
                                    >
                                        {value}
                                    </span>
                                ))
                            )}
                        </div>
                    </>
                )}
            </button>

            {dropdownState && (
                <div className="absolute top-full mt-2 w-72 rounded-md border bg-white shadow-md z-50">
                    <div className="p-2">
                        <div className="flex items-center border-b pb-2">
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
                                className="lucide lucide-search mr-2 h-4 w-4 opacity-50"
                            >
                                <circle cx="11" cy="11" r="8"></circle>
                                <path d="m21 21-4.3-4.3"></path>
                            </svg>
                            <input
                                className="flex h-8 w-full rounded-md py-2 text-sm outline-none"
                                placeholder={item}
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                        </div>
                        <div className="max-h-[300px] overflow-y-auto mt-2">
                            {filteredData.map((area) => (
                                <div key={area.value}>
                                    <div className="p-2 text-sm text-gray-400">
                                        {area.label}
                                    </div>
                                    {area.items.map((item) => (
                                        <div
                                            key={item.value}
                                            className="flex items-center text-sm p-2 hover:bg-gray-100 rounded-md cursor-pointer"
                                            onClick={() => toggleValue(item.value)}
                                        >
                                            <div className={`w-4 h-4  border rounded-sm mr-2 flex items-center justify-center ${
                                                isSelected(item.value) ? 'bg-blue-500 border-blue-500' : 'border-gray-400'
                                            }`}>
                                                {isSelected(item.value) && (
                                                    <svg
                                                        xmlns="http://www.w3.org/2000/svg"
                                                        width="16"
                                                        height="16"
                                                        viewBox="0 0 24 24"
                                                        fill="none"
                                                        stroke="currentColor"
                                                        strokeWidth="2"
                                                        strokeLinecap="round"
                                                        strokeLinejoin="round"
                                                        className="lucide lucide-check text-white"
                                                    >
                                                        <path d="M20 6 9 17l-5-5"></path>
                                                    </svg>
                                                )}
                                            </div>
                                            <span>{item.label}</span>
                                        </div>
                                    ))}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}