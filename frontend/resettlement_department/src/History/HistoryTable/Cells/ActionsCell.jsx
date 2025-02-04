import React from "react";
import axios from "axios";
import { HOSTLINK } from "../../..";

export default function ActionsCell( {props, setData}) {
  const value = props;

  const paramsSerializer = {
    indexes: null,
    encode: (value) => encodeURIComponent(value)
  };

  const download_balance = async (new_apartment_house_address, family_structure_house_address) => {
    const requestBody = { "new_apartment_house_address": new_apartment_house_address, "family_structure_house_address": family_structure_house_address };
    
    try {
      // Делаем запрос с responseType: 'arraybuffer' для скачивания файла
      const response = await fetch('/balance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      // Проверяем, что статус запроса успешен
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      // Получаем данные как ArrayBuffer
      const arrayBuffer = await response.arrayBuffer();

      // Создаем новый Blob с типом данных
      const blob = new Blob([arrayBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      
      // Создаем URL для Blob
      const url = URL.createObjectURL(blob);

      // Создаем ссылку для скачивания
      const link = document.createElement('a');
      link.href = url;
      link.download = 'balance.xlsx'; // Имя файла для скачивания

      // Симулируем клик по ссылке, чтобы начать скачивание
      link.click();

      // Освобождаем URL после использования
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error", error);
    }
  };



  const delete_history = async (history_id) => {
    try {
      const response = await axios.delete(
        `${HOSTLINK}/delete/${history_id}`,
        {
          params: { history_id: history_id },
          paramsSerializer,
        }
      );

      // Если запрос на удаление прошел успешно, обновляем данные
      if (response.status === 200) {
        // Обновляем локальные данные, убирая удаленную строку
        setData(prevData => prevData.filter(item => item.history_id !== history_id));
      }
    } catch (error) {
      console.error("Error:", error.response?.data);
    }
  };


  const approve_history = async (history_id) => {
    try {
      const response = await axios.patch(
        `${HOSTLINK}/approve/${history_id}`,
        {
          params: { history_id: history_id },
          paramsSerializer,
        }
      );
  
      // Если запрос прошел успешно, обновляем данные
      if (response.status === 200) {
        // Обновляем локальные данные, изменяя status_id для выбранного history_id
        setData(prevData => 
          prevData.map(item => 
            item.history_id === history_id ? { ...item, status_id: 1 } : item
          )
        );
      }
    } catch (error) {
      console.error("Error:", error.response?.data);
    }
  };
  


  return (
    <td className="p-2 font-normal">
      <div className="flex w-full flex-row items-center justify-start gap-1">
        <div className="flex flex-1 justify-around">
          <Button
            name="Скачать"
            func={() => download_balance(value.new_house_addresses, value.old_house_addresses)}
          />
          {value.status_id === 1 ? (
            <Button name="Одобрено" isDisabled={true} />
          ) : (
            <Button name="Одобрить" func={() => approve_history(value.history_id)} />
          )}
          {value.status_id === 1 ? (
            value.is_downloaded ? (
              <Button name="Контейнер загружен" isDisabled={true} />
            ) : (
              <Button name="Загрузить контейнер" />
            )
          ) : (
            <Button name="Отменить" func={() => delete_history(value.history_id) }/>
          )}
        </div>
      </div>
    </td>
  );
}

function Button({ name, func = null, isDisabled }) {
  return (
    <button
      className={`px-6 py-2 bg-gray-400 rounded text-white min-w-[150px] max-w-[150px] ${isDisabled ? 'opacity-50' : ''}`}
      disabled={isDisabled}
      onClick={func}
    >
      {name}
    </button>
  );
}
