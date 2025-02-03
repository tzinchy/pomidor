import React from "react";

export default function ActionsCell(props){
    const value = props['props']
    console.log('ACTION ', value);
    return (
        <td className="p-2 font-normal ">
            <div className="flex w-full flex-row items-center justify-start gap-1">
                <div className="flex flex-1 justify-around">
                        <Button name='Скачать'/>
                        {value.status_id==1 ? (<Button name='Одобрено' isDisabled={true} />) : (<Button name='Одобрить' />)}
                        {value.status_id==1 ? value.is_downloaded ? <Button name={'Контейнер загружен'} isDisabled={true} /> : <Button name={'Загрузить контейнер'}/> : (<Button name={'Отменить'} />)}
                </div>
            </div>
        </td>
    )
}

function Button({ name, func=null, isDisabled }){
    return (
        <button className={`px-6 py-2 bg-gray-400 rounded text-white min-w-[150px] max-w-[150px] ${isDisabled ? 'opacity-50' : ''}`} disabled={isDisabled} onClick={func}>{name}</button>
    )
}