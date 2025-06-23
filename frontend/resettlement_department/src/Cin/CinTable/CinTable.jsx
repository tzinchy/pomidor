import React, {useState, useEffect} from "react";
import CinTableBody from "./CinTableBody";
import { TableHead } from "../../PloshadkiTable/Table/Components";
import { HOSTLINK } from "../..";

export default function CinTable() {
    const {cinData, setCinData} = useState([])
    const headers = ['Вариант', 'Адрес отселения', 'Адрес ЦИНа', 'График работы ЦИН', 'Дата начала работы','Телефон для осмота', 'Телефон для ответа', 'График работы Департамента в ЦИНе', 'Адрес Отдела']
    
    useEffect(() => { 
        fetch(`${HOSTLINK}/history`)
        .then((res) => res.json())
        .then((fetchedData) => {
            setCinData(fetchedData);
            console.log(fetchedData);
        });
    }, []);
    
    return (
        <div className="relative flex flex-col lg:flex-row h-[90vh] gap-2 bg-neutral-100 w-full transition-all duration-300">
            <div className="relative flex w-full">
                <div className="overflow-auto rounded-md border absolute left-0 h-full transition-all ease-in-out w-[calc(100%)] scrollbar-custom">
                    <table className="text-sm caption-bottom w-full border-collapse bg-white transition-all duration-300">
                        <TableHead headers={headers} />
                        <CinTableBody data={cinData} setData={setCinData} />
                    </table>
                </div>
            </div>
        </div>
    )
}