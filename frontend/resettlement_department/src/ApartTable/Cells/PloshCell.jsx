import React from "react";

export default function PloshCell( props ){
  const value = props['props']

  return (
    <div className="flex w-full flex-row items-center justify-start gap-1 text-gray-400 text-xs">
      <div className="flex flex-1 flex-col items-start justify-start truncate">
        <div className="line-clamp-2">{`${value['full_living_area'] ? value['full_living_area'] : '-'} м², ${value['total_living_area'] ? value['total_living_area'] : '-'} м², ${value['living_area'] ? value['living_area'] : '-'} м²`}</div>
        <div>
          <span className='font-bold'>{value['room_count']}</span> комн. {`${value['floor'] ? value['floor'] + ' этаж' : "-"}, ${value['type_of_settlement']} `}
        </div>
      </div>
    </div>
  );
  }