import React from "react";

export default function DetailsStatusCell( props ){
    const val = props['props'];

    const colors = {
        "Согласие": 'bg-green-100 text-emerald-600',
        "Ждёт одобрения": 'bg-blue-100 text-amber-500', 
        "Отказ": 'bg-red-100  text-red-700 ',
        "Суд": 'bg-red-300 text-white',
        "Фонд компенсация": 'bg-violet-200 text-violet-500',
        "Фонд докупка": 'bg-violet-200 text-violet-500',
        "Ожидание": 'bg-yellow-100 text-amber-600'
    }

    return (
        <td className="p-2 font-normal" >
            <div>
                <button className={`w-full max-w-[calc(180px)] px-6 py-2 text-center cursor-default rounded font-semibold ${ colors[val.status] }`}>{val.status}</button>
            </div>
        </td>
    )
}