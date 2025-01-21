import React from "react";

export default function ApartmentCell( props ) {
  const value = props['props']
  
  return (
    <div className="flex w-full flex-row items-center justify-start gap-1">
      <div className="flex flex-1 flex-col items-start justify-start truncate">
        <div className="truncate">{`№ ${value['apart_number']}`}</div>
        <div className="text-muted-foreground truncate text-xs">
          {`${value['room_count'] || 0} комн.`}
        </div>
      </div>
    </div>
  );
  }