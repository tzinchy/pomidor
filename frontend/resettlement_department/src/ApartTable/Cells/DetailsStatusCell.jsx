import React, { useState, useRef, useEffect } from "react";
import ReactDOM from "react-dom";
import { canSeeDashboard, HOSTLINK } from "../..";
import DeclineModal from "./DeclineModal";

export default function DetailsStatusCell({
  props,
  selectedRowId,
  apartType,
  fetchApartments,
  lastSelectedAddres,
  lastSelectedMunicipal,
  apartmentDetails,
  newApartId
}) {
  const val = props;
  const [isOpen, setIsOpen] = useState(false);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState(null);
  const buttonRef = useRef(null);
  const dropdownRef = useRef(null); // Ссылка на выпадающий список
  const [minFloor, setMinFloor] = useState("");
  const [maxFloor, setMaxFloor] = useState("");
  const [unom, setUnom] = useState("");
  const [entrance, setEntrance] = useState("");
  const [apartment_layout, setApartment_layout] = useState("");
  const [notes, setNotes] = useState("");

  const colors = canSeeDashboard ? {
    "Ждёт одобрения": "bg-blue-100 text-blue-500",
    "Подготовить смотровой": "bg-orange-100 text-orange-500",
    'Ожидание': "bg-yellow-100 text-amber-600",
    'Согласие': "bg-green-100 text-emerald-600",
    'Отказ': "bg-red-100  text-red-700 ",
    'Суд': "bg-red-300 text-white",
    "МФР Компенсация": "bg-violet-200 text-violet-500",
    "МФР Докупка": "bg-violet-200 text-violet-500",
  } : {
    'Согласие': "bg-green-100 text-emerald-600",
    'Отказ': "bg-red-100  text-red-700 ",
  };

  const toggleDropdown = () => setIsOpen(!isOpen);

  // Закрытие выпадающего списка при клике вне его области
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target) &&
        buttonRef.current &&
        !buttonRef.current.contains(event.target)
      ) {
        setIsOpen(false);
      }
    };

    // Добавляем обработчик при монтировании
    document.addEventListener("mousedown", handleClickOutside);

    // Убираем обработчик при размонтировании
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Вычисляем позицию выпадающего списка
  const getDropdownPosition = () => {
    if (buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      return {
        top: rect.bottom + window.scrollY,
        left: rect.left + window.scrollX,
        width: rect.width,
      };
    }
    return { top: 0, left: 0, width: 0 };
  };

  // Остальной код без изменений
  const changeStatus = async (apartmentId, newStatus) => {
    console.log(apartmentId, parseInt(newApartId), JSON.stringify({ new_status: newStatus }), apartType)
    try {
      const url = `${HOSTLINK}/tables/apartment/${apartmentId}/${parseInt(newApartId)}/change_status?apart_type=${apartType}`;
      const response = await fetch(url, {
        method: "POST",
        credentials: 'include',
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ new_status: newStatus }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Ошибка при изменении статуса");
      }

      const result = await response.json();
      console.log("Статус успешно изменен:", result.message, lastSelectedAddres, lastSelectedMunicipal);
      fetchApartments(lastSelectedAddres, lastSelectedMunicipal);
      return result;
    } catch (error) {
      console.error("Ошибка:", error);
      alert("Не удалось изменить статус. Попробуйте снова.");
      throw error;
    }
  };

  async function setCancellReason(apartmentId, declineReason) {
    try {
      const response = await fetch(
        `${HOSTLINK}/tables/apartment/${apartmentId}/${parseInt(newApartId)}/set_decline_reason`,
        {
          method: "POST",
          credentials: 'include',
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
    if ((status === "Отказ") || (status === "Суд")) {
      setSelectedStatus(status);
      setShowRejectModal(true);
    } else {
      changeStatus(selectedRowId, status, apartType);
    }
    setIsOpen(false);
  };

  const handleAcceptReject = async () => {
    if (selectedStatus) {
      const declineReason = {
        min_floor: minFloor,
        max_floor: maxFloor,
        unom: unom,
        entrance: entrance,
        apartment_layout: apartment_layout,
        notes: notes,
      };

      try {
        await setCancellReason(selectedRowId, declineReason);
        await changeStatus(selectedRowId, selectedStatus, apartType);

        setShowRejectModal(false);
        setSelectedStatus(null);
        setMinFloor("");
        setMaxFloor("");
        setUnom("");
        setEntrance("");
        setApartment_layout("");
        setNotes("");
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
            dropdownRef={dropdownRef} // Передаем ссылку на выпадающий список
          />
        )}
      </div>

      <DeclineModal
        isOpen={showRejectModal}
        onClose={() => setShowRejectModal(false)}
        onAccept={handleAcceptReject}
        apartmentDetails={apartmentDetails}
        minFloor={minFloor}
        maxFloor={maxFloor}
        unom={unom}
        entrance={entrance}
        apartment_layout={apartment_layout}
        notes={notes}
        setMinFloor={setMinFloor}
        setMaxFloor={setMaxFloor}
        setUnom={setUnom}
        setEntrance={setEntrance}
        setApartment_layout={setApartment_layout}
        setNotes={setNotes}
      />
    </td>
  );
}

// Компонент для выпадающего списка (рендерится через портал)
function Dropdown({ colors, position, onSelect, dropdownRef }) {
  return ReactDOM.createPortal(
    <div
      ref={dropdownRef} // Используем переданную ссылку
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
          className={`px-2 py-2 cursor-pointer ${colors[key]}`}
          onClick={() => onSelect(key)}
        >
          {key}
        </div>
      ))}
    </div>,
    document.body
  );
}