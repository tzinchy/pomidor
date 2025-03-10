import React from "react";
import { useLocation } from "react-router-dom";

export default function Header(){
    return (
        <header className="flex justify-end bg-neutral-100">
            <HeaderNutton name={'Баланс'} link={'/balance'}/>
            <HeaderNutton name={'История подбора'} link={'/history'}/>
        </header>
    )
}

function HeaderNutton({name, link}){
    const location = useLocation();
    const isActive = location.pathname === `${link}`;

    return (
        <button className={`m-4 px-4 py-2 text-left border rounded-md shadow-sm flex justify-between items-center ${isActive ? 'bg-blue-500 text-white hover:bg-blue-600' : 'bg-white hover:bg-gray-50'}`}>
            <a href={link}>{name}</a>
        </button>
    )
}