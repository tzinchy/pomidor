import React from "react";

export default function PloshCell( props ){
  const value = props['props']

  console.log(value.floor);

  return (
    <div className="flex w-full flex-row items-center justify-start gap-1 text-gray-400">
      <div className="flex flex-1 flex-col items-start justify-start truncate">
        <div className="line-clamp-2">{`${value['full_living_area']} м², ${value['total_living_area']} м², ${value['living_area']} м²`}</div>
        <div className="text-xs">
          <span className='font-bold'>{value['room_count']}</span> комн. {`${value['type_of_settlement'] ? value['type_of_settlement'] : '-'} ${value['floor'] ? value['floor'] : "-"}`}
        </div>
      </div>
    </div>
  );
  }