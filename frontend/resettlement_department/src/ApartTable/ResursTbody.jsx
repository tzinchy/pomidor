import React, {useState} from 'react';
import FamilyCell from './Cells/Fio';
import AdressCell from './Cells/AdressCell';
import PloshCell from './Cells/PloshCell';
import StatusCell from './Cells/StatusCell';
import Notes from './Cells/Notes';


export default function ResursTbody({ data, apartType, fetchApartmentDetails, isDetailsVisible, setIsDetailsVisible, selectedRow, setSelectedRow }){
    
    
    if (!data || data.length === 0) {
        return <div></div>;
    }

    function handleClick(index, visibility, val) {
        if (visibility) {
            if (index !== selectedRow) {
                setSelectedRow(index); // Обновляем выбранную строку
                apartType === "FamilyStructure" ? fetchApartmentDetails(val["family_apartment_needs_id"]) : fetchApartmentDetails(val["new_apart_id"]);
            } else {
                setSelectedRow(false)
                setIsDetailsVisible(false); // Закрываем панель
            }
        } else {
            setSelectedRow(index); // Устанавливаем выбранную строку
            setIsDetailsVisible(true); // Открываем панел
            apartType === "FamilyStructure" ? fetchApartmentDetails(val["family_apartment_needs_id"]) : fetchApartmentDetails(val["new_apart_id"]);
        }
    }
    

    return (
        <tbody>
            {data.map((val, index) => (
                <tr key={index} 
                    className={`bg-white border-b transition-colors ${index === selectedRow ? "bg-zinc-100" : "hover:bg-gray-100"} ${(selectedRow || selectedRow === 0) && (index != selectedRow) ? 'blur-[1px]' : ''}`} 
                    onClick={() => handleClick(index, isDetailsVisible, val)}
                >
                    <td className="p-2 font-normal whitespace-nowrap" style={{width: 13+'vw'}}><AdressCell props={val} /></td>
                    {apartType == 'FamilyStructure' ? (<td className="p-2 font-normal whitespace-nowrap" style={{width: 15+'vw'}}><FamilyCell props={val}/></td>) : ''}
                    <td className="p-2 font-normal whitespace-nowrap" style={{width: 5+'vw'}}><PloshCell props={val}/></td>
                    <td className="p-2 font-normal whitespace-nowrap" style={{width: 5+'vw'}}><StatusCell props={val}/></td>
                    <td className="p-2 font-normal whitespace-nowrap" style={{width: 20+'vw'}}><Notes props={val}/></td>
                </tr>
            ))}
        </tbody>
    )
}