import React, { useState, useRef } from "react";
import ReactDOM from "react-dom";

export default function DetailsStatusCell(props) {
    const val = props['props'];
    const [isOpen, setIsOpen] = useState(false);
    const buttonRef = useRef(null); // Ссылка на кнопку для вычисления позиции

    const colors = {
        "Согласие": 'bg-green-100 text-emerald-600',
        "Ждёт одобрения": 'bg-blue-100 text-blue-500', 
        "Отказ": 'bg-red-100  text-red-700 ',
        "Суд": 'bg-red-300 text-white',
        "Фонд компенсация": 'bg-violet-200 text-violet-500',
        "Фонд докупка": 'bg-violet-200 text-violet-500',
        "Ожидание": 'bg-yellow-100 text-amber-600'
    };

    const toggleDropdown = () => setIsOpen(!isOpen);

    // Вычисляем позицию выпадающего списка
    const getDropdownPosition = () => {
        if (buttonRef.current) {
            const rect = buttonRef.current.getBoundingClientRect();
            return {
                top: rect.bottom + window.scrollY, // Ниже кнопки
                left: rect.left + window.scrollX,   // Слева от кнопки
                width: rect.width                  // Ширина кнопки
            };
        }
        return { top: 0, left: 0, width: 0 };
    };

    return (
        <td className="p-2 font-normal">
            <div className="relative">
                <button 
                    ref={buttonRef}
                    onClick={toggleDropdown}
                    className={`w-full max-w-[calc(180px)] px-6 py-2 text-center rounded font-semibold ${colors[val.status]}`}
                >
                    {val.status}
                </button>
                {isOpen && (
                    <Dropdown
                        colors={colors}
                        position={getDropdownPosition()}
                        onClose={() => setIsOpen(false)}
                        onSelect={(status) => {
                            console.log(`Selected status: ${status}`);
                            setIsOpen(false);
                        }}
                    />
                )}
            </div>
        </td>
    );
}

// Компонент для выпадающего списка (рендерится через портал)
function Dropdown({ colors, position, onClose, onSelect }) {
    return ReactDOM.createPortal(
        <div 
            className="fixed z-50 bg-white shadow-lg rounded-md max-h-40 overflow-y-auto scrollbar-custom text-center"
            style={{
                top: position.top,
                left: position.left,
                width: position.width
            }}
        >
            {Object.keys(colors).map((key) => (
                <div 
                    key={key}
                    className={`px-2 py-2 hover:border hover:border-white cursor-pointer ${colors[key]}`}
                    onClick={() => onSelect(key)}
                >
                    {key}
                </div>
            ))}
        </div>,
        document.body // Рендерим вне таблицы
    );
}