import React from 'react';
import FamilyCell from './Cells/Fio';
import AdressCell from './Cells/AdressCell';
import PloshCell from './Cells/PloshCell';
import StatusCell from './Cells/StatusCell';
import Notes from './Cells/Notes';


export default function ResursTbody({ data, apartType, fetchApartmentDetails }){

    if (!data || data.length === 0) {
        return <div>Загрузка данных...</div>;
    }

    return (
        <tbody>
            {data.map((val, index) => (
                <tr key={index} className="bg-white border-b transition-colors" onClick={() =>fetchApartmentDetails(val['affair_id'])}>
                    <td className="p-2 font-normal" style={{width: 13+'vw'}}><AdressCell props={val} /></td>
                    {apartType == 'FamilyStructure' ? (<td className="p-2 font-normal" style={{width: 15+'vw'}}><FamilyCell props={val}/></td>) : ''}
                    <td className="p-2 font-normal" style={{width: 5+'vw'}}><PloshCell props={val}/></td>
                    <td className="p-2 font-normal" style={{width: 5+'vw'}}><StatusCell props={val}/></td>
                    <td className="p-2 font-normal" style={{width: 20+'vw'}}><Notes props={val}/></td>
                </tr>
            ))}
        </tbody>
    )
}