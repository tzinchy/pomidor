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
              download_balance(history_id, is_wave, is_shadow);
              setShowDownloadOptions(false);
            }}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Баланс
          </button>
          <button
            onClick={() => {
              download_container(history_id);
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
