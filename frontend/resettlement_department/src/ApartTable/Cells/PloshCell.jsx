import React from "react";

export default function PloshCell( props ){
  const value = props['props']

  return (
    <div className="flex w-full flex-row items-center justify-start gap-1">
      <div className="flex flex-1 flex-col items-start justify-start truncate">
        <div className="line-clamp-2">{value['full_living_area']}</div>
        <div className="line-clamp-1 text-muted-foreground text-xs">
          {value['total_living_area'] + ', ' + value['living_area']}
        </div>
      </div>
    </div>
  );
  }