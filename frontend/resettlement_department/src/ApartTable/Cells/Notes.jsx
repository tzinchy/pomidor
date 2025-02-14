import React from "react";

export default function NotesCell(props){
    const value = props['props'];
    
    return (
      <div className="text-sm flex w-full flex-row items-center justify-start gap-1 text-gray-400">
        <div className="flex flex-1 flex-col items-start justify-start">
          <div className="whitespace-normal">{value['notes']}</div>
        </div>
      </div>
    )
}