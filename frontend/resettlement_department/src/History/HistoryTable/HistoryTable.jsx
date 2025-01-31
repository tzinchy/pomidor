import React from "react";
import { TableHead } from "../../PloshadkiTable/Table/Components";
import HistoryTableBody from "./HistoryTableBody";

export default function HistoryTable(){
    return (
        <div className="relative flex flex-col lg:flex-row h-[calc(100vh-3.5rem)] gap-2 bg-neutral-100 w-full transition-all duration-300">
            <div className="relative flex h-[calc(100vh-3.5rem)] w-full">
                <div className="overflow-auto rounded-md border absolute left-0 h-full transition-all ease-in-out w-[calc(100%)] scrollbar-custom">
                    <table className="text-sm caption-bottom w-full border-collapse bg-white transition-all duration-300">
                        <TableHead headers={headers} />
                        <HistoryTableBody data={displayData} houseDetailsHandler={houseDetailsHandler} />
                    </table>
                </div>
            </div>
        </div>
    )
}