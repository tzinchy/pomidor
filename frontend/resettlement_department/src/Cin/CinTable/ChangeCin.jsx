import { useState, useEffect } from "react";
import AirDatepicker from 'air-datepicker';
import 'air-datepicker/air-datepicker.css';
import localeRu from 'air-datepicker/locale/ru';
import { parseISO, isValid, format } from 'date-fns';
import ScheduleSelector from "./ScheduleSelector";
import ChangeEntrences from "./ChangeEntrences";
import { HOSTLINK } from "../..";
import AddressDropdown from "./AddressDropdown";
import axios from "axios"; 

export default function ChangeCin({ props: rowData , fetchTableData, type = "edit" }) {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [formData, setFormData] = useState({});
    const [dates, setDates] = useState({});
    const [entrances, setEntrances] = useState(['1']);
    const [newEntranceNumber, setNewEntranceNumber] = useState('');
    const [phoneParts, setPhoneParts] = useState({
        osmotr: { main: '', ext: '' },
        otvet: { main: '', ext: '' }
    });
    const [showCustomSchedule, setShowCustomSchedule] = useState(false);
    const [customSchedule, setCustomSchedule] = useState({
        days: [],
        timeFrom: '08:00',
        timeTo: '17:00'
    });
    const [districtOptions, setDistrictOptions] = useState([]);
    const [municipalOptions, setMunicipalOptions] = useState([]);
    const daysOfWeek = [
        { id: 'mon', label: 'пн' },
        { id: 'tue', label: 'вт' },
        { id: 'wed', label: 'ср' },
        { id: 'thu', label: 'чт' },
        { id: 'fri', label: 'пт' },
        { id: 'sat', label: 'сб' },
        { id: 'sun', label: 'вс' }
    ];
    const [newAddresses, setNewAddresses] = useState([]);
    const vseOtdel = ['ул. Бахрушина, д. 18, стр. 1, каб. 403 (с понедельника по четверг с 8:00 до 17:00, пятница с 8:00 до 15:45, перерыв на обед ежедневно с 12:00 до 12:45)', 
        'ул. Ивана Франко, д. 8, корп. 2, каб. 10 (с понедельника по четверг с 8:00 до 17:00, пятница с 8:00 до 15:45, перерыв на обед ежедневно с 12:00 до 12:45)',
        'ул. Фабрициуса, д. 9, каб. 1 (с понедельника по четверг с 8:00 до 17:00, пятница с 8:00 до 15:45, перерыв на обед ежедневно с 12:00 до 12:45)',
        'ул. Руставели, д. 10, корп. 3 каб. 22, 27, 28 (с понедельника по четверг с 8:00 до 17:00, пятница с 8:00 до 15:45, перерыв на обед ежедневно с 12:00 до 12:45)',
        'ул. Руставели, д. 10, корп. 3, каб. 8, 9, 10 (с понедельника по четверг с 8:00 до 17:00, пятница с 8:00 до 15:45, перерыв на обед ежедневно с 12:00 до 12:45)',
        'ул. Стромынка, д. 3, каб. 304 (график работы: понедельник – четверг с 8:00 до 17:00, пятница с 8:00 до 15:45, перерыв на обед с 12:00 до 12:45)', 
        'Университетский просп., д. 6, корп. 1, каб. 4, 5 (с понедельника по четверг с 8:00 до 17:00, пятница с 8:00 до 15:45, перерыв на обед ежедневно с 12:15 до 13:00)',
        'Университетский просп., д. 6, корп. 1, каб. 1, 2, 3 (с понедельника по четверг с 8:00 до 17:00, пятница с 8:00 до 15:45, перерыв на обед ежедневно с 12:00 до 12:45)',
        'Университетский просп., д. 6, корп. 1, каб. 4, 5 (с понедельника по четверг с 8:00 до 17:00, пятница с 8:00 до 15:45, перерыв на обед ежедневно с 12:00 до 12:45)']

    useEffect(() => { 
        const fetchData = async () => {
            try {
                // Загрузка адресов
                const url = new URL(`${HOSTLINK}/tables/house_addresses`);
                url.searchParams.append('apart_type', 'NewApartment');            
                const response = await fetch(url.toString());
                const fetchedData = await response.json();
                setNewAddresses(fetchedData);

                // Загрузка районов с параметром apart_type
                const districtsUrl = new URL(`${HOSTLINK}/tables/district`);
                districtsUrl.searchParams.append('apart_type', 'NewApartment');
                const districtsResponse = await fetch(districtsUrl.toString());
                const districtsData = await districtsResponse.json();
                setDistrictOptions(districtsData);

                // Загрузка муниципальных округов с параметром apart_type
                const municipalUrl = new URL(`${HOSTLINK}/tables/municipal_district`);
                municipalUrl.searchParams.append('apart_type', 'NewApartment');
                const municipalResponse = await fetch(municipalUrl.toString());
                const municipalData = await municipalResponse.json();
                setMunicipalOptions(municipalData);
            } catch (error) {
                console.log('Error fetching data: ', error);
            }
        };
        
        fetchData();
    }, []);

    // Форматирование даты в YYYY-MM-DD
    const formatDateToShort = (dateString) => {
        if (!dateString) return '';
        const date = new Date(dateString);
        return format(date, 'yyyy-MM-dd');
    };

    // Разбор телефонного номера на основную часть и добавочную
    const parsePhoneNumber = (phone) => {
        if (!phone) return { main: '', ext: '' };
        const parts = phone.split('доп.');
        return {
            main: parts[0].trim(),
            ext: parts[1] ? parts[1].trim() : ''
        };
    };

    // Форматирование телефона при вводе
    const formatPhoneInput = (value) => {
        const cleanedValue = value.replace(/\D/g, '');
        
        let formattedValue = '';
        if (cleanedValue.length > 0) {
            formattedValue = `+7 (${cleanedValue.substring(1, 4)}`;
            if (cleanedValue.length > 4) {
                formattedValue += `) ${cleanedValue.substring(4, 7)}`;
            }
            if (cleanedValue.length > 7) {
                formattedValue += `-${cleanedValue.substring(7, 9)}`;
            }
            if (cleanedValue.length > 9) {
                formattedValue += `-${cleanedValue.substring(9, 11)}`;
            }
        }
        return formattedValue;
    };

    // Синхронизация dates с formData с правильным форматом даты
    useEffect(() => {
        const formattedDates = {};
        for (const key in dates) {
            formattedDates[key] = formatDateToShort(dates[key]);
        }
        
        setFormData(prev => ({
            ...prev,
            start_dates_by_entrence: formattedDates,
            // Для создания используем дату первого подъезда как start_date
            start_date: formattedDates['1'] || formatDateToShort(new Date())
        }));
    }, [dates]);

    // Инициализация формы
    useEffect(() => {
        if (rowData && isModalOpen && type === "edit") {
            // Копируем все данные из rowData в formData
            setFormData({ ...rowData });

            // Парсим даты
            const datesData = rowData.start_dates_by_entrence;
            let parsedDates = {};
            
            try {
                parsedDates = typeof datesData === 'string' 
                    ? JSON.parse(datesData) 
                    : datesData || {};
            } catch (e) {
                console.error('Error parsing dates:', e);
            }

            const validDates = {};
            for (const key in parsedDates) {
                if (parsedDates[key]) {
                    const date = parseISO(parsedDates[key]);
                    if (isValid(date)) {
                        validDates[key] = parsedDates[key];
                    }
                }
            }

            const entranceList = Object.keys(validDates).length > 0 
                ? Object.keys(validDates).sort((a, b) => parseInt(a) - parseInt(b))
                : rowData.entrances || ['1'];

            const osmotrPhone = parsePhoneNumber(rowData.phone_osmotr || '');
            const otvetPhone = parsePhoneNumber(rowData.phone_otvet || '');

            setPhoneParts({
                osmotr: osmotrPhone,
                otvet: otvetPhone
            });
            
            setDates(validDates);
            setEntrances(entranceList);

            // Инициализация кастомного графика, если он есть
            if (rowData.cin_schedule && !['time2plan', 'закрыто'].includes(rowData.cin_schedule)) {
                initCustomSchedule(rowData.cin_schedule);
            }
        } else if (isModalOpen && type === "create") {
            // Инициализация для создания нового ЦИНа
            const initialDate = formatDateToShort(new Date());
            setFormData({
                start_dates_by_entrence: { '1': initialDate },
                start_date: initialDate,
                district: '',
                municipal_district: ''
            });
            setDates({ '1': initialDate });
            setEntrances(['1']);
            setPhoneParts({
                osmotr: { main: '', ext: '' },
                otvet: { main: '', ext: '' }
            });
        }
    }, [rowData, isModalOpen, type]);

    // Инициализация кастомного графика из строки
    const initCustomSchedule = (scheduleString) => {
        const timeRegex = /(\d{2}:\d{2})-(\d{2}:\d{2})/;
        const timeMatch = scheduleString.match(timeRegex);
        
        if (timeMatch) {
            const daysPart = scheduleString.split(timeMatch[0])[0].trim();
            const selectedDays = daysOfWeek
                .filter(day => daysPart.includes(day.label))
                .map(day => day.id);
            
            setCustomSchedule({
                days: selectedDays,
                timeFrom: timeMatch[1],
                timeTo: timeMatch[2]
            });
            
            setShowCustomSchedule(true);
        }
    };

    const handleOpenModal = () => {
        setIsModalOpen(true);
    };
    
    const handleCloseModal = () => {
        setIsModalOpen(false);
        setNewEntranceNumber('');
        setShowCustomSchedule(false);
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

    const handlePhoneChange = (e, phoneType) => {
        const value = e.target.value;
        const formattedValue = formatPhoneInput(value);
        
        setPhoneParts(prev => {
            const newParts = {
                ...prev,
                [phoneType]: {
                    ...prev[phoneType],
                    main: formattedValue
                }
            };
            
            setFormData(prevFormData => ({
                ...prevFormData,
                [`phone_${phoneType}`]: newParts[phoneType].ext 
                    ? `${newParts[phoneType].main} доп. ${newParts[phoneType].ext}`
                    : newParts[phoneType].main
            }));
            
            return newParts;
        });
    };

    const handlePhoneExtChange = (e, phoneType) => {
        const value = e.target.value.replace(/\D/g, '').slice(0, 4);
        
        setPhoneParts(prev => {
            const newParts = {
                ...prev,
                [phoneType]: {
                    ...prev[phoneType],
                    ext: value
                }
            };
            
            setFormData(prevFormData => ({
                ...prevFormData,
                [`phone_${phoneType}`]: value 
                    ? `${newParts[phoneType].main} доп. ${value}`
                    : newParts[phoneType].main
            }));
            
            return newParts;
        });
    };

    const prepareFormData = () => {
        const data = { ...formData };
        
        // Убедимся, что все обязательные поля присутствуют
        if (type === "create") {
            if (!data.unom) {
                alert('Поле UNOM обязательно для заполнения');
                return null;
            }
        }
        
        // Преобразуем даты в правильный формат
        if (data.start_dates_by_entrence) {
            const formattedDates = {};
            for (const key in data.start_dates_by_entrence) {
                formattedDates[key] = formatDateToShort(data.start_dates_by_entrence[key]);
            }
            data.start_dates_by_entrence = formattedDates;
        }

        return data;
    };

    const handleSubmit = async () => {
        const preparedData = prepareFormData();
        if (!preparedData) return;
        
        console.log('Отправляемые данные:', preparedData);
        
        try {
            let response;
            if (type === "create") {
                response = await axios.post(`${HOSTLINK}/cin/create_cin`, preparedData);
            } else {
                response = await axios.patch(`${HOSTLINK}/cin/update_cin`, preparedData);
            }
            
            console.log('Успешное обновление:', response.data);
            fetchTableData();
            setIsModalOpen(false);
        } catch (error) {
            console.error('Ошибка:', error.response?.data || error.message);
            alert(`Ошибка при ${type === "create" ? 'создании' : 'обновлении'} ЦИНа: ${error.response?.data?.detail || error.message}`);
        }
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
                {type === "create" ? (
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                ) : (
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
                )}
            </button>

            {isModalOpen && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-xl font-semibold">
                                {type === "create" ? "Создание нового ЦИНа" : "Редактирование ЦИНа"}
                            </h2>
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
                                    <AddressDropdown 
                                        addresses={newAddresses} 
                                        value={formData.cin_address || ''}
                                        onChange={(value) => setFormData(prev => ({ ...prev, cin_address: value }))}
                                        placeholder="Выберите адрес ЦИНа"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">"Правильный" адрес ЦИНа</label>
                                    <input
                                        name="full_cin_address"
                                        type="text"
                                        value={formData.full_cin_address || ''}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Округ</label>
                                    <AddressDropdown 
                                        addresses={districtOptions} 
                                        value={formData.district || ''}
                                        onChange={(value) => setFormData(prev => ({ ...prev, district: value }))}
                                        placeholder="Выберите район"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">График работы ЦИНа</label>
                                    <ScheduleSelector 
                                        value={formData.cin_schedule || ''} 
                                        onChange={(value) => setFormData(prev => ({ ...prev, cin_schedule: value }))}
                                        type='cin' 
                                    />
                                </div>
                                
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Телефон для осмотра</label>
                                    <div className="flex gap-2">
                                        <input
                                            type="text"
                                            value={phoneParts.osmotr.main}
                                            onChange={(e) => handlePhoneChange(e, 'osmotr')}
                                            placeholder="+7 (XXX) XXX XX XX"
                                            className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                        />
                                        <div className="flex items-center">
                                            <span className="px-2 text-gray-500">доп.</span>
                                            <input
                                                type="text"
                                                value={phoneParts.osmotr.ext}
                                                onChange={(e) => handlePhoneExtChange(e, 'osmotr')}
                                                placeholder="XXXX"
                                                maxLength={4}
                                                className="w-20 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                            />
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Адрес заселения</label>
                                    <AddressDropdown 
                                        addresses={newAddresses} 
                                        value={formData.house_address || ''}
                                        onChange={(value) => setFormData(prev => ({ ...prev, house_address: value }))}
                                        placeholder="Выберите адрес заселения"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">"Правильный" адрес заселения</label>
                                    <input
                                        name="full_house_address"
                                        type="text"
                                        value={formData.full_house_address || ''}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Район</label>
                                    <AddressDropdown 
                                        addresses={municipalOptions} 
                                        value={formData.municipal_district || ''}
                                        onChange={(value) => setFormData(prev => ({ ...prev, municipal_district: value }))}
                                        placeholder="Выберите муниципальный округ"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">График работы Департамента</label>
                                    <ScheduleSelector 
                                        value={formData.dep_schedule || ''} 
                                        onChange={(value) => setFormData(prev => ({ ...prev, dep_schedule: value }))}
                                        type='dep' 
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Телефон для ответа</label>
                                    <div className="flex gap-2">
                                        <input
                                            type="text"
                                            value={phoneParts.otvet.main}
                                            onChange={(e) => handlePhoneChange(e, 'otvet')}
                                            placeholder="+7 (XXX) XXX XX XX"
                                            className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                        />
                                        <div className="flex items-center">
                                            <span className="px-2 text-gray-500">доп.</span>
                                            <input
                                                type="text"
                                                value={phoneParts.otvet.ext}
                                                onChange={(e) => handlePhoneExtChange(e, 'otvet')}
                                                placeholder="XXXX"
                                                maxLength={4}
                                                className="w-20 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                            />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Секция с датами по подъездам */}
                        <ChangeEntrences 
                            newEntranceNumber={newEntranceNumber}
                            setNewEntranceNumber={setNewEntranceNumber}
                            handleAddEntrance={handleAddEntrance}
                            entrances={entrances}
                            handleRemoveEntrance={handleRemoveEntrance}
                        />

                        <div className="mt-6">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Адрес Отдела</label>
                            <AddressDropdown 
                                addresses={vseOtdel} 
                                value={formData.otdel}
                                onChange={(value) => setFormData(prev => ({ ...prev, otdel: value }))}
                                placeholder="Выберите адрес ЦИНа"
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
                                onClick={handleSubmit}
                                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                            >
                                {type === "create" ? "Создать" : "Сохранить"}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}