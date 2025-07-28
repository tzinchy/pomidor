
export default function ChangeEntrences({newEntranceNumber, setNewEntranceNumber, handleAddEntrance, entrances, handleRemoveEntrance}) {

    return (
        <div className="mt-6">
            <div className="flex justify-between items-center mb-2">
                <label className="block text-sm font-medium text-gray-700">Даты начала работы по подъездам</label>
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={newEntranceNumber}
                        onChange={(e) => setNewEntranceNumber(e.target.value)}
                        placeholder="Номер подъезда"
                        className="px-2 py-1 border border-gray-300 rounded-md shadow-sm w-32"
                    />
                    <button
                        type="button"
                        onClick={handleAddEntrance}
                        className="text-sm text-blue-600 hover:text-blue-800 whitespace-nowrap"
                    >
                        + Добавить подъезд
                    </button>
                </div>
            </div>
            
            <div className="space-y-2">
                {entrances.map(entrance => (
                    <div key={entrance} className="flex items-center gap-2">
                        <label className="w-20 text-sm text-gray-700">Подъезд {entrance}</label>
                        <input
                            id={`datepicker-${entrance}`}
                            type="text"
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                            readOnly
                        />
                        {entrances.length > 1 && (
                            <button
                                type="button"
                                onClick={() => handleRemoveEntrance(entrance)}
                                className="text-red-500 hover:text-red-700"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                            </button>
                        )}
                    </div>
                ))}
            </div>
        </div>
    )
}