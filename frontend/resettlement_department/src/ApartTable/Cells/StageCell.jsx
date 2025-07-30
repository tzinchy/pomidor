import React from "react";
import { format } from "date-fns";

export default function StageCell(props) {
  // Добавляем проверки на всех уровнях вложенности
  const apartment = props?.props || {};
  const classificator = apartment?.classificator || {};
  
  // Защита от отсутствия данных
  if (!apartment || !classificator) {
    return (
      <div className="flex w-full flex-row items-center justify-start gap-1">
        <div className="text-red-500 text-xs">Данные отсутствуют</div>
      </div>
    );
  }

  return (
    <div className="flex w-full flex-row items-center justify-start gap-1">
      <div className="flex flex-1 flex-col items-start justify-start truncate">
        <div className="flex items-center gap-1 truncate">
          {classificator?.action || 'Нет данных'}
        </div>
        <div className="text-gray-500 flex items-center gap-1 truncate text-xs">
          {classificator?.stageName ? `${classificator.stageName} ` : ''}
          {classificator?.stageDate && (
            <span className="opacity-60">
              ({format(
                new Date(classificator.stageDate),
                'dd.MM.yyyy'
              )})
            </span>
          )}
        </div>
      </div>
    </div>
  );
}