import { useState, useEffect } from "react";
import { RefreshCcw } from "lucide-react";
import { HOSTLINK } from "../..";
import { RiskIcon } from "../../PloshadkiTable/Table/Icons";
import FileUploader from "../../Balance/Components/FileUploader";
import ToolTip from "../ToolTip";

export default function UpdateDataButton() {
    const [isModalOpen, setModalOpen] = useState(false);
    const [updateHistory, setUpdateHistory] = useState([]);
    const [statData, setStatData] = useState([]);
    const [loadingStates, setLoadingStates] = useState({
        need: false,
        resource: false,
        oldApart: false,
        newApart: false,
        offers: false,
        orderDecisions: false,
        done: false
    });

    const handleUpdate = async (type, url) => {
        try {
            // Устанавливаем состояние загрузки для соответствующей кнопки
            setLoadingStates(prev => ({
                ...prev,
                [type === "Потребность" ? "need" : 
                 type === "Ресурс" ? "resource" :
                 type === "Выписки" ? "orders" :
                 type === "Запустить триггер" ? "done" :
                 type === "oldApart" ? "oldApart" :
                 type === "newApart" ? "newApart" : "orderDecisions"]: true
            }));

            const response = await fetch(url, { method: "PATCH" , credentials: 'include',});
            if (!response.ok) throw new Error("Ошибка обновления");
            
            // Обновляем историю после успешного обновления
            await fetchAddresses();
        } catch (error) {
            console.error("Ошибка запроса:", error);
        } finally {
            // Снимаем состояние загрузки
            setLoadingStates(prev => ({
                ...prev,
                [type === "Потребность" ? "need" : 
                 type === "Ресурс" ? "resource" :
                 type === "Выписки" ? "orders" : 
                 type === "Запустить триггер" ? "done" :
                 type === "oldApart" ? "oldApart" :
                 type === "newApart" ? "newApart" : "orderDecisions"]: false
            }));
        }
    };

    const handleDownload = async (type, url) => {
        try {
            // Устанавливаем состояние загрузки
            setLoadingStates(prev => ({
                ...prev,
                [type === "oldApart" ? "oldApart" :
                 type === "newApart" ? "newApart" : 
                 type === "offers" ? "offers" : "orderDecisions"]: true
            }));

            const response = await fetch(url, {credentials: 'include',});
            if (!response.ok) throw new Error("Ошибка загрузки файла");
            
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = downloadUrl;
            
            // Устанавливаем имя файла в зависимости от типа
            let filename = '';
            if (type === "oldApart") filename = 'old_apart.xlsx';
            else if (type === "newApart") filename = 'new_apart.xlsx';
            else if (type === "offers") filename = 'offers.xlsx';
            else filename = 'order_decisions.xlsx';
            
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
            window.URL.revokeObjectURL(downloadUrl);
        } catch (error) {
            console.error("Ошибка загрузки:", error);
        } finally {
            setLoadingStates(prev => ({
                ...prev,
                [type === "oldApart" ? "oldApart" :
                 type === "newApart" ? "newApart" : 
                 type === "offers" ? "offers" : "orderDecisions"]: true
            }));
        }
    };

    const fetchAddresses = async () => {
        try {
            const response = await fetch(`${HOSTLINK}/rsm/update_info_stat`, {credentials: 'include',});
            if (!response.ok) throw new Error('Ошибка загрузки адресов');
            const data = await response.json();
            setUpdateHistory(data);
            console.log('RSM data',data);
        } catch (err) {
            console.log(err.message);
        }
    };

    const fetchStat = async () => {
        try {
            const response = await fetch(`${HOSTLINK}/tables/get_stat`, {credentials: 'include',});
            if (!response.ok) throw new Error('Ошибка загрузки статистики');
            const data = await response.json();
            console.log('stat data', data);
            setStatData(data);
        } catch (err) {
            console.log(err.message);
        }
    };

    return (
        <div className="flex flex-col items-center relative group">
                    <ToolTip text={`Обновить данные`} />
            <button
                className="p-2 mt-2  text-white rounded-full hover:bg-blue-100 rounded-md transition"
                onClick={() => { setModalOpen(true); fetchAddresses(); fetchStat();}}
            >
                <RefreshCcw size={24} className={"stroke-blue-500"}/>
            </button>
            
            {isModalOpen && (
                <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-[10]">
                    <div className="bg-white p-6 rounded-lg shadow-lg items-center justify-items-center w-[40%]">
                        <h2 className="text-lg font-semibold mb-4">Обновление данных</h2>
                        
                        <div className="grid grid-cols-4 gap-4 items-center justify-items-center mb-4">
                            <button
                                className={`px-4 py-2 border items-center rounded-md justify-self-center ${
                                    loadingStates.need 
                                        ? 'bg-gray-300 cursor-not-allowed' 
                                        : 'hover:bg-gray-50 bg-white'
                                }`}
                                onClick={() => handleUpdate("Потребность", HOSTLINK+'/rsm/get_old_apart')}
                                disabled={loadingStates.need}
                            >
                                {loadingStates.need ? (
                                    <span className="flex items-center">
                                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Обновление...
                                    </span>
                                ) : (
                                    "Потребность"
                                )}
                            </button>
                            <button
                                className={`px-4 py-2 border items-center rounded-md justify-self-center ${
                                    loadingStates.resource 
                                        ? 'bg-gray-300 cursor-not-allowed' 
                                        : 'hover:bg-gray-50 bg-white'
                                }`}
                                onClick={() => handleUpdate("Ресурс", HOSTLINK+"/rsm/get_new_apart")}
                                disabled={loadingStates.resource}
                            >
                                {loadingStates.resource ? (
                                    <span className="flex items-center">
                                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Обновление...
                                    </span>
                                ) : (
                                    "Ресурс"
                                )}
                            </button>
                            <button
                                className={`px-4 py-2 border items-center rounded-md justify-self-center ${
                                    loadingStates.orders 
                                        ? 'bg-gray-300 cursor-not-allowed' 
                                        : 'hover:bg-gray-50 bg-white'
                                }`}
                                onClick={() => handleUpdate("Выписки", HOSTLINK+"/rsm/get_orders")}
                                disabled={loadingStates.orders}
                            >
                                {loadingStates.orders ? (
                                    <span className="flex items-center">
                                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Обновление...
                                    </span>
                                ) : (
                                    "Выписки"
                                )}
                            </button>
                            <button
                                className={`px-4 py-2 border items-center rounded-md justify-self-center ${
                                    loadingStates.done 
                                        ? 'bg-gray-300 cursor-not-allowed' 
                                        : 'hover:bg-gray-50 bg-white'
                                }`}
                                onClick={() => handleUpdate("Запустить триггер", HOSTLINK+"/admin/use_sync_offer_status_strict")}
                                disabled={loadingStates.done}
                            >
                                {loadingStates.done ? (
                                    <span className="flex items-center">
                                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Обновление...
                                    </span>
                                ) : (
                                    "Запустить триггер"
                                )}
                            </button>
                        </div>

                        <h3 className="text-md font-medium mb-2">История обновлений:</h3>
                        <div className="max-h-40 overflow-auto border rounded p-2 mb-4">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b">
                                        <th className="text-left p-1">Тип</th>
                                        <th className="text-left p-1">Время</th>
                                        <th className="text-left p-1">Обновлено</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {updateHistory.length > 0 ? (
                                        updateHistory.map((entry, index) => (
                                            <tr key={index} className="">
                                                <td className="p-1">{entry.name === 'new_aparts_resource' ? 'Ресурс' : entry.name === 'old_aparts_kpu' ? 'Потребность' : 'Выписки'}</td>
                                                <td className="p-1 text-gray-500">{entry.timestamp.slice(8, 10)}.{entry.timestamp.slice(5, 7)}.{entry.timestamp.slice(0, 4)} | {entry.timestamp.slice(11, 16)}</td>
                                                <td className="p-1 flex text-gray-500 justify-center">{entry.is_active ? <RiskIcon risk='Работа завершена' /> : <RiskIcon risk='Наступили риски' /> }</td>
                                            </tr>
                                        ))
                                    ) : (
                                        <tr>
                                            <td colSpan="2" className="text-center text-gray-500 p-2">Нет обновлений</td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>

                        <h3 className="text-md font-medium mb-2">Скачать файлы:</h3>
                        <div className="grid grid-cols-4 gap-4 items-center justify-items-center mb-4">
                            <button
                                className={`px-4 py-2 border items-center rounded-md justify-self-center ${
                                    loadingStates.oldApart 
                                        ? 'bg-gray-300 cursor-not-allowed' 
                                        : 'hover:bg-gray-50 bg-white'
                                }`}
                                onClick={() => handleDownload("oldApart", HOSTLINK+'/tables/old_apart')}
                                disabled={loadingStates.oldApart}
                            >
                                {loadingStates.oldApart ? (
                                    <span className="flex items-center">
                                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Загрузка...
                                    </span>
                                ) : (
                                    "Старые квартиры"
                                )}
                            </button>
                            <button
                                className={`px-4 py-2 border items-center rounded-md justify-self-center ${
                                    loadingStates.newApart 
                                        ? 'bg-gray-300 cursor-not-allowed' 
                                        : 'hover:bg-gray-50 bg-white'
                                }`}
                                onClick={() => handleDownload("newApart", HOSTLINK+'/tables/new_apart')}
                                disabled={loadingStates.newApart}
                            >
                                {loadingStates.newApart ? (
                                    <span className="flex items-center">
                                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Загрузка...
                                    </span>
                                ) : (
                                    "Новые квартиры"
                                )}
                            </button>
                            <button
                                className={`px-4 py-2 border items-center rounded-md justify-self-center ${
                                    loadingStates.orderDecisions 
                                        ? 'bg-gray-300 cursor-not-allowed' 
                                        : 'hover:bg-gray-50 bg-white'
                                }`}
                                onClick={() => handleDownload("orderDecisions", HOSTLINK+'/tables/order_decisions')}
                                disabled={loadingStates.orderDecisions}
                            >
                                {loadingStates.orderDecisions ? (
                                    <span className="flex items-center">
                                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Загрузка...
                                    </span>
                                ) : (
                                    "Решения по заявкам"
                                )}
                            </button>
                            <button
                                className={`px-4 py-2 border items-center rounded-md justify-self-center ${
                                    loadingStates.offers 
                                        ? 'bg-gray-300 cursor-not-allowed' 
                                        : 'hover:bg-gray-50 bg-white'
                                }`}
                                onClick={() => handleDownload("offers", HOSTLINK+'/tables/offer_result')}
                                disabled={loadingStates.offers}
                            >
                                {loadingStates.offers ? (
                                    <span className="flex items-center">
                                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Загрузка...
                                    </span>
                                ) : (
                                    "Подборы"
                                )}
                            </button>
                        </div>
                        
                        <h3 className="text-md font-medium mb-2">Статистика записей:</h3>
                        <div className="max-h-40 overflow-auto border rounded p-2">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b">
                                        <th className="text-left p-1"></th>
                                        <th className="text-left p-1">Количество записей</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {Object.keys(statData).length > 0 ? (
                                        Object.entries(statData).map(([key, value]) => (
                                            <tr key={key}>
                                                <td className="p-1 capitalize">{key}</td>
                                                <td className="p-1">{value.toLocaleString()}</td>
                                            </tr>
                                        ))
                                    ) : (
                                        <tr>
                                            <td colSpan="2" className="text-center text-gray-500 p-2">Данные загружаются...</td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>

                        <FileUploader link={`/rsm/upload-file/`}/>
                        <button
                            className="mt-4 px-4 py-2 justify-self-center bg-gray-500 text-white rounded hover:bg-gray-600"
                            onClick={() => setModalOpen(false)}
                        >
                            Закрыть
                        </button>
                    </div>
                </div>
            )}

        </div>
    );
}