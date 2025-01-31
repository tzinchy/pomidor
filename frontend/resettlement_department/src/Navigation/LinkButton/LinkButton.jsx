import React, { useState } from "react";
import { createPortal } from "react-dom";
import { useLocation } from "react-router-dom";
import {NavSvg, NavPng} from './NavSvg'
import { ASIDELINK } from "../..";


export default function LinkButton({ name }) {
    const location = useLocation();
    const isActive = location.pathname === `/${name}`;
    const [tooltip, setTooltip] = useState({ visible: false, x: 0, y: 0 });
    const [timeoutId, setTimeoutId] = useState(null);

    const handleMouseEnter = (e) => {
        const rect = e.currentTarget.getBoundingClientRect();
        const id = setTimeout(() => {
        setTooltip({
            visible: true,
            x: rect.right + 10, // Смещение подсказки справа
            y: rect.top + rect.height / 5.5, // Центрирование по высоте
        });
        }, 500); // Задержка в 0.5 секунды
        setTimeoutId(id);
    };

    const handleMouseLeave = () => {
        clearTimeout(timeoutId); // Отменяем показ, если курсор ушел до завершения задержки
        setTooltip((prev) => ({ ...prev, visible: false })); // Скрытие подсказки
    };

    return (
        <div
        className="relative group"
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        >
        <a
            href={`${ASIDELINK}/${name}`}
            className={`items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ${
            isActive ? "text-gray-400" : "text-black"
            } h-10 flex p-0`}
        >
            <button
            className="items-center justify-center whitespace-nowrap rounded-md text-sm font-medium h-10 flex p-0"
            data-state="closed"
            >
                <NavPng state={name} />
            </button>
        </a>
        <Tooltip x={tooltip.x} y={tooltip.y} visible={tooltip.visible}>
            <TooltipDesc name={name} />
        </Tooltip>
        </div>
    );
}

function Tooltip({ children, x, y, visible }) {
    return createPortal(
        <div
        style={{
            position: "absolute",
            top: y,
            left: x,
            zIndex: 1050,
            backgroundColor: "white", // Белый фон
            color: "black", // Черный текст
            padding: "5px 10px", // Увеличенный отступ
            borderRadius: "5px", // Больше скругление углов
            fontSize: "14px", // Увеличенный размер шрифта
            whiteSpace: "nowrap",
            boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)", // Добавлена легкая тень
            pointerEvents: "none",
            opacity: visible ? 1 : 0, // Прозрачность
            transition: "opacity 0.2s ease", // Анимация плавного появления
        }}
        >
        {children}
        </div>,
        document.body
    );
}

function TooltipDesc({ name }){
    const descriptions = {
        'table_page': 'Площадки',
        'dashboard': 'Дашборд',
        'aparts': 'Ресурс / Отселяемые дома'
    } 

    return descriptions[name]
}
