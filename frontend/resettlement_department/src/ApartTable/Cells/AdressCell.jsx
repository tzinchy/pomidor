import React from "react";

export default function AdressCell( props ){
  const value = props['props']
  
  return (
      <div className="flex w-full flex-row items-center justify-start gap-1">
        <div className="flex flex-1 flex-col items-start justify-start truncate">
          <div className="line-clamp-2">{value['house_address'] + ', кв.' + value['apart_number']}</div>
          <div className="line-clamp-1 text-muted-foreground text-xs">
            <span className="font-bold">{value['district']}</span>, {value['municipal_district']}
          </div>
        </div>
      </div>
  );
  }