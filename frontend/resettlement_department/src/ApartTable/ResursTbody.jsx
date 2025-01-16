import React from 'react'
import FamilyCell from './Cells/Fio'
import ApartmentCell from './Cells/ApartmentCell'
import AdressCell from './Cells/AdressCell'
import PloshCell from './Cells/PloshCell'


export default function ResursTbody({ data }){

    if (!data || data.length === 0) {
        return <div>Загрузка данных...</div>;
    }

    return (
        <tbody>
            {data.map((val, index) => (
                <tr key={index} className="bg-white border-b transition-colors">
                    <th className="p-2 font-normal"><AdressCell props={val} /></th>
                    <th className="p-2 font-normal"><ApartmentCell props={val} /></th>
                    <th className="p-2 font-normal"><PloshCell props={val}/></th>
                </tr>
            ))}
        </tbody>
    )
}