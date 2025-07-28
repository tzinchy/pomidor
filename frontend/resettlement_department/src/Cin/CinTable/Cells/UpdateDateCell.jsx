import { format, parseISO } from 'date-fns';
import { ru } from 'date-fns/locale';

const UpdateDateCell = ({ dateTimeString }) => {
  if (!dateTimeString) return null;
  
  try {
    const date = parseISO(dateTimeString);
    const timeFormat = 'HH:mm:ss';
    const dateFormat = 'dd.MM.yyyy';
    
    return (
      <div className="whitespace-nowrap">
        <span className="text-gray-600">
          {format(date, timeFormat)}
        </span>
        {' '}
        <span className="text-gray-900">
          {format(date, dateFormat, { locale: ru })}
        </span>
      </div>
    );
  } catch (e) {
    console.error('Invalid date format:', dateTimeString);
    return <span className="text-red-500">Invalid date</span>;
  }
};

export default UpdateDateCell;