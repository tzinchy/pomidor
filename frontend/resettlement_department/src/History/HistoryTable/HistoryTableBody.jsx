import React from "react";
import IdCell from "./Cells/IdCell";
import AddressCell from "./Cells/AddressCell";
import ActionsCell from "./Cells/ActionsCell";

export default function HistoryTableBody({ data }){
    return (
        <tbody>
            {data.map((val, index) => (
                <tr key={index} className={`bg-white border-b transition-colors hover:bg-gray-100`} >
                    <IdCell props={val} />
                    <AddressCell address={val.old_house_addresses} />
                    <AddressCell address={val.new_house_addresses} />
                    <ActionsCell props={val}/>
                </tr>
            ))}
        </tbody>
    )
}