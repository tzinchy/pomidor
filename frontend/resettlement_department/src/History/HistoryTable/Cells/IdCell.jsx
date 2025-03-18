import React from "react";

export default function IdCell(props){
    const value = props['props']
    return (
        <td className="p-2 font-bold text-base whitespace-nowrap">
            <div className="flex w-full flex-row items-center justify-start gap-1">
                <div className="flex flex-1 flex-col items-start justify-start truncate">
                    <div className="line-clamp-2">{value['history_id']}</div>
                </div>
            </div>
        </td>
    )
}