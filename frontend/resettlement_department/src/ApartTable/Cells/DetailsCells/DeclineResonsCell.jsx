import React, { useState, useEffect } from "react";
import DeclineModal from "../DeclineModal";
import { HOSTLINK } from "../../..";

export default function DeclineResonsCell({ props, newApartId, apartmentDetails, selectedRowId, fetchApartmentDetails }) {
  const value = props['decline_reason'];
  const [minFloor, setMinFloor] = useState(value.min_floor);
  const [maxFloor, setMaxFloor] = useState(value.max_floor);
  const [unom, setUnom] = useState(value.unom);
  const [entrance, setEntrance] = useState(value.entrance);
  const [apartment_layout, setApartment_layout] = useState(value.apartment_layout);
  const [notes, setNotes] = useState(value.notes);
  const [showRejectModal, setShowRejectModal] = useState(false);

  // Синхронизация состояний с value при изменении value
  useEffect(() => {
    setMinFloor(value.min_floor);
    setMaxFloor(value.max_floor);
    setUnom(value.unom);
    setEntrance(value.entrance);
    setApartment_layout(value.apartment_layout);
    setNotes(value.notes);
  }, [value]); // Зависимость от value

  async function update_declined_reason(decline_reason_id, declineReason) {
    try {
      const response = await fetch(
        `${HOSTLINK}/tables/apartment/decline_reason/${decline_reason_id}/update_declined_reason`,
        {
          method: "PATCH",
          credentials: "include",
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

  const handleAcceptReject = async () => {
    const declineReason = {
      min_floor: minFloor,
      max_floor: maxFloor,
      unom: unom,
      entrance: entrance,
      apartment_layout: apartment_layout,
      notes: notes,
    };

    try {
      await update_declined_reason(props.decline_reason_id, declineReason);

      setShowRejectModal(false);
      setMinFloor("");
      setMaxFloor("");
      setUnom("");
      setEntrance("");
      setApartment_layout("");
      setNotes("");
      fetchApartmentDetails(selectedRowId);
    } catch (error) {
      console.error("Ошибка при обработке отказа:", error);
      alert("Не удалось обработать отказ. Попробуйте снова.");
    }
  };

  return (
    <div className="flex w-full flex-row items-center justify-start gap-1 text-gray-400">
      <div className="flex flex-1 flex-col items-start justify-start " onClick={() => setShowRejectModal(true)}>
        <div className="line-clamp-2 text-xs">{value.notes ? value.notes : '-'}</div>
        <div className="text-xs">
          {`Эт: ${value.min_floor ? value.min_floor : '-'} - ${value.max_floor ? value.max_floor : '-'}; Дом: ${value.unom ? value.unom : '-'}; Секция: ${value.entrance ? value.entrance : '-'}; Планировка: ${value.apartment_layout ? value.apartment_layout : '-'}`}
        </div>
      </div>
      <DeclineModal
        isOpen={showRejectModal}
        onClose={() => setShowRejectModal(false)} // Передаем функцию закрытия
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
    </div>
  );
}