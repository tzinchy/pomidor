import {useState, useEffect} from "react";
import axios from "axios";
import CinTableBody from "./CinTableBody";
import { TableHead } from "../../PloshadkiTable/Table/Components";
import { HOSTLINK } from "../..";

export default function CinTable() {
    return (
        <div className="relative flex flex-col lg:flex-row h-[97vh] gap-2 bg-neutral-100 w-full transition-all duration-300">
            <div className="relative flex w-full">
                <div className="overflow-auto rounded-md border absolute left-0 h-full transition-all ease-in-out w-[calc(100%)] scrollbar-custom">
                    <table className="text-sm caption-bottom w-full border-collapse bg-white transition-all duration-300">
                        <CinTableBody /> 
                    </table>
                </div>
            </div>
        </div>
    )
}