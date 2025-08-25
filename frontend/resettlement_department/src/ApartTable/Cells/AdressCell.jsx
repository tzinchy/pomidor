import React from "react";

export default function AdressCell( props ){
  const value = props['props']
  
  return (
    <div className="flex w-full flex-row items-center justify-start gap-1">
      <div className="flex flex-1 flex-col items-start justify-start min-w-0">
        <div className="whitespace-normal break-words text-sm">
          {value['house_address']}
        </div>
        <div className="whitespace-normal break-words text-muted-foreground text-xs">
          <span className="font-bold">{value['district']}</span>, {value['municipal_district']}
          {value.is_queue ? (
            <div className="inline-flex items-center rounded-full border py-0.5 font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 text-foreground ml-1 h-4 px-1 text-xs bg-amber-100 border-amber-200">
              Очередник
            </div>
          ) : ''}
          {(value.is_special_needs_marker || value.for_special_needs_marker) ? (
            <div className="inline-flex items-center rounded-full border py-0.5 font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 text-foreground ml-1 h-4 px-1 text-xs bg-gray-100 border-gray-200">
              Инвалид
            </div>
          ) : ''}
          {(value.was_queue || value.was_queue) ? (
            <div className="inline-flex items-center rounded-full border py-0.5 font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 text-foreground ml-1 h-4 px-1 text-xs bg-yellow-100 border-gray-200">
              Быв. очередник
            </div>
          ) : ''}
        </div>
      </div>
    </div>
  );
  }