import React, {useState, useEffect} from "react";
import { TableHead } from "../../PloshadkiTable/Table/Components";
import HistoryTableBody from "./HistoryTableBody";
import { HOSTLINK } from "../..";
import ConfirmationModal from "../../ApartTable/ConfirmationModal";
import api from "../../api";

  const paramsSerializer = {
    indexes: null,
    encode: (value) => encodeURIComponent(value)
  };



export default function HistoryTable(){
    const headers = ["Номер истории", "Старый дом", "Новый дом", ""]
    const [data, setData] = useState([])
    const [showConfirmContainerUpload, setShowConfirmContainerUpload] = useState(false);
    const [historyId, setHistoryId] = useState(null); 
    const [loadingHistoryId, setLoadingHistoryId] = useState(null);


    const upload_container = async (history_id) => {
    try {
        console.log(`${HOSTLINK}/push_container/${history_id}`)
        const response = await api.post(
        `${HOSTLINK}/push_container/${history_id}`,
        null,
        );
        if (response.status === 200) {
        // Обновляем локальные данные, изменяя status_id для выбранного history_id
        console.log("before update", data.find(item => item.history_id === history_id));
        setData(prevData => 
            prevData.map(item => 
            item.history_id === history_id ? { ...item, status_id: 1, is_downloaded : true } : item
            )
        );
        console.log("after update", data.find(item => item.history_id === history_id));
        }
    } catch (error) {
        console.error("Error:", error.response?.data);
    }
    };

    const handleConfirmContainerUpload = async (history_id) => {
    setShowConfirmContainerUpload(false);         // сразу скрыть модалку
    setLoadingHistoryId(history_id);              // начать загрузку
    await upload_container(history_id);
    setHistoryId(null);
    setLoadingHistoryId(null);                    // убрать загрузку
    };



    useEffect(() => { 
        fetch(`${HOSTLINK}/history`, {credentials: 'include',})
        .then((res) => res.json())
        .then((fetchedData) => {
            setData(fetchedData);
            console.log(fetchedData);
        });
    }, []);

    return (
        <div>
                              <div className="flex w-full flex-row items-center justify-start gap-1">
                    {showConfirmContainerUpload && (
                    <ConfirmationModal
                      isOpen={showConfirmContainerUpload}
                      onClose={() => setShowConfirmContainerUpload(false)}
                      onConfirm={async () => await handleConfirmContainerUpload(historyId)}
                      title={<span>Подтверждение действия</span>}
                      message={
                        <span>
                          Вы хотите загрузить контейнер, продолжить?
                        </span>
                      }
                      confirmText="Да, продолжить"
                    />
                  )}
                  </div>

        <div className="relative flex flex-col lg:flex-row h-[90vh] gap-2 bg-neutral-100 w-full transition-all duration-300">

            <div className="relative flex w-full">
                <div className="overflow-auto rounded-md border absolute left-0 h-full transition-all ease-in-out w-[calc(100%)] scrollbar-custom">
                    <table className="text-sm caption-bottom w-full border-collapse bg-white transition-all duration-300">
                        <TableHead headers={headers} />
                        <HistoryTableBody 
                        data={data} 
                        loadingHistoryId={loadingHistoryId}
                        setData={setData} 
                        setShowConfirmContainerUpload={setShowConfirmContainerUpload}
                        setHistoryId={setHistoryId} />
                    </table>
                </div>
            </div>
        </div>
                </div>
    )
}