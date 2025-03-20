import React from "react";

export default function DeclineResonsCell( props ){
  const value = props['props']['decline_reason_id'];
  console.log('DECLINE', value);

  return (
    <div className="flex w-full flex-row items-center justify-start gap-1 text-gray-400">
      <div className="flex flex-1 flex-col items-start justify-start ">
        <div className="line-clamp-2 text-xs">{value.notes}</div>
        <div className="text-xs">
            {`Эт: ${value.min_floor} - ${value.max_floor}; Дом: ${value.unom}; Секция: ${value.entrance}; Планировка: ${value.apartment_layout}`}
        </div>
      </div>
    </div>
  );
  }