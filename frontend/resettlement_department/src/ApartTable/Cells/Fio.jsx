import React from "react";

export default function FamilyCell( {fio, status} ){

    return (
      <div className="flex w-full flex-row items-center justify-start gap-1">
        <div className="flex flex-1 flex-col items-start justify-start truncate">
          <div className="truncate">{`${fio ? fio.replace('-.-.', '') : '-'}`}</div>
          <div className="text-muted-foreground truncate text-xs">
            {status}
          </div>
        </div>
      </div>
    );
  }