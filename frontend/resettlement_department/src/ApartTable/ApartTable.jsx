import React from "react";
import { TableHead } from "../PloshadkiTable/Table/Components";
import ResursTbody from "./ResursTbody";


export default function ApartTable({ state, data }){

    const headers = [
        "Адрес",
        "Кв.",
        "Квадратура"
      ];

    return (
        <div className="relative flex h-[calc(100vh-1rem)] w-full">
            <div className="overflow-auto rounded-md border absolute left-0 h-full transition-all ease-in-out w-[calc(100%)]">
                <table className="text-base caption-bottom w-full border-collapse bg-white">
                    <TableHead headers={headers} />
                    <ResursTbody data={data} />
                </table>
            </div>
        </div>
    )
}