import React from "react";

export default function IdCell(props){
    const value = props['props']
    return (
        <td>
            <div className="flex w-full flex-row items-center justify-start gap-1">
                <div className="flex flex-1 flex-col items-start justify-start truncate">
                    <div className="line-clamp-2">{value['id']}</div>
                </div>
            </div>
        </td>
    )
}