import React, { useState, useRef, useEffect } from "react";
import { HOSTLINK } from "../..";

export default function NotesCell({props, apartType}) {
  const value = props;
  const [isEditing, setIsEditing] = useState(false);
  const [notes, setNotes] = useState(value["notes"]);
  const inputRef = useRef(null);

  const id = apartType === 'OldApart' ? 'affair_id' : 'new_apart_id';

  // Фокус на поле ввода при активации редактирования
  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isEditing]);

  // Обработчик клика для активации редактирования
  const handleClick = (e) => {
    e.stopPropagation(); // Предотвращаем всплытие события
    setIsEditing(true);
  };

  // Функция для отправки данных на сервер
  const saveNotes = async (apartment_id, newNotes, apartType) => {
    try {
      const response = await fetch(`${HOSTLINK}/tables/apartment/${apartment_id}/set_notes?apart_type=${apartType}`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          apartment_id: apartment_id,
          apart_type: apartType,
          notes: newNotes,
        }),
      });

      if (!response.ok) {
        throw new Error("Ошибка при сохранении примечаний");
      }

      const result = await response.json();
      console.log("Примечания успешно сохранены:", result);
    } catch (error) {
      console.error("Ошибка:", error);
    }
  };

  // Обработчик сохранения при потере фокуса
  const handleBlur = () => {
    setIsEditing(false);
    if (notes !== value["notes"]) {
      // Вызываем функцию сохранения, если данные изменились
      saveNotes(value[id], notes, apartType);
      props.onSave?.(value, notes); // Вызов родительской функции, если она передана
    }
  };

  return (
    <div
      className="text-sm flex w-full flex-row items-center justify-start gap-1 text-gray-400  cursor-pointer"
      onClick={handleClick}
    >
      <div className="flex flex-1 flex-col items-start justify-start">
        {isEditing ? (
          <textarea
            ref={inputRef}
            value={notes || ""}
            onChange={(e) => setNotes(e.target.value)}
            onBlur={handleBlur}
            className="w-full rounded focus:outline-none resize-none"
            rows={3}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleBlur();
              }
            }}
          />
        ) : (
          <div className="whitespace-normal">
            {notes || (
              <div className="flex text-gray-300">
                <span className="text-gray-300 mr-2">Добавить примечание</span>
                <svg
                  className="w-4 h-4 group-hover:opacity-100 transition-opacity"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  onClick={handleClick}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
                  />
                </svg>
              </div>
              
            )}
          </div>
        )}
      </div>
    </div>
  );
}