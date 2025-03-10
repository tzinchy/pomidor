import React from "react";
import AdressCell from "./Cells/AdressCell";
import PloshCell from "./Cells/PloshCell";
import DetailsStatusCell from "./Cells/DetailsStatusCell";
import DatesCell from "./Cells/DatesCell";

export default function ApartDetails({ className, apartmentDetails, setIsDetailsVisible, apartType, setSelectedRow }) {
  function handleClose() {
    setIsDetailsVisible(false);
    setSelectedRow(false);
  }

  const table = apartType === "OldApart" ? "new_apartments" : "old_apartments";

  return (
    <div
      className={`relative z-20 flex flex-col bg-white rounded transition-all duration-300 shadow-lg ${className}`}
      style={{ 
        minWidth: 650+'px', // Минимальная ширина для читаемости
        maxWidth: 'calc(100vw - 32px)', // Отступы по краям экрана
        maxHeight: 'calc(100vh)', // Отступ сверху и снизу
      }}
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
                    <td><AdressCell props={value} /></td>
                    <td><PloshCell props={value} /></td>
                    <DatesCell props={value} />
                    <DetailsStatusCell props={value} />
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="relative flex flex-col place-items-center py-4 text-gray-500">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-cat stroke-muted-foreground h-12 w-12 stroke-1">
              <path d="M12 5c.67 0 1.35.09 2 .26 1.78-2 5.03-2.84 6.42-2.26 1.4.58-.42 7-.42 7 .57 1.07 1 2.24 1 3.44C21 17.9 16.97 21 12 21s-9-3-9-7.56c0-1.25.5-2.4 1-3.44 0 0-1.89-6.42-.5-7 1.39-.58 4.72.23 6.5 2.23A9.04 9.04 0 0 1 12 5Z"></path>
              <path d="M8 14v.5"></path>
              <path d="M16 14v.5"></path>
              <path d="M11.25 16.25h1.5L12 17l-.75-.75Z"></path>
            </svg>
            <div>Нет данных для отображения</div>
          </div>
        )}
      </div>
    </div>
  );
}
