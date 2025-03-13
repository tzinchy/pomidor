import React, { useState, useRef } from "react";
import ReactDOM from "react-dom";
import { HOSTLINK } from "../..";

export default function DetailsStatusCell({props, selectedRowId, apartType, fetchApartments, lastSelectedAddres, lastSelectedMunicipal, apartmentDetails}) {
    const val = props;
    const [isOpen, setIsOpen] = useState(false);
    const [showRejectModal, setShowRejectModal] = useState(false); // Состояние для отображения модального окна
    const [selectedStatus, setSelectedStatus] = useState(null); // Состояние для хранения выбранного статуса
    const buttonRef = useRef(null); // Ссылка на кнопку для вычисления позиции
    const [minFloor, setMinFloor] = useState(""); // Состояние для минимального этажа
    const [maxFloor, setMaxFloor] = useState(""); // Состояние для максимального этажа

    const colors = {
        "Ждёт одобрения": 'bg-blue-100 text-blue-500', 
        "Ожидание": 'bg-yellow-100 text-amber-600',
        "Согласие": 'bg-green-100 text-emerald-600',
        "Отказ": 'bg-red-100  text-red-700 ',
        "Суд": 'bg-red-300 text-white',
        "Фонд компенсация": 'bg-violet-200 text-violet-500',
        "Фонд докупка": 'bg-violet-200 text-violet-500'
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

    const changeStatus = async (apartmentId, newStatus, apartType) => {
        try {
            // Формируем URL с apartment_id и apart_type
            const url = `${HOSTLINK}/tables/apartment/${apartmentId}/change_status?apart_type=${apartType}`;
    
            // Отправляем POST-запрос
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ new_status: newStatus }), // Тело запроса
            });
    
            // Обработка ответа
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Ошибка при изменении статуса');
            }
    
            const result = await response.json();
            console.log('Статус успешно изменен:', result.message);
            fetchApartments(lastSelectedAddres, lastSelectedMunicipal);
            return result;
        } catch (error) {
            console.error('Ошибка:', error);
            alert('Не удалось изменить статус. Попробуйте снова.');
            throw error; // Пробрасываем ошибку для дальнейшей обработки
        }
    };

    const handleStatusSelect = (status) => {
        if (status === "Отказ") {
            setSelectedStatus(status); // Сохраняем выбранный статус
            setShowRejectModal(true); // Показываем модальное окно
        } else {
            changeStatus(selectedRowId, status, apartType); // Отправляем запрос
        }
        setIsOpen(false); // Закрываем выпадающий список
    };

    const handleAcceptReject = () => {
        if (selectedStatus) {
            // Выводим значения минимального и максимального этажа в консоль
            console.log("Минимальный этаж:", minFloor);
            console.log("Максимальный этаж:", maxFloor);

            // Вызываем changeStatus с выбранным статусом
            changeStatus(selectedRowId, selectedStatus, apartType);

            // Закрываем модальное окно и сбрасываем состояния
            setShowRejectModal(false);
            setSelectedStatus(null);
            setMinFloor(""); // Сбрасываем минимальный этаж
            setMaxFloor(""); // Сбрасываем максимальный этаж
        }
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
                        onSelect={handleStatusSelect}
                    />
                )}
            </div>

            {/* Модальное окно для статуса "Отказ" */}
            {showRejectModal && (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white p-6 rounded-lg shadow-lg relative w-full max-w-md">
            {/* Кнопка закрытия (крестик) */}
            <button
                onClick={() => setShowRejectModal(false)} // Закрываем окно без изменения статуса
                className="absolute top-2 right-2 text-gray-500 hover:text-gray-700"
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-6 w-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                    />
                </svg>
            </button>

            {/* Адрес */}
            <h2 className="text-lg font-semibold mb-4">{apartmentDetails ? apartmentDetails.house_address + ", кв. " + apartmentDetails.apart_number : ""}</h2>

            {/* От какого этажа */}
            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Этажность</label>
                <div className="flex text-xs items-center">
                    <label className="block text-gray-700 mr-1">От</label>
                    <input
                        type="number"
                        className="w-full px-1 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 mr-1"
                        placeholder="Введите мин этаж"
                    />
                    <label className="block text-gray-700 mr-1">До</label>
                    <input
                        type="number"
                        className="w-full px-1 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 mr-1"
                        placeholder="Введите макс этаж"
                    />
                </div>
            </div>

            {/* Дом (выпадающий список) */}
            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Дом</label>
                <select
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                    <option value="">Выберите дом</option>
                    <option value="1">Дом 1</option>
                    <option value="2">Дом 2</option>
                    <option value="3">Дом 3</option>
                    {/* Добавьте больше опций по необходимости */}
                </select>
            </div>

            {/* Секция */}
            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Секция</label>
                <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Введите секцию"
                />
            </div>

            {/* Планировка */}
            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Планировка</label>
                <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Введите планировку"
                />
            </div>

            {/* Общий комментарий */}
            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Общий комментарий</label>
                <textarea
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Введите комментарий"
                    rows={3}
                />
            </div>

            {/* Кнопка "Принять" */}
            <button
                onClick={handleAcceptReject}
                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 w-full"
            >
                Принять
            </button>
        </div>
    </div>
)}
        </td>
    );
}

// Компонент для выпадающего списка (рендерится через портал)
function Dropdown({ colors, position, onSelect }) {
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