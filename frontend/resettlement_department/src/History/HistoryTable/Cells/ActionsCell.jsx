import React from "react";

export default function ActionsCell({props}){
    const value = props['props'];

    return (
        <td className="p-2 font-normal whitespace-nowrap">
            <div className="flex w-full flex-row items-center justify-start gap-1">
                <div className="flex flex-1 justify-around truncate">
                        <button className="px-6 py-2 bg-gray-400 rounded text-white">Скачать</button>
                        <button className="px-6 py-2 bg-gray-400 rounded text-white">Одобрить</button>
                        <button className="px-6 py-2 bg-gray-400 rounded text-white">Отменить</button>
                </div>
            </div>
        </td>
    )
}