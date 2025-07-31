import React from "react";

export default function DownloadApartsXLSX({ apartType, apartments, withLastOffer = false }) {
  const handleDownload = async () => {
    let apartIds = [];

    if (apartType === "OldApart") {
      apartIds = apartments.map(row => row.affair_id);
    } else if (apartType === "NewApartment") {
      apartIds = apartments.map(row => row.new_apart_id);
    }

    try {
      const params = new URLSearchParams({
        apart_type: apartType,
        with_last_offer: withLastOffer.toString(),
      });

      apartIds.forEach(id => params.append("apart_ids", id));

      const response = await fetch(`http://127.0.0.1:8000/tables/curent_table?${params.toString()}`, {
        method: "GET",
        // credentials: "include", // включи при авторизации через сессию
      });

      if (!response.ok) throw new Error("Ошибка сети");

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);

      const now = new Date();
      const timestamp = now.toISOString().replace(/[:.]/g, "-"); // "2025-07-30T15-01-22-000Z"
      const filename = `${apartType}_${timestamp}.xlsx`;

      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Ошибка при загрузке:", error);
    }
  };

  return (
    <button
      onClick={handleDownload}
      className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-700"
    >
      Скачать Excel
    </button>
  );
}