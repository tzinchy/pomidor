import React from "react";

export default function DeclineModal({
  isOpen,
  onClose,
  onAccept,
  apartmentDetails,
  minFloor,
  maxFloor,
  unom,
  entrance,
  apartment_layout,
  notes,
  setMinFloor,
  setMaxFloor,
  setUnom,
  setEntrance,
  setApartment_layout,
  setNotes,
}) {

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-lg relative w-full max-w-md">
        <button
          onClick={onClose}
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

        <h2 className="text-lg font-semibold mb-4">
          {apartmentDetails
            ? apartmentDetails.house_address +
              ", кв. " +
              apartmentDetails.apart_number
            : ""}
        </h2>

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
          </select>
        </div>

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

        <button
          onClick={onAccept}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 w-full"
        >
          Принять
        </button>
      </div>
    </div>
  );
}