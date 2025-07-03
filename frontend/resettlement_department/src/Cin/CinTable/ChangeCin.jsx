import React, { useState, useEffect } from "react";
import AirDatepicker from 'air-datepicker';
import 'air-datepicker/air-datepicker.css';
import localeRu from 'air-datepicker/locale/ru';
import { parseISO, isValid, format } from 'date-fns';

export default function ChangeCin({ props: rowData }) {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [formData, setFormData] = useState({
        cin_address: '',
        address: '',
        phone_osmotr: '',
        phone_otvet: '',
        otdel: '',
        cin_schedule: '',
        dep_schedule: '',
        start_dates_by_entrence: {}
    });
    const [dates, setDates] = useState({});
    const [entrances, setEntrances] = useState(['1']);
    const [newEntranceNumber, setNewEntranceNumber] = useState('');

    // Форматирование даты в YYYY-MM-DD
    const formatDateToShort = (dateString) => {
        if (!dateString) return '';
        const date = new Date(dateString);
        return format(date, 'yyyy-MM-dd');
    };

    // Синхронизация dates с formData с правильным форматом даты
    useEffect(() => {
        const formattedDates = {};
        for (const key in dates) {
            formattedDates[key] = formatDateToShort(dates[key]);
        }
        
        setFormData(prev => ({
            ...prev,
            start_dates_by_entrence: formattedDates
        }));
    }, [dates]);

    // Инициализация формы
    useEffect(() => {
        if (rowData && isModalOpen) {
            // Парсим даты по подъездам
            const datesData = rowData.start_dates_by_entrence;
            let parsedDates = {};
            
            try {
                parsedDates = typeof datesData === 'string' 
                    ? JSON.parse(datesData) 
                    : datesData || {};
            } catch (e) {
                console.error('Error parsing dates:', e);
            }

            // Фильтруем невалидные даты
            const validDates = {};
            for (const key in parsedDates) {
                if (parsedDates[key]) {
                    const date = parseISO(parsedDates[key]);
                    if (isValid(date)) {
                        validDates[key] = parsedDates[key];
                    }
                }
            }

            // Получаем список подъездов
            const entranceList = Object.keys(validDates).length > 0 
                ? Object.keys(validDates).sort((a, b) => parseInt(a) - parseInt(b))
                : rowData.entrances || ['1'];

            setFormData({
                cin_address: rowData.cin_address || '',
                address: rowData.address || '',
                phone_osmotr: rowData.phone_osmotr || '',
                phone_otvet: rowData.phone_otvet || '',
                otdel: rowData.otdel || '',
                cin_schedule: rowData.cin_schedule || '',
                dep_schedule: rowData.dep_schedule || '',
                start_dates_by_entrence: validDates
            });
            
            setDates(validDates);
            setEntrances(entranceList);
        }
    }, [rowData, isModalOpen]);

    const handleOpenModal = () => {
        setIsModalOpen(true);
    };
    
    const handleCloseModal = () => {
        setIsModalOpen(false);
        setNewEntranceNumber('');
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleDateChange = (entrance, dateString) => {
        setDates(prev => ({
            ...prev,
            [entrance]: dateString
        }));
    };

    const handleAddEntrance = () => {
        if (!newEntranceNumber.trim()) return;
        
        const entranceNum = newEntranceNumber.trim();
        if (entrances.includes(entranceNum)) {
            alert('Подъезд с таким номером уже существует');
            return;
        }

        setEntrances(prev => [...prev, entranceNum].sort((a, b) => parseInt(a) - parseInt(b)));
        setDates(prev => ({
            ...prev,
            [entranceNum]: new Date().toISOString()
        }));
        setNewEntranceNumber('');
    };

    const handleRemoveEntrance = (entrance) => {
        if (entrances.length <= 1) return;
        
        setEntrances(prev => prev.filter(e => e !== entrance));
        setDates(prev => {
            const newDates = { ...prev };
            delete newDates[entrance];
            return newDates;
        });
    };

    const handleSubmit = () => {
        console.log('Отправляемые данные:', formData);
        // Здесь будет логика отправки данных на сервер
    };

    // Инициализация datepicker для каждого подъезда
    useEffect(() => {
        if (isModalOpen) {
            entrances.forEach(entrance => {
                new AirDatepicker(`#datepicker-${entrance}`, {
                    locale: localeRu,
                    dateFormat: 'dd.MM.yyyy',
                    selectedDates: [dates[entrance] ? new Date(dates[entrance]) : new Date()],
                    onSelect: ({ date }) => {
                        handleDateChange(entrance, date.toISOString());
                    }
                });
            });
        }
    }, [isModalOpen, entrances, dates]);
    return (
        <>
            <button
                className="flex-shrink-0 p-1 text-gray-400 hover:text-blue-500 transition-colors"
                onClick={handleOpenModal}
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                    />
                </svg>
            </button>

            {isModalOpen && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-xl font-semibold">Редактирование ЦИНа</h2>
                            <button 
                                onClick={handleCloseModal}
                                className="text-gray-500 hover:text-gray-700"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Адрес ЦИНа</label>
                                    <input
                                        name="cin_address"
                                        type="text"
                                        value={formData.cin_address}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                    />
                                </div>
                                
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Адрес заселения</label>
                                    <input
                                        name="address"
                                        type="text"
                                        value={formData.address}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                    />
                                </div>
                                
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Телефон для осмотра</label>
                                    <input
                                        name="phone_osmotr"
                                        type="text"
                                        value={formData.phone_osmotr}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                    />
                                </div>
                            </div>
                            
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">График работы ЦИН</label>
                                    <input
                                        name="cin_schedule"
                                        type="text"
                                        value={formData.cin_schedule}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                    />
                                </div>
                                
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">График работы Департамента</label>
                                    <input
                                        name="dep_schedule"
                                        type="text"
                                        value={formData.dep_schedule}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                    />
                                </div>
                                
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Телефон для ответа</label>
                                    <input
                                        name="phone_otvet"
                                        type="text"
                                        value={formData.phone_otvet}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Секция с датами по подъездам */}
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

                        <div className="mt-6">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Адрес Отдела</label>
                            <input
                                name="otdel"
                                type="text"
                                value={formData.otdel}
                                onChange={handleInputChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                            />
                        </div>
                        
                        <div className="mt-6 flex justify-end space-x-3">
                            <button
                                type="button"
                                onClick={handleCloseModal}
                                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                            >
                                Отмена
                            </button>
                            <button
                                type="button"
                                onClick={console.log('formData', formData)}
                                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                            >
                                Сохранить
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    )
}