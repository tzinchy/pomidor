import React from "react";
import IdCell from "./Cells/IdCell";
import AddressCell from "./Cells/AddressCell";
import ActionsCell from "./Cells/ActionsCell";

export default function HistoryTableBody({ 
    data, 
    setData, 
    setShowConfirmContainerUpload,
    setShowConfirmHistoryDelete,
    setShowConfirmApprove,
    setHistoryId, 
    loadingHistoryId }){
    return (
        <tbody>
            {data.map((val, index) => (
                <tr key={index} className={`bg-white border-b transition-colors hover:bg-gray-100`} >
                    <IdCell props={val} />
                    <AddressCell address={val.old_house_addresses} />
                    <AddressCell address={val.new_house_addresses} />
                    <ActionsCell
                    history_id={val.history_id}
                    status_id={val.status_id}
                    is_downloaded={val.is_downloaded}
                    is_wave={val.is_wave}
                    is_shadow={val.is_shadow}
                    setData={setData} 
                    setShowConfirmContainerUpload={setShowConfirmContainerUpload}
                    setHistoryId={setHistoryId}
                    loadingHistoryId={loadingHistoryId}
                    setShowConfirmHistoryDelete={setShowConfirmHistoryDelete}
                    setShowConfirmApprove={setShowConfirmApprove} />
                </tr>
            ))}
        </tbody>
    )
}