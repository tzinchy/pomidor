import React from "react";

export default function DatesCell(props){
    const value = props.props;
    return (
        <td className="p-2 font-normal" >
            <div className="flex flex-col justify-center items-start gap-0 w-[140px] text-left flex-wrap p-4 w-full">
                <div className="text-slate-500 w-full truncate">
                    { value.sentence_date ? `${value.sentence_date.slice(8)}.${value.sentence_date.slice(5,7)}.${value.sentence_date.slice(0,4)}` : ''}
                </div>
                <div className="w-full truncate ">
                    { value.answer_date ? `${value.answer_date.slice(8)}.${value.answer_date.slice(5,7)}.${value.answer_date.slice(0,4)}` : ""}
                </div>
            </div>
        </td>
    )
}