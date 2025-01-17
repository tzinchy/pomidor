import React, { useEffect, useRef } from "react";

export default function ApartDetails({ apartmentDetails }) {

    function handleClose(){
        
    }

    return (
        <div
        className={`relative z-20 flex flex-col bg-white ${
            apartmentDetails ? "" : "overflow-hidden"
        }`}
        >
        {/* Заголовок и кнопка закрытия */}
        <div className="flex justify-between items-center bg-accent/40 p-4">
            <div className="flex flex-col">
            <h2 className="text-lg font-bold">
                {apartmentDetails ? apartmentDetails.district : ""}
            </h2>
            <p className="text-sm text-gray-600">
                {apartmentDetails
                ? `${apartmentDetails.municipal_district}, ${apartmentDetails.house_address}`
                : ""}
            </p>
            </div>
            <button
            className="h-10 w-10 p-0 border border-gray-300 rounded-full flex items-center justify-center"
            onClick={handleClose}
            >
            <span className="h-6 w-6 text-gray-600">X</span>
            </button>
        </div>

        {/* Контент */}
        <div className="p-4 overflow-y-auto">
            {apartmentDetails ? (
            <div className="space-y-2 text-sm">
                <p><strong>Apartment Number:</strong> {apartmentDetails.apart_number}</p>
                <p><strong>Floor:</strong> {apartmentDetails.floor}</p>
                <p><strong>Room Count:</strong> {apartmentDetails.room_count}</p>
                <p><strong>Living Area:</strong> {apartmentDetails.living_area} m²</p>
                <p><strong>Status:</strong> {apartmentDetails.status}</p>
                <p><strong>Owner:</strong> {apartmentDetails.owner}</p>
                <p><strong>Notes:</strong> {apartmentDetails.notes}</p>
            </div>
            ) : (
            <p className="text-gray-500">Нет данных для отображения</p>
            )}
        </div>
        </div>
    );
}
