import React from "react";

export default function HistoryTableBody({ data }){
    return (
        <tbody>
            {data.map((val, index) => (
                <tr key={index} className={`bg-white border-b transition-colors hover:bg-gray-100`} >
                    <td className="p-2 font-normal whitespace-nowrap" style={{width: 13+'vw'}}><AdressCell props={val} /></td>
                    <td className="p-2 font-normal whitespace-nowrap" style={{width: 5+'vw'}}><PloshCell props={val}/></td>
                    <td className="p-2 font-normal whitespace-nowrap" style={{width: 5+'vw'}}><StatusCell props={val}/></td>
                    <td className="p-2 font-normal whitespace-nowrap" style={{width: 20+'vw'}}><Notes props={val}/></td>
                </tr>
            ))}
        </tbody>
    )
}