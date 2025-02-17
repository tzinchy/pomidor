import React, {useState} from "react";
import axios from "axios";
import { HOSTLINK } from "../../..";

export default function ActionsCell( {props, setData}) {
  const value = props;
  const [showDownloadOptions, setShowDownloadOptions] = useState(false);

  const paramsSerializer = {
    indexes: null,
    encode: (value) => encodeURIComponent(value)
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

  const download_balance = async (new_apartment_house_address, family_structure_house_address) => {
    const requestBody = { "new_apartment_house_address": new_apartment_house_address, "family_structure_house_address": family_structure_house_address };
    
    try {
      // Делаем запрос с responseType: 'arraybuffer' для скачивания файла
      const response = await fetch(`${HOSTLINK}/balance`, {
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

  const download_container = async (history_id) => {
    // Реализация скачивания контейнера аналогична download_balance
    try {
      const response = await fetch(`${HOSTLINK}/container/${history_id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          history_id
        }),
      });

      if (!response.ok) throw new Error('Network response was not ok');
      
      const arrayBuffer = await response.arrayBuffer();
      const blob = new Blob([arrayBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const url = URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = 'container.xlsx';
      link.click();
      URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error("Error", error);
    }
  };

  const DownloadModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-xl">
        <div className="flex items-center content-center">
          <h3 className="text-lg font-semibold mb-4 mr-4">Выберите тип скачивания</h3>
          <button
            onClick={() => setShowDownloadOptions(false)}
            className="mb-4 text-gray-500 hover:text-gray-700"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-x stroke-muted-foreground opacity-50 group-hover:opacity-100">
              <path d="M18 6 6 18"></path>
              <path d="m6 6 12 12"></path>
            </svg>
          </button>
        </div>
        <div className="flex justify-around">
          <button
            onClick={() => {
              download_balance(value.new_house_addresses, value.old_house_addresses);
              setShowDownloadOptions(false);
            }}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Баланс
          </button>
          <button
            onClick={() => {
              download_container(value.history_id);
              setShowDownloadOptions(false);
            }}
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
          >
            Контейнер
          </button>
        </div>
      </div>
    </div>
  );
  


  return (
    <td className="p-2 font-normal">
      <div className="flex w-full flex-row items-center justify-start gap-1">
        <div className="flex flex-1 justify-around">
          <Button
            name="Скачать"
            func={() => setShowDownloadOptions(true)}
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
      {showDownloadOptions && <DownloadModal />}
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
