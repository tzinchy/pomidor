import React, { useState } from "react";
import { TableHead } from "../PloshadkiTable/Table/Components";
import ResursTbody from "./ResursTbody";
import ApartDetails from "./ApartDetails";

export default function ApartTable({
  apartType,
  data,
  fetchApartmentDetails,
  apartmentDetails,
  detailsRef,
}) {
  const [isDetailsVisible, setIsDetailsVisible] = useState(false);

  const headers =
    apartType === "FamilyStructure"
      ? ["Адрес", "ФИО", "Площадь, тип, этаж", "Статус", "Примечания"]
      : ["Адрес", "Площадь, тип, этаж", "Статус", "Примечания"];

  return (
    <div className="relative flex h-[calc(100vh-1rem)] w-full">
      {/* Таблица */}
      <div
        className={`overflow-auto rounded-md border relative h-full w-full transition-all duration-300 ease-in-out`}
      >
        <table className="text-sm caption-bottom w-full border-collapse bg-white">
          <TableHead headers={headers} />
          <ResursTbody
            data={data}
            apartType={apartType}
            fetchApartmentDetails={fetchApartmentDetails}
          />
        </table>
      </div>

      {/* Боковая панель */}
      {apartmentDetails && (
        <ApartDetails
          apartmentDetails={apartmentDetails}
          detailsRef={detailsRef}
          setIsDetailsVisible={setIsDetailsVisible}
        />
      )}
    </div>
  );
}
