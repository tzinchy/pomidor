import React from "react";
import IdCell from "../../History/HistoryTable/Cells/IdCell";
import AddressCell from "../../History/HistoryTable/Cells/AddressCell";

export default function CinTableBody({data, setData}) {
    return (
        <tbody>
            {data.map((val, index) => (
                <tr key={index} className={`bg-white border-b transition-colors hover:bg-gray-100`} >
                    <IdCell props={val} />
                    <AddressCell address={val.old_house_addresses} />
                </tr>
            ))}
        </tbody>
    )
}