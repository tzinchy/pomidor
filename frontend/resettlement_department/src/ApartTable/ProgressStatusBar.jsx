import React, { useState, useRef, useEffect } from "react";

const ProgressStatusBar = ({ data = {}, handleFilterChange }) => {
  const progressColors = {
    "Согласие": "#10b981",
    "Отказ": "#ef4444",
    "Суд": "#dc2626",
    "МФР Компенсация": "#a78bfa",
    "МФР Докупка": "#a78bfa",
    "МФР (вне района)": "#a78bfa",
    "МФР Компенсация (вне района)": "#a78bfa",
    "Ожидание": "#fbbf24",
    "Ждёт одобрения": "#3b82f6",
    "Подготовить смотровой": "#f76d0a",
    "Не подобрано": "#94a3b8",
    "Свободная": "#94a3b8",
    "Резерв": "#94a3b8",
    "Блок": "#94a3b8",
    "Подборов не будет": "#94a3b8",
    "Передано во вне": "#94a3b8"
  };

  const statusOrder = [
    "Отказ",
    "Суд",
    "МФР Компенсация",
    "МФР Докупка",
    "МФР (вне района)",
    "МФР Компенсация (вне района)",
    "Ждёт одобрения",
    "Ожидание",
    "Подготовить смотровой",
    "Не подобрано",
    "Свободная",
    "Резерв",
    "Блок",
    "Подборов не будет",
    "Передано во вне",
    "Согласие",
  ];

  const [isHovered, setIsHovered] = useState(false);
  const popupRef = useRef(null);
  const barRef = useRef(null);
  const timeoutRef = useRef(null);

  useEffect(() => {
    const handleMouseLeaveBar = (e) => {
      // Если курсор перешел на всплывающее окно - не закрываем
      if (e.relatedTarget && popupRef.current?.contains(e.relatedTarget)) {
        return;
      }
      // Иначе закрываем с небольшой задержкой
      timeoutRef.current = setTimeout(() => {
        setIsHovered(false);
      }, 100);
    };

    const handleMouseEnterPopup = () => {
      clearTimeout(timeoutRef.current);
    };

    const handleMouseLeavePopup = (e) => {
      // Если курсор перешел на прогресс-бар - не закрываем
      if (e.relatedTarget && barRef.current?.contains(e.relatedTarget)) {
        return;
      }
      // Иначе закрываем
      setIsHovered(false);
    };

    const bar = barRef.current;
    const popup = popupRef.current;

    if (bar) {
      bar.addEventListener('mouseleave', handleMouseLeaveBar);
    }

    if (popup) {
      popup.addEventListener('mouseenter', handleMouseEnterPopup);
      popup.addEventListener('mouseleave', handleMouseLeavePopup);
    }

    return () => {
      if (bar) {
        bar.removeEventListener('mouseleave', handleMouseLeaveBar);
      }
      if (popup) {
        popup.removeEventListener('mouseenter', handleMouseEnterPopup);
        popup.removeEventListener('mouseleave', handleMouseLeavePopup);
      }
      clearTimeout(timeoutRef.current);
    };
  }, []);

  const handleStatusClick = (status) => {
    if (handleFilterChange) {
      handleFilterChange('status', [status]);
      setIsHovered(false);
    }
  };

  const renderProgress = () => {
    if (!data || typeof data !== 'object' || Object.keys(data).length === 0) {
      return <div className="text-slate-500">-_-</div>;
    }

    const total = Object.values(data).reduce((sum, val) => sum + val, 0);
    
    const segments = statusOrder
      .map(key => ({
        key,
        value: data[key] || 0,
        percentage: total > 0 ? ((data[key] || 0) / total * 100) : 0,
        color: progressColors[key],
      }))
      .filter(segment => segment.value > 0);
      
    return (
      <div className="ml-4 relative w-full flex items-center">
        <div 
          ref={barRef}
          className="relative h-6 w-full bg-slate-200 rounded-md overflow-hidden flex"
          onMouseEnter={() => {
            clearTimeout(timeoutRef.current);
            setIsHovered(true);
          }}
        >
          {segments.map(({ key, percentage, color, value }) => (
            <div
              key={key}
              className="h-6 relative"
              style={{
                width: `${percentage}%`,
                backgroundColor: color,
                minWidth: percentage > 0 ? '2px' : '0',
              }}
            >
              {percentage >= 10 && (
                <div className="absolute inset-0 flex items-center font-bold justify-center text-xs text-white">
                  {value}
                </div>
              )}
            </div>
          ))}
        </div>

        <div 
          ref={popupRef}
          className={`absolute left-1/2 -translate-x-1/2 top-full mt-2 w-[200px] z-[10000] bg-white border border-slate-200 rounded-lg shadow-lg transition-all duration-200 ${
            isHovered ? 'opacity-100' : 'opacity-0 pointer-events-none'
          }`}
        >
          <table className="caption-bottom w-full text-sm">
            <tbody className="[&_tr:last-child]:border-0">
              {segments.map(({ key, value, color }) => (
                <tr
                  key={key}
                  className="hover:bg-muted/50 border-b transition-colors text-slate-500 cursor-pointer"
                  onClick={() => handleStatusClick(key)}
                >
                  <td className="align-middle [&:has([role=checkbox])]:pr-0 px-2 py-1 text-center text-xs">
                    <div
                      className="flex h-4 w-4 rounded"
                      style={{ backgroundColor: color }}
                    ></div>
                  </td>
                  <td className="align-middle [&:has([role=checkbox])]:pr-0 px-0 py-1 text-right text-xs font-bold">
                    {value}
                  </td>
                  <td className="align-middle [&:has([role=checkbox])]:pr-0 px-4 py-1 text-left text-xs">
                    {key}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <span className="absolute -top-2 left-1/2 -translate-x-1/2">
            <svg width="10" height="5" viewBox="0 0 30 10" preserveAspectRatio="none" className="block rotate-180">
              <polygon points="0,0 30,0 15,10"></polygon>
            </svg>
          </span>
        </div>
      </div>
    );
  };

  return renderProgress();
};

export default ProgressStatusBar;