import React from "react";

export default function DetailsAdressCell( props ){
  const value = props['props']  
  
  return (
    <div className="flex w-full flex-row items-center justify-start gap-1">
      <div className="flex flex-1 flex-col items-start justify-start truncate">
        <div className="line-clamp-2">{value['house_address'] + ', кв.' + value['apart_number']}</div>
        <div className="line-clamp-1 text-muted-foreground text-xs">
          <span className="font-bold">{value['district']}</span>, {value['municipal_district']}
          {value.is_queue ? (<div className="inline-flex items-center rounded-full border py-0.5 font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 text-foreground ml-1 h-4 px-1 text-xs bg-amber-100 border-amber-200">Очередник</div>) : ''}
        </div>
      </div>
    </div>
  );
  }