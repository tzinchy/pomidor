import React from "react";
import { HOSTLINK } from "..";

export default function DownloadApartsXLSX({ apartType, apartments, withLastOffer = true }) {
  const handleDownload = async () => {
    let apartIds = [];

    if (apartType === "OldApart") {
      apartIds = apartments.map(row => row.affair_id);
    } else if (apartType === "NewApartment") {
      apartIds = apartments.map(row => row.new_apart_id);
    }

    try {
    //   const params = new URLSearchParams({
    //     apart_type: apartType,
    //     with_last_offer: withLastOffer.toString(),
    //   });

    //   apartIds.forEach(id => params.append("apart_ids", id));

    const response = await fetch(`${HOSTLINK}/tables/curent_table`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        apart_type: apartType,
        apart_ids: apartIds,
        with_last_offer: withLastOffer,
      }),
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
      className="px-4 py-2 border bg-white duration-300 text-black rounded hover:bg-gray-100"
    >
      Скачать Excel
    </button>
  );
}