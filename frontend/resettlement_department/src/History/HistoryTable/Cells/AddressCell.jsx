import React from "react";

export default function AddressCell({ address }){
    return (
        <td className="p-2 font-normal whitespace-nowrap">
            <div className="flex w-full flex-row items-center justify-start gap-1">
                <div className="flex flex-1 flex-col items-start justify-start truncate">
                    <div className="line-clamp-2">
                        {address.map((val, index) => (
                            <p key={index}>{val}</p>
                        ))}
                    </div>
                </div>
            </div>
        </td>
    )
}