import { useState, useEffect, useRef } from 'react';
import { format, parseISO, isValid } from 'date-fns';
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
      
      setDates(prevDates => {
        const mergedDates = { ...prevDates };
        for (const key in parsedDates) {
          if (parsedDates[key]) {
            const date = parseISO(parsedDates[key]);
            if (isValid(date)) {
              mergedDates[key] = parsedDates[key];
            }
          }
        }
        return mergedDates;
      });
    } catch (e) {
      console.error('Error processing dates:', e);
      setDates({});
    }
  }, [props.props?.start_dates_by_entrence]);

  // Получаем список всех подъездов
  const getEntrances = () => {
    const entranceIds = Object.keys(dates).length > 0 
      ? Object.keys(dates) 
      : props.props.entrances || ['1'];
    
    return entranceIds.sort((a, b) => parseInt(a) - parseInt(b));
  };

  const entrances = getEntrances();

  return (
    <div className="flex flex-col gap-2">
      {entrances.map(entranceId => (
        <div key={entranceId} className="flex items-center justify-between gap-2">
          <div className="flex-1 min-w-0 flex items-center">
            <span className="mr-2">Подъезд {entranceId}:</span>
            <div className="whitespace-nowrap overflow-hidden text-ellipsis">
              {dates[entranceId] 
                ? (() => {
                    const date = parseISO(dates[entranceId]);
                    return isValid(date) ? format(date, 'dd.MM.yyyy') : 'Неверная дата';
                  })()
                : 'Дата не указана'}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}