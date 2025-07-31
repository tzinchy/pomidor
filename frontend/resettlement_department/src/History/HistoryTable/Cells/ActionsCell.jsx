import React, {useState} from "react";
import api from "../../../api";
import { approveAvailable, HOSTLINK } from "../../..";


export default function ActionsCell( {  history_id,
  status_id,
  is_downloaded,
  is_wave,
  is_shadow,
  setData, 
  setShowConfirmContainerUpload,
  setShowConfirmHistoryDelete,
  setShowConfirmApprove, 
  setHistoryId,
  loadingHistoryId}) {
  // const value = props;
  const [showDownloadOptions, setShowDownloadOptions] = useState(false);


  // const paramsSerializer = {
  //   indexes: null,
  //   encode: (value) => encodeURIComponent(value)
  // };





  const download_balance = async (history_id, is_wave, is_shadow) => {
    const requestBody = { "history_id": parseInt(history_id), "is_wave": is_wave, "is_shadow": is_shadow};
    console.log('requestBody', requestBody);
    
    try {
      // Делаем запрос с responseType: 'arraybuffer' для скачивания файла
      const response = await fetch(`${HOSTLINK}/balance`, {
        method: 'POST',
        credentials: 'include',
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
        credentials: 'include',
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
  <div className="fixed inset-0 z-[99999] backdrop-blur-sm flex items-center justify-center animate-fadeIn">
    <div className="relative bg-white/30 backdrop-blur-lg border border-white/40 bg-white/90 ring-1 ring-white/10 
                    shadow-2xl rounded-2xl px-6 py-6 w-[340px] max-w-full transition text-center">

      {/* Крестик в правом верхнем углу */}
      <button
        onClick={() => setShowDownloadOptions(false)}
        className="absolute top-3 right-3 text-gray-500 hover:text-red-600 transition"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
             fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
             className="lucide lucide-x stroke-muted-foreground opacity-60 hover:opacity-100 transition">
          <path d="M18 6 6 18"></path>
          <path d="m6 6 12 12"></path>
        </svg>
      </button>

      {/* Заголовок по центру */}
      <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-6 mt-2">
        Выберите тип скачивания
      </h3>

      {/* Кнопки */}
      <div className="flex justify-center gap-4">
        <button
          onClick={() => {
            download_balance(history_id, is_wave, is_shadow);
            setShowDownloadOptions(false);
          }}
          className="flex-1 py-2 text-sm font-medium bg-blue-500 text-white rounded-md hover:bg-blue-600 transition"
        >
          Баланс
        </button>
        <button
          onClick={() => {
            download_container(history_id);
            setShowDownloadOptions(false);
          }}
          className="flex-1 py-2 text-sm font-medium bg-green-500 text-white rounded-md hover:bg-green-600 transition"
        >
          Контейнер
        </button>
      </div>
    </div>
  </div>
);
  


  return (
    <td className="p-2 font-normal">

        <div className="flex flex-1 justify-around">
          <Button
            name="Скачать"
            func={() => setShowDownloadOptions(true)}
          />
          {status_id === 1 ? (
            <Button name="Одобрено" isDisabled={true} />
          ) : !approveAvailable ? (
            <Button name="Ждет одобрения" isDisabled={true} />
          ) : (
            <Button 
            name={loadingHistoryId === history_id ? "Загрузка..." : "Одобрить"}
            isDisabled={loadingHistoryId === history_id} 
            func={() => {setShowConfirmApprove(true); setHistoryId(history_id)}} />
          )}
          {status_id === 1 ? (
            is_downloaded ? (
              <Button name="Контейнер загружен" isDisabled={true} />
            ) : (
            <Button
              name={loadingHistoryId === history_id ? "Загрузка..." : "Загрузить контейнер"}
              isDisabled={loadingHistoryId === history_id}
              func={() => {
                setShowConfirmContainerUpload(true);
                setHistoryId(history_id);
              }}
            />
            )
          ) : (
            <Button 
            name={loadingHistoryId === history_id ? "Загрузка..." : "Отменить"}
            isDisabled={loadingHistoryId === history_id}
            func={() => {setShowConfirmHistoryDelete(true); setHistoryId(history_id) }}/>
          )}
        </div>
      {showDownloadOptions && <DownloadModal />}
    </td>
  );
}

function Button({ name, func = null, isDisabled = false }) {
  const isSuccessState = name === "Одобрено" || name === "Контейнер загружен";
  const finalDisabled = isDisabled || isSuccessState;

  const baseStyle = `
    min-w-[120px] max-w-[120px] px-4 py-2 rounded-md text-sm font-medium
    flex justify-center items-center text-center transition-all
    shadow-md hover:shadow-lg active:shadow-none
    focus:outline-none focus:ring-2 focus:ring-offset-1 dark:focus:ring-offset-gray-900
  `;

  const successStyle = `
    bg-green-50 text-green-900
    cursor-not-allowed opacity-70
    focus:ring-green-300
  `;

  const disabledStyle = `
    bg-gray-300 text-white opacity-60 cursor-not-allowed
    focus:ring-gray-300
  `;

  const activeStyle = `
    bg-gradient-to-r from-blue-300 to-blue-400 text-white
    hover:from-blue-500 hover:to-blue-600 active:scale-95
    focus:ring-blue-300
  `;

  return (
    <button
      onClick={func}
      disabled={finalDisabled}
      className={`
        ${baseStyle}
        ${isSuccessState ? successStyle : finalDisabled ? disabledStyle : activeStyle}
      `}
    >
      {name}
    </button>
  );
}
