import React from "react";
import { TableHead } from "../PloshadkiTable/Table/Components";
import ResursTbody from "./ResursTbody";
import ApartDetails from "./ApartDetails";

export default function ApartTable({
  apartType,
  data,
  fetchApartmentDetails,
  apartmentDetails,
  selectedRow,
  setSelectedRow,
  isDetailsVisible, 
  setIsDetailsVisible
}) {
  

  const headers =
    apartType === "FamilyStructure"
      ? ["Адрес", "ФИО", "Площадь, тип, этаж", "Статус", "Примечания"]
      : ["Адрес", "Площадь, тип, этаж", "Статус", "Примечания"];

  return (
    <div className="relative flex flex-col lg:flex-row h-[calc(100vh-1rem)] gap-2 bg-neutral-100 w-full transition-all duration-300">
      {/* Таблица */}
      <div
        className={`overflow-auto rounded-md border h-full ${
          isDetailsVisible ? "lg:w-2/4" : "w-full"
        } transition-all duration-300 ease-in-out`}
        style={{
          scrollbarWidth: "thin", // Firefox
          scrollbarColor: "#c1c1c1 #f1f1f1", // Firefox
        }}
      >
        <div className="overflow-auto rounded-md border absolute left-0 h-[calc(100vh-1.5rem)] w-full transition-all ease-in-out">
          <table className="text-sm caption-bottom w-full border-collapse bg-white">
            <TableHead headers={headers} />
            <ResursTbody
              data={data}
              apartType={apartType}
              fetchApartmentDetails={fetchApartmentDetails}
              isDetailsVisible={isDetailsVisible}
              setIsDetailsVisible={setIsDetailsVisible}
              selectedRow={selectedRow}
              setSelectedRow={setSelectedRow}
            />
          </table>
        </div>
      </div>

      {/* Боковая панель */}
      {apartmentDetails && isDetailsVisible && (
          <ApartDetails
            apartmentDetails={apartmentDetails}
            setIsDetailsVisible={setIsDetailsVisible}
            apartType={apartType}
            setSelectedRow={setSelectedRow}
          />
      )}
    </div>
  );
}
