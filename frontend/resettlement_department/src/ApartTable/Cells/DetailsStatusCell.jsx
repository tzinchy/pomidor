import React, { useState, useRef } from "react";
import ReactDOM from "react-dom";
import { HOSTLINK } from "../..";

export default function DetailsStatusCell({
  props,
  selectedRowId,
  apartType,
  fetchApartments,
  lastSelectedAddres,
  lastSelectedMunicipal,
  apartmentDetails,
}) {
  const val = props;
  const [isOpen, setIsOpen] = useState(false);
  const [showRejectModal, setShowRejectModal] = useState(false); // Состояние для отображения модального окна
  const [selectedStatus, setSelectedStatus] = useState(null); // Состояние для хранения выбранного статуса
  const buttonRef = useRef(null); // Ссылка на кнопку для вычисления позиции
  const [minFloor, setMinFloor] = useState(""); // Состояние для минимального этажа
  const [maxFloor, setMaxFloor] = useState(""); // Состояние для максимального этажа
  const [unom, setUnom] = useState(""); // Состояние для UNOM
  const [entrance, setEntrance] = useState(""); // Состояние для подъезда
  const [apartment_layout, setApartment_layout] = useState(""); // Состояние для планировки
  const [notes, setNotes] = useState(""); // Состояние для комментария

  const colors = {
    "Ждёт одобрения": "bg-blue-100 text-blue-500",
    Ожидание: "bg-yellow-100 text-amber-600",
    Согласие: "bg-green-100 text-emerald-600",
    Отказ: "bg-red-100  text-red-700 ",
    Суд: "bg-red-300 text-white",
    "Фонд компенсация": "bg-violet-200 text-violet-500",
    "Фонд докупка": "bg-violet-200 text-violet-500",
  };

  const toggleDropdown = () => setIsOpen(!isOpen);

  // Вычисляем позицию выпадающего списка
  const getDropdownPosition = () => {
    if (buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      return {
        top: rect.bottom + window.scrollY, // Ниже кнопки
        left: rect.left + window.scrollX, // Слева от кнопки
        width: rect.width, // Ширина кнопки
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
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ new_status: newStatus }), // Тело запроса
      });

      // Обработка ответа
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Ошибка при изменении статуса");
      }

      const result = await response.json();
      console.log("Статус успешно изменен:", result.message);
      fetchApartments(lastSelectedAddres, lastSelectedMunicipal);
      return result;
    } catch (error) {
      console.error("Ошибка:", error);
      alert("Не удалось изменить статус. Попробуйте снова.");
      throw error; // Пробрасываем ошибку для дальнейшей обработки
    }
  };

  async function setCancellReason(apartmentId, declineReason) {
    try {
      const response = await fetch(
        `${HOSTLINK}/tables/apartment/${apartmentId}/set_cancell_reason`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(declineReason),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Ошибка при отправке данных");
      }

      const result = await response.json();
      console.log("Причина отмены успешно установлена:", result);
      return result;
    } catch (error) {
      console.error("Ошибка:", error);
      throw error;
    }
  }

  const handleStatusSelect = (status) => {
    if (status === "Отказ") {
      setSelectedStatus(status); // Сохраняем выбранный статус
      setShowRejectModal(true); // Показываем модальное окно
    } else {
      changeStatus(selectedRowId, status, apartType); // Отправляем запрос
    }
    setIsOpen(false); // Закрываем выпадающий список
  };

  const handleAcceptReject = async () => {
    if (selectedStatus) {
      // Создаем объект с данными для отправки
      const declineReason = {
        min_floor: minFloor,
        max_floor: maxFloor,
        unom: unom,
        entrance: entrance,
        apartment_layout: apartment_layout,
        notes: notes,
      };

      // Выводим данные в консоль для проверки
      console.log("Данные для отправки:", declineReason);

      try {
        // Устанавливаем причину отмены
        await setCancellReason(selectedRowId, declineReason);

        // Меняем статус на "Отказ"
        await changeStatus(selectedRowId, selectedStatus, apartType);

        // Закрываем модальное окно и сбрасываем состояния
        setShowRejectModal(false);
        setSelectedStatus(null);
        setMinFloor(""); // Сбрасываем минимальный этаж
        setMaxFloor(""); // Сбрасываем максимальный этаж
        setUnom(""); // Сбрасываем UNOM
        setEntrance(""); // Сбрасываем подъезд
        setApartment_layout(""); // Сбрасываем планировку
        setNotes(""); // Сбрасываем комментарий
      } catch (error) {
        console.error("Ошибка при обработке отказа:", error);
        alert("Не удалось обработать отказ. Попробуйте снова.");
      }
    }
  };

  return (
    <td className="p-2 font-normal">
      <div className="relative">
        <button
          ref={buttonRef}
          onClick={toggleDropdown}
          className={`w-full max-w-[calc(180px)] px-6 py-2 text-center rounded font-semibold ${
            colors[val.status]
          }`}
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
            <h2 className="text-lg font-semibold mb-4">
              {apartmentDetails
                ? apartmentDetails.house_address +
                  ", кв. " +
                  apartmentDetails.apart_number
                : ""}
            </h2>

            {/* От какого этажа */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Этажность
              </label>
              <div className="flex text-xs items-center">
                <label className="block text-gray-700 mr-1">От</label>
                <input
                  type="number"
                  value={minFloor}
                  onChange={(e) => setMinFloor(e.target.value)}
                  className="w-full px-1 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 mr-1"
                  placeholder="Введите мин этаж"
                />
                <label className="block text-gray-700 mr-1">До</label>
                <input
                  type="number"
                  value={maxFloor}
                  onChange={(e) => setMaxFloor(e.target.value)}
                  className="w-full px-1 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 mr-1"
                  placeholder="Введите макс этаж"
                />
              </div>
            </div>

            {/* Дом (выпадающий список) */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Дом
              </label>
              <select
                value={unom}
                onChange={(e) => setUnom(e.target.value)}
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
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Секция
              </label>
              <input
                type="text"
                value={entrance}
                onChange={(e) => setEntrance(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Введите секцию"
              />
            </div>

            {/* Планировка */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Планировка
              </label>
              <input
                type="text"
                value={apartment_layout}
                onChange={(e) => setApartment_layout(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Введите планировку"
              />
            </div>

            {/* Общий комментарий */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Общий комментарий
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
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
        width: position.width,
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