import React, { useState, useRef, useEffect } from "react";

export default function TryDropdown({ item, data, func, filterType, isFiltersReset }) {
    const [dropdownState, setDropdownState] = useState(false);
    const [selectedValues, setSelectedValues] = useState([]);
    const [searchQuery, setSearchQuery] = useState("");
    const container = useRef(null);

    // Сброс выбранных значений при сбросе фильтров
    useEffect(() => {
        if (isFiltersReset) {
            setSelectedValues([]);
            func(filterType, []);
        }
    }, [isFiltersReset, filterType, func]);

    // Закрытие выпадающего списка при клике вне контейнера
    const handleClickOutside = (e) => {
        if (container.current && !container.current.contains(e.target)) {
            setDropdownState(false);
        }
    };

    // Добавление/удаление значения из списка выбранных
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

    // Проверка, выбрано ли значение
    const isSelected = (value) => selectedValues.includes(value);

    // Обработчик клика вне компонента
    useEffect(() => {
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    // Фильтрация данных на основе поискового запроса
    const filteredData = Array.isArray(data) // Проверка, что data — это массив
        ? data.filter((value) =>
              value.toString().toLowerCase().includes(searchQuery.toLowerCase())
        )
        : []; // Если data не массив, возвращаем пустой массив

    return (
        <div className="flex items-center mr-4">
            <button
                onClick={() => setDropdownState(!dropdownState)}
                type="button"
                aria-haspopup="dialog"
                className="bg-white inline-flex items-center justify-center whitespace-nowrap text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-gray-100 rounded-md px-3 h-8 border-dashed"
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
            </button>

            {dropdownState && (
                <div
                    ref={container}
                    className="fixed bg-white transition-transform duration-300 ease-in-out z-50 dropdown-open"
                    style={{ top: "5%" }}
                >
                    <div className="z-50 w-72 rounded-md border shadow-md outline-none p-0">
                        <div className="flex h-full w-full flex-col overflow-hidden rounded-md">
                            <div className="flex items-center border-b px-3">
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
                                    className="lucide lucide-search mr-2 h-4 w-4 shrink-0 opacity-50"
                                >
                                    <circle cx="11" cy="11" r="8"></circle>
                                    <path d="m21 21-4.3-4.3"></path>
                                </svg>
                                <input
                                    className="flex h-11 w-full rounded-md py-3 text-sm outline-none disabled:cursor-not-allowed disabled:opacity-50"
                                    placeholder={item}
                                    autoComplete="off"
                                    autoCorrect="off"
                                    spellCheck="false"
                                    aria-autocomplete="list"
                                    role="combobox"
                                    aria-expanded="true"
                                    type="text"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                />
                            </div>
                        </div>
                        <div className="max-h-[300px] overflow-y-auto overflow-x-hidden z-50">
                            <div className="text-foreground overflow-hidden p-1">
                                {filteredData.map((value) => (
                                    <div
                                        onClick={() => toggleValue(value)}
                                        key={value}
                                        className="relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none"
                                        data-value={value}
                                    >
                                        <div
                                            className={`mr-2 flex h-4 w-4 items-center justify-center rounded-sm border ${
                                                isSelected(value)
                                                    ? "text-primary-foreground border-black"
                                                    : "opacity-60 [&_svg]:invisible"
                                            }`}
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
                                                className="lucide lucide-check h-4 w-4"
                                            >
                                                <path d="M20 6 9 17l-5-5"></path>
                                            </svg>
                                        </div>
                                        <span>{value}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}