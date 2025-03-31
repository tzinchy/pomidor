import React, { useState } from "react";
import PloshCell from "./Cells/PloshCell";
import DetailsStatusCell from "./Cells/DetailsStatusCell";
import { HOSTLINK } from "..";
import ManualSelectionModal from "./ManualSelectionModal";
import DetailsAdressCell from "./Cells/DetailsCells/DetailsAddressCell";
import DeclineResonsCell from "./Cells/DetailsCells/DeclineResonsCell";

export default function ApartDetails({
  className,
  apartmentDetails,
  setIsDetailsVisible,
  apartType,
  setSelectedRow,
  selectedRowId,
  fetchApartments,
  lastSelectedAddres,
  lastSelectedMunicipal,
  fetchApartmentDetails,
  getFilteData
}) {
  const [isManualSelectionOpen, setIsManualSelectionOpen] = useState(false); // Состояние для модального окна

  function handleClose() {
    setIsDetailsVisible(false);
    setSelectedRow(false);
  }

  const table = apartType === "OldApart" ? "new_apartments" : "old_apartments";

  // Функция для отмены подборов
  const handleCancelMatching = async () => {
    if (!apartmentDetails?.affair_id) {
      alert("Ошибка: ID квартиры не найден.");
      return;
    }

    try {
      const url = `${HOSTLINK}/tables/apartment/${apartmentDetails.affair_id}/cancell_matching_for_apart?apart_type=${apartType}`;
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Ошибка при отмене подборов");
      }

      const result = await response.json();
      console.log("Подборы отменены:", result.message);
      fetchApartments();
    } catch (error) {
      console.error("Ошибка:", error);
      alert("Не удалось отменить подборы. Попробуйте снова.");
    }
  };

  return (
    <div
      className={`relative z-20 flex flex-col bg-white rounded transition-all duration-300 shadow-lg ${className}`}
      style={{
        minWidth: 650 + "px",
        maxHeight: "calc(100vh)",
      }}
    >
      {/* Заголовок и кнопка закрытия */}
      <div className="flex justify-between items-center p-4 border-b">
        <div className="flex flex-col">
          <h2 className="text-lg font-bold truncate">
            {apartType !== "OldApart"
              ? apartmentDetails
                ? apartmentDetails.house_address + ", кв. " + apartmentDetails.apart_number
                : ""
              : apartmentDetails
              ? apartmentDetails.fio
              : ""}
          </h2>
          <p className="text-sm text-gray-600">
            {apartType === "OldApart"
              ? apartmentDetails
                ? `${apartmentDetails.district}, ${apartmentDetails.municipal_district}, ${apartmentDetails.house_address + ", кв. " + apartmentDetails.apart_number}`
                : ""
              : apartmentDetails
              ? `${apartmentDetails.district}, ${apartmentDetails.municipal_district}`
              : ""}
          </p>
        </div>
        {apartType === "OldApart" && (
          <div className="flex">
            <button
              onClick={() => setIsManualSelectionOpen(true)}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              Ручной подбор
            </button>
            <a target="_blank" rel="noreferrer" href={`http://webrsm.mlc.gov:5222/ObjectCard?ObjId=${apartmentDetails.affair_id}&RegisterViewId=KursKpu&isVertical=true&useMasterPage=true`}><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-file-text"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"></path><path d="M14 2v4a2 2 0 0 0 2 2h4"></path><path d="M10 9H8"></path><path d="M16 13H8"></path><path d="M16 17H8"></path></svg></a>
          </div>
        )}
        <button
          className="h-10 w-10 p-0 border border-gray-300 rounded-full flex items-center justify-center"
          onClick={handleClose}
        >
          <span className="h-6 w-6 text-gray-600">X</span>
        </button>
      </div>

      {/* Контент */}
      <div className="p-4 overflow-y-auto">
        {apartmentDetails.offers ? (
          <div className="overflow-x-auto">
            <table className="text-sm caption-bottom w-full border-collapse bg-white">
              <tbody>
                {Object.values(apartmentDetails.offers).map((value, index) => {
                  const offerKeys = Object.keys(value); // Получаем ключи объекта offers
                  const hasMultipleOffers = offerKeys.length > 1; // Проверяем, есть ли больше одного ключа
                  return (
                    <React.Fragment key={index}>
                      {/* Основная строка */}
                      <tr className={`bg-white transition-colors ${hasMultipleOffers ? 'border-b-2 border-b-gray-200' : 'border-b-2 border-b-red-200'}`}>
                        <td>
                          <DetailsAdressCell props={offerKeys.length > 0 ? value[offerKeys[0]] : value} />
                        </td>
                        <td>
                          <PloshCell props={offerKeys.length > 0 ? value[offerKeys[0]] : value} />
                        </td>
                        <DetailsStatusCell
                          props={offerKeys.length > 0 ? value[offerKeys[0]] : value} // Передаем первый элемент, если есть несколько
                          selectedRowId={selectedRowId}
                          apartType={apartType}
                          fetchApartments={fetchApartments}
                          lastSelectedAddres={lastSelectedAddres}
                          lastSelectedMunicipal={lastSelectedMunicipal}
                          apartmentDetails={apartmentDetails}
                          newApartId={offerKeys[0]}
                        />
                        <DeclineResonsCell 
                          props={offerKeys.length > 0 ? value[offerKeys[0]] : value} 
                          newApartId={offerKeys[0]} 
                          apartmentDetails={apartmentDetails}
                          selectedRowId={selectedRowId}
                          fetchApartmentDetails={fetchApartmentDetails}
                        />
                      </tr>

                      {/* Дополнительные строки, если есть несколько offers */}
                      {hasMultipleOffers &&
                        offerKeys.slice(1).map((key, subIndex) => (
                          <tr key={`${index}-${subIndex}`} className={`bg-white border-b-2 transition-colors ${key === offerKeys[offerKeys.length-1] ? 'border-b-2 border-b-red-200' : '' }`}>
                            <td>
                              <DetailsAdressCell props={value[key]} />
                            </td>
                            <td>
                              <PloshCell props={value[key]} />
                            </td>
                            <DetailsStatusCell
                              props={value[key]}
                              selectedRowId={selectedRowId}
                              apartType={apartType}
                              fetchApartments={fetchApartments}
                              lastSelectedAddres={lastSelectedAddres}
                              lastSelectedMunicipal={lastSelectedMunicipal}
                              apartmentDetails={apartmentDetails}
                              newApartId={key}
                            />
                            <DeclineResonsCell 
                              props={offerKeys.length > 0 ? value[key] : value} 
                              newApartId={key} 
                              apartmentDetails={apartmentDetails}
                              selectedRowId={selectedRowId}
                              fetchApartmentDetails={fetchApartmentDetails}
                            />
                          </tr>
                        ))}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
            {apartType === "OldApart" && (
              <div className="mt-4 flex gap-2">
                <button
                  onClick={handleCancelMatching}
                  className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
                >
                  Отменить подборы
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="relative flex flex-col place-items-center py-4 text-gray-500">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="lucide lucide-cat stroke-muted-foreground h-12 w-12 stroke-1"
            >
              <path d="M12 5c.67 0 1.35.09 2 .26 1.78-2 5.03-2.84 6.42-2.26 1.4.58-.42 7-.42 7 .57 1.07 1 2.24 1 3.44C21 17.9 16.97 21 12 21s-9-3-9-7.56c0-1.25.5-2.4 1-3.44 0 0-1.89-6.42-.5-7 1.39-.58 4.72.23 6.5 2.23A9.04 9.04 0 0 1 12 5Z"></path>
              <path d="M8 14v.5"></path>
              <path d="M16 14v.5"></path>
              <path d="M11.25 16.25h1.5L12 17l-.75-.75Z"></path>
            </svg>
            <div>Нет данных для отображения</div>
          </div>
        )}
      </div>

      {/* Модальное окно для ручного подбора */}
      <ManualSelectionModal
        isOpen={isManualSelectionOpen}
        onClose={() => setIsManualSelectionOpen(false)}
        apartmentId={apartmentDetails.affair_id}
        fetchApartments={fetchApartments}
        getFilteData={getFilteData}
      />
    </div>
  );
}