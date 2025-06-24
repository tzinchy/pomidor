import React, {useState, useEffect} from "react";
import axios from "axios";
import CinTableBody from "./CinTableBody";
import { TableHead } from "../../PloshadkiTable/Table/Components";
import { HOSTLINK } from "../..";

export default function CinTable() {
    const {cinData, setCinData} = useState([])
    const headers = ['ID', 'Вариант', 'Адрес отселения', 'Адрес ЦИНа', 'График работы ЦИН', 'Дата начала работы','Телефон для осмота', 'Телефон для ответа', 'График работы Департамента в ЦИНе', 'Адрес Отдела']
    
    useEffect(() => { 
        fetchCin();
    }, []);

    const fetchCin = async () => {
    try {
      const response = await axios.get(`${HOSTLINK}/cin`);
      setCinData(response.data);
      console.log('response.data', response.data);
    } catch (error) {
      console.error("Error fetching districts:", error.response?.data);
    }
  };
    
    return (
        <div className="relative flex flex-col lg:flex-row h-[90vh] gap-2 bg-neutral-100 w-full transition-all duration-300">
            <div className="relative flex w-full">
                <div className="overflow-auto rounded-md border absolute left-0 h-full transition-all ease-in-out w-[calc(100%)] scrollbar-custom">
                    <table className="text-sm caption-bottom w-full border-collapse bg-white transition-all duration-300">
                        <TableHead headers={headers} />
                        {cinData ? 
                            <CinTableBody data={cinData} setData={setCinData} /> 
                            :
                            <div className="flex flex-1 justify-center h-64">
                                <div className="relative flex flex-col place-items-center py-4 text-gray-500">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-cat stroke-muted-foreground h-12 w-12 stroke-1">
                                        <path d="M12 5c.67 0 1.35.09 2 .26 1.78-2 5.03-2.84 6.42-2.26 1.4.58-.42 7-.42 7 .57 1.07 1 2.24 1 3.44C21 17.9 16.97 21 12 21s-9-3-9-7.56c0-1.25.5-2.4 1-3.44 0 0-1.89-6.42-.5-7 1.39-.58 4.72.23 6.5 2.23A9.04 9.04 0 0 1 12 5Z"></path>
                                        <path d="M8 14v.5"></path>
                                        <path d="M16 14v.5"></path>
                                        <path d="M11.25 16.25h1.5L12 17l-.75-.75Z"></path>
                                    </svg>
                                </div>
                            </div> 
                        }
                    </table>
                </div>
            </div>
        </div>
    )
}