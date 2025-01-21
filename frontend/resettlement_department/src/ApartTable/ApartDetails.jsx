import React from "react";
import AdressCell from "./Cells/AdressCell";
import PloshCell from "./Cells/PloshCell";
import DetailsStatusCell from "./Cells/DetailsStatusCell";
import DatesCell from "./Cells/DatesCell";

export default function ApartDetails({ apartmentDetails, setIsDetailsVisible, apartType, setSelectedRow }) {
  function handleClose() {
    setIsDetailsVisible(false);
    setSelectedRow(-1);
  }

  const table = apartType === "FamilyStructure" ? "new_apartments" : "old_apartments";

  return (
    <div
      className={`relative z-20 flex flex-col bg-white rounded transition-all duration-300 shadow-lg
      w-full sm:w-full md:w-3/4 lg:max-w-[50%]`}
      style={{minWidth:700+'px'}}
    >
      {/* Заголовок и кнопка закрытия */}
      <div className="flex justify-between items-center p-4 border-b">
        <div className="flex flex-col">
          <h2 className="text-lg font-bold truncate">
            {apartmentDetails
              ? apartmentDetails.house_address + ", кв. " + apartmentDetails.apart_number
              : ""}
          </h2>
          <p className="text-sm text-gray-600">
            {apartmentDetails
              ? `${apartmentDetails.district}, ${apartmentDetails.municipal_district}`
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
        {apartmentDetails[table] ? (
          <div className="overflow-x-auto">
            <table className="text-sm caption-bottom w-full border-collapse bg-white">
              <tbody>
                {apartmentDetails[table].map((value, index) => (
                  <tr
                    key={index}
                    className={`bg-white border-b transition-colors hover:bg-gray-100`}
                  >
                    <AdressCell props={value} />
                    <PloshCell props={value} />
                    <DatesCell props={value} />
                    <DetailsStatusCell props={value} />
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500">Нет данных для отображения</p>
        )}
      </div>
    </div>
  );
}
