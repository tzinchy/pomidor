import React, { useState, useEffect } from 'react';
import { Menu } from '@headlessui/react';

const daysOfWeek = [
    { id: 'mon', label: 'пн' },
    { id: 'tue', label: 'вт' },
    { id: 'wed', label: 'ср' },
    { id: 'thu', label: 'чт' },
    { id: 'fri', label: 'пт' },
    { id: 'sat', label: 'сб' },
    { id: 'sun', label: 'вс' }
];

const ScheduleSelector = ({ value, onChange, type }) => {
    const [showCustomSchedule, setShowCustomSchedule] = useState(false);
    const [scheduleType, setScheduleType] = useState('');
    const [daySchedules, setDaySchedules] = useState({});

    useEffect(() => {
        if (value === 'time2plan' || value === 'закрыто' || value === 'отдел') {
            setScheduleType(value);
            setShowCustomSchedule(false);
            setDaySchedules({});
        } else if (value) {
            setScheduleType('custom');
            setShowCustomSchedule(true);
            parseScheduleString(value);
        } else {
            setScheduleType('');
            setDaySchedules({});
        }
    }, [value]);

    const parseScheduleString = (scheduleStr) => {
        if (!scheduleStr) return;

        const newDaySchedules = {};
        
        // Разбиваем на отдельные части (дни и время)
        const parts = scheduleStr.split(', ');
        
        parts.forEach(part => {
            // Обрабатываем формат "Пн-Пт 09:00-18:00"
            const rangeMatch = part.match(/([А-Яа-я]+)-([А-Яа-я]+) (\d{2}:\d{2})-(\d{2}:\d{2})/);
            if (rangeMatch) {
                const [_, startDay, endDay, timeFrom, timeTo] = rangeMatch;
                const startIndex = daysOfWeek.findIndex(d => d.label === startDay);
                const endIndex = daysOfWeek.findIndex(d => d.label === endDay);
                
                if (startIndex !== -1 && endIndex !== -1) {
                    for (let i = startIndex; i <= endIndex; i++) {
                        newDaySchedules[daysOfWeek[i].id] = { timeFrom, timeTo };
                    }
                }
            } 
            // Обрабатываем формат "Пн,Ср,Пт 09:00-18:00"
            else if (part.includes(' ')) {
                const [daysPart, timePart] = part.split(' ');
                const [timeFrom, timeTo] = timePart.split('-');
                const days = daysPart.split(',');
                
                days.forEach(dayLabel => {
                    const day = daysOfWeek.find(d => d.label === dayLabel.trim());
                    if (day) {
                        newDaySchedules[day.id] = { timeFrom, timeTo };
                    }
                });
            }
            // Обрабатываем формат "Пн 09:00-18:00"
            else {
                const dayMatch = part.match(/([А-Яа-я]+) (\d{2}:\d{2})-(\d{2}:\d{2})/);
                if (dayMatch) {
                    const [_, dayLabel, timeFrom, timeTo] = dayMatch;
                    const day = daysOfWeek.find(d => d.label === dayLabel);
                    if (day) {
                        newDaySchedules[day.id] = { timeFrom, timeTo };
                    }
                }
            }
        });

        setDaySchedules(newDaySchedules);
    };

    const formatScheduleString = (schedules) => {
        // Сначала группируем дни с одинаковым временем
        const timeGroups = {};
        Object.entries(schedules).forEach(([dayId, time]) => {
            const key = `${time.timeFrom}-${time.timeTo}`;
            if (!timeGroups[key]) {
                timeGroups[key] = [];
            }
            timeGroups[key].push(dayId);
        });

        // Для каждой группы времени форматируем дни
        const result = [];
        Object.entries(timeGroups).forEach(([time, dayIds]) => {
            const [timeFrom, timeTo] = time.split('-');
            const sortedDays = dayIds.sort((a, b) => 
                daysOfWeek.findIndex(d => d.id === a) - daysOfWeek.findIndex(d => d.id === b)
            );

            // Группируем последовательные дни
            let groups = [];
            let currentGroup = [sortedDays[0]];
            
            for (let i = 1; i < sortedDays.length; i++) {
                const prevIndex = daysOfWeek.findIndex(d => d.id === sortedDays[i-1]);
                const currIndex = daysOfWeek.findIndex(d => d.id === sortedDays[i]);
                
                if (currIndex === prevIndex + 1) {
                    currentGroup.push(sortedDays[i]);
                } else {
                    groups.push(currentGroup);
                    currentGroup = [sortedDays[i]];
                }
            }
            groups.push(currentGroup);

            // Форматируем группы дней
            groups.forEach(group => {
                if (group.length === 1) {
                    result.push(`${daysOfWeek.find(d => d.id === group[0]).label} ${timeFrom}-${timeTo}`);
                } else {
                    const first = daysOfWeek.find(d => d.id === group[0]).label;
                    const last = daysOfWeek.find(d => d.id === group[group.length-1]).label;
                    result.push(`${first}-${last} ${timeFrom}-${timeTo}`);
                }
            });
        });

        return result.join(', ');
    };

    const handleScheduleTypeChange = (type) => {
        setScheduleType(type);
        
        if (type === 'custom') {
            setShowCustomSchedule(true);
        } else {
            setShowCustomSchedule(false);
            onChange(type);
            setDaySchedules({});
        }
    };

    const handleDayTimeChange = (dayId, field, value) => {
        const newDaySchedules = {
            ...daySchedules,
            [dayId]: {
                ...daySchedules[dayId],
                [field]: value
            }
        };
        
        setDaySchedules(newDaySchedules);
        const formatted = formatScheduleString(newDaySchedules);
        onChange(formatted);
    };

    const handleDayToggle = (dayId) => {
        const newDaySchedules = { ...daySchedules };
        
        if (newDaySchedules[dayId]) {
            delete newDaySchedules[dayId];
        } else {
            newDaySchedules[dayId] = { 
                timeFrom: '09:00', 
                timeTo: '18:00' 
            };
        }
        
        setDaySchedules(newDaySchedules);
        
        if (Object.keys(newDaySchedules).length > 0) {
            const formatted = formatScheduleString(newDaySchedules);
            onChange(formatted);
            setScheduleType('custom');
        } else {
            onChange('');
            setScheduleType('');
        }
    };

    const handleCloseCustomSchedule = () => {
        setShowCustomSchedule(false);
    };

    return (
        <div className="space-y-2">
            <Menu as="div" className="relative">
                <Menu.Button className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-left focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                    {Object.keys(daySchedules).length > 0 
                        ? formatScheduleString(daySchedules)
                        : scheduleType || 'Выберите график...'}
                </Menu.Button>
                <Menu.Items className="absolute z-10 mt-1 w-full bg-white shadow-lg rounded-md py-1 ring-1 ring-black ring-opacity-5 focus:outline-none">
                    {type === 'cin' ? (
                        <Menu.Item>
                            {({ active }) => (
                                <button
                                    onClick={() => handleScheduleTypeChange('time2plan')}
                                    className={`${active ? 'bg-gray-100' : ''} block px-4 py-2 text-sm text-gray-700 w-full text-left`}
                                >
                                    time2plan
                                </button>
                            )}
                        </Menu.Item>
                    ) : (
                        <Menu.Item>
                            {({ active }) => (
                                <button
                                    onClick={() => handleScheduleTypeChange('отдел')}
                                    className={`${active ? 'bg-gray-100' : ''} block px-4 py-2 text-sm text-gray-700 w-full text-left`}
                                >
                                    отдел
                                </button>
                            )}
                        </Menu.Item>
                    )}
                    <Menu.Item>
                        {({ active }) => (
                            <button
                                onClick={() => handleScheduleTypeChange('закрыто')}
                                className={`${active ? 'bg-gray-100' : ''} block px-4 py-2 text-sm text-gray-700 w-full text-left`}
                            >
                                закрыто
                            </button>
                        )}
                    </Menu.Item>
                    <Menu.Item>
                        {({ active }) => (
                            <button
                                onClick={() => handleScheduleTypeChange('custom')}
                                className={`${active ? 'bg-gray-100' : ''} block px-4 py-2 text-sm text-gray-700 w-full text-left`}
                            >
                                Выбрать дни
                            </button>
                        )}
                    </Menu.Item>
                </Menu.Items>
            </Menu>
            
            {showCustomSchedule && (
                <div className="mt-2 p-3 border border-gray-200 rounded-md space-y-3 relative">
                    <button
                        type="button"
                        onClick={handleCloseCustomSchedule}
                        className="absolute top-2 right-2 text-gray-500 hover:text-gray-700"
                        aria-label="Закрыть"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                        </svg>
                    </button>
                    
                    <div className="space-y-2">
                        <label className="block text-sm font-medium text-gray-700">Дни недели:</label>
                        <div className="flex flex-wrap gap-2">
                            {daysOfWeek.map(day => (
                                <button
                                    key={day.id}
                                    type="button"
                                    onClick={() => handleDayToggle(day.id)}
                                    className={`px-3 py-1 text-sm rounded-md ${
                                        daySchedules[day.id]
                                            ? 'bg-blue-500 text-white'
                                            : 'bg-gray-200 text-gray-700'
                                    }`}
                                >
                                    {day.label}
                                </button>
                            ))}
                        </div>
                    </div>
                    
                    {Object.keys(daySchedules).length > 0 && (
                        <div className="space-y-3">
                            <label className="block text-sm font-medium text-gray-700">Время работы:</label>
                            {Object.entries(daySchedules).map(([dayId, schedule]) => (
                                <div key={dayId} className="grid grid-cols-12 gap-2 items-center">
                                    <span className="col-span-2 text-sm font-medium">
                                        {daysOfWeek.find(d => d.id === dayId).label}:
                                    </span>
                                    <input
                                        type="time"
                                        value={schedule.timeFrom}
                                        onChange={(e) => handleDayTimeChange(dayId, 'timeFrom', e.target.value)}
                                        className="col-span-4 px-2 py-1 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                    />
                                    <span className="col-span-1 text-center">—</span>
                                    <input
                                        type="time"
                                        value={schedule.timeTo}
                                        onChange={(e) => handleDayTimeChange(dayId, 'timeTo', e.target.value)}
                                        className="col-span-4 px-2 py-1 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => handleDayToggle(dayId)}
                                        className="col-span-1 text-red-500 hover:text-red-700"
                                    >
                                        ×
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default ScheduleSelector;