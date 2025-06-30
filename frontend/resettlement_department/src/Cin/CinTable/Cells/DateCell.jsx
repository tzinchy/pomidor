import { useState, useEffect, useRef } from 'react';
import { format, parseISO } from 'date-fns';
import AirDatepicker from 'air-datepicker';
import 'air-datepicker/air-datepicker.css';
import localeRu from 'air-datepicker/locale/ru';

export default function DateCell(props) {
  const [dates, setDates] = useState({});
  const datepickerRefs = useRef({});

  // Инициализация данных
  useEffect(() => {
    try {
      const datesData = props.props?.start_dates_by_entrence;
      
      const parsedDates = typeof datesData === 'string' 
        ? JSON.parse(datesData) 
        : datesData || {};
      
      setDates(parsedDates);
    } catch (e) {
      console.error('Error processing dates:', e);
      setDates({});
    }
  }, [props.props?.start_dates_by_entrence]);

  useEffect(() => {
    console.log('dates', dates);
  }, [dates])

  // Инициализация datepicker'ов
  const initDatepicker = (entranceId, inputElement) => {
    if (!inputElement || datepickerRefs.current[entranceId]) return;

    datepickerRefs.current[entranceId] = new AirDatepicker(inputElement, {
      locale: localeRu,
      dateFormat: 'dd.MM.yyyy',
      onSelect({ date: selectedDate }) {
        const isoDate = format(selectedDate, 'yyyy-MM-dd');
        const newDates = { 
          ...dates, // сохраняем все существующие данные
          [entranceId]: isoDate // обновляем только текущий подъезд
        };
        setDates(newDates);
        
        if (props.onChange) {
          props.onChange(JSON.stringify(newDates));
        }
      },
      autoClose: true,
    });

    // Устанавливаем текущую дату если она есть
    if (dates[entranceId]) {
      datepickerRefs.current[entranceId].selectDate(parseISO(dates[entranceId]));
    }
  };

  // Получаем список всех подъездов
  const getEntrances = () => {
    // Используем существующие подъезды из dates или props
    const entranceIds = Object.keys(dates).length > 0 
      ? Object.keys(dates) 
      : props.props.entrances || ['1'];
    
    return entranceIds.sort((a, b) => parseInt(a) - parseInt(b));
  };

  return (
    <div className="flex flex-col gap-2">
      {getEntrances().map(entranceId => (
        <div key={entranceId} className="flex items-center justify-between gap-2">
          <div className="flex-1 min-w-0 flex items-center">
            <span className="mr-2">Подъезд {entranceId}:</span>
            <div className="whitespace-nowrap overflow-hidden text-ellipsis">
              {dates[entranceId] 
                ? format(parseISO(dates[entranceId]), 'dd.MM.yyyy')
                : 'Дата не указана'}
            </div>
            <input
              ref={el => initDatepicker(entranceId, el)}
              type="text"
              className="absolute opacity-0 w-0 h-0"
              readOnly
            />
          </div>

          <button
            onClick={() => datepickerRefs.current[entranceId]?.show()}
            className="flex-shrink-0 p-1 text-gray-400 hover:text-blue-500 transition-colors"
            aria-label={`Изменить дату для подъезда ${entranceId}`}
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
        </div>
      ))}

      <style jsx global>{`
        .air-datepicker {
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
          border-radius: 8px;
        }
      `}</style>
    </div>
  );
}