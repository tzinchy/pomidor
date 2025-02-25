import { useState } from "react";
import { RefreshCcw } from "lucide-react";
import { HOSTLINK } from "../..";

export default function UpdateDataButton() {
    const [isModalOpen, setModalOpen] = useState(false);
    const [updateHistory, setUpdateHistory] = useState([]);

    const handleUpdate = async (type, url) => {
        try {
            const response = await fetch(url, { method: "PATCH" });
            if (!response.ok) throw new Error("Ошибка обновления");
            
            setUpdateHistory(prev => [
                { type, timestamp: new Date().toLocaleString() },
                ...prev,
            ]);
            console.log(updateHistory);
        } catch (error) {
            console.error("Ошибка запроса:", error);
        }
    };

    return (
        <div className="flex flex-col items-center">
            <button
                className=" absolute bottom-5 p-2 bg-blue-500 text-white rounded-full hover:bg-blue-600"
                onClick={() => setModalOpen(true)}
            >
                <RefreshCcw size={24} />
            </button>
            
            {isModalOpen && (
                <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
                    <div className="bg-white p-6 rounded-lg shadow-lg items-center justify-items-center w-96">
                        <h2 className="text-lg font-semibold mb-4">Обновление данных</h2>
                        
                        <div className="grid grid-cols-2 gap-4 items-center justify-items-center mb-4">
                            <button
                                className="px-4 py-2 border items-center rounded-md justify-self-center hover:bg-gray-50 bg-white"
                                onClick={() => handleUpdate("Обновить старые дома", HOSTLINK+'/rsm/get_old_apart')}
                            >
                                Обновить старые дома
                            </button>
                            <button
                                className="px-4 py-2 border items-center rounded-md justify-self-center hover:bg-gray-50 bg-white"
                                onClick={() => handleUpdate("Обновить новые дома", "/rsm/get_new_apart")}
                            >
                                Обновить новые дома
                            </button>
                        </div>
                        
                        <h3 className="text-md font-medium mb-2">История обновлений:</h3>
                        <div className="max-h-40 overflow-auto border rounded p-2">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b">
                                        <th className="text-left p-1">Тип</th>
                                        <th className="text-left p-1">Время</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {updateHistory.length > 0 ? (
                                        updateHistory.map((entry, index) => (
                                            <tr key={index} className="border-b">
                                                <td className="p-1">{entry.type}</td>
                                                <td className="p-1 text-gray-500">{entry.timestamp}</td>
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