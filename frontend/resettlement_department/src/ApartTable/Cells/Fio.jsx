import React from "react";

export default function FamilyCell( props ){
  const value = props['props']

    return (
      <div className="flex w-full flex-row items-center justify-start gap-1">
        <div className="flex flex-1 flex-col items-start justify-start truncate">
          <div className="truncate">{`${value['fio'] ? value['fio'].replace('-.-.', '') : '-'}`}</div>
        </div>
      </div>
    );
  }