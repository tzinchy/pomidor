import React, {useState, useEffect} from "react";
import { TableHead } from "../../PloshadkiTable/Table/Components";
import HistoryTableBody from "./HistoryTableBody";
import { HOSTLINK } from "../..";

export default function HistoryTable(){
    const headers = ["Номер истории", "Старый дом", "Новый дом", ""]
    const [data, setData] = useState([])

    useEffect(() => { 
        fetch(`${HOSTLINK}/history`, {credentials: 'include',})
        .then((res) => res.json())
        .then((fetchedData) => {
            setData(fetchedData);
            console.log(fetchedData);
        });
    }, []);

    return (
        <div className="relative flex flex-col lg:flex-row h-[90vh] gap-2 bg-neutral-100 w-full transition-all duration-300">
            <div className="relative flex w-full">
                <div className="overflow-auto rounded-md border absolute left-0 h-full transition-all ease-in-out w-[calc(100%)] scrollbar-custom">
                    <table className="text-sm caption-bottom w-full border-collapse bg-white transition-all duration-300">
                        <TableHead headers={headers} />
                        <HistoryTableBody data={data} setData={setData} />
                    </table>
                </div>
            </div>
        </div>
    )
}