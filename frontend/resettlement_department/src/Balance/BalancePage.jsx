import React, { useState } from "react";
import { DropdownProvider } from "./Components/DropdownContext";
import DropdownButton from "./Components/DropdownButton";
import SubmitButton from "./Components/SubmitButton";
import Aside from "../Navigation/Aside";
import Header from "./Components/Header";
import FileUploader from "./Components/FileUploader";
import TestBtn from "./Components/TestBtn";
import RemoveStageButton from "./Components/RemoveStageButton";

const ResponseDisplay = ({ data }) => {
  if (!data) return null;

  return (
    <div className="mt-4 p-4 bg-white rounded-xl shadow-xl w-1/2">
      <h3 className="text-lg font-semibold mb-4">Результаты подбора:</h3>
      <div className="space-y-3">
        Подобрано - {data.offer} кв., Не подобрано - {data.cannot_offer} кв.
      </div>
    </div>
  );
};

export default function BalancePage() {
  const [responseData, setResponseData] = useState(null);
  const [error, setError] = useState(null);
  const [stages, setStages] = useState([{ id: 1 }]);
  const [isShadow, setIsShadow] = useState(false); // Состояние для чек-бокса

  const handleResponse = (data, error) => {
    if (error) {
      setError(error);
      setResponseData(null);
    } else {
      setResponseData(data);
      setError(null);
    }
  };

  const addStage = () => {
    const newId = stages.length > 0 ? Math.max(...stages.map(stage => stage.id)) + 1 : 1;
    setStages([...stages, { id: newId }]);
  };

  const removeStage = (id) => {
    if (stages.length > 1) {
      setStages(prev => {
        const newStages = prev.filter(stage => stage.id !== id);
        return newStages.map((stage, index) => ({ ...stage, id: index + 1 }));
      });
    }
  };

  return (
    <div className="bg-muted/60 flex min-h-screen w-full flex-col">
      <Aside />
      <Header />
      <main className="relative flex flex-1 flex-col gap-2 p-2 sm:pl-16 bg-neutral-100 items-center">
        <DropdownProvider>
          <div className="p-4 justify-items-center bg-white w-2/3 min-h-[60vh] rounded-xl shadow-xl">
            {stages.map((stage, index) => (
              <div key={stage.id} className="mb-4 w-full">
                <div className="flex justify-around w-full">
                  <DropdownButton 
                    id={`old_apartment_house_address_${stage.id}`} 
                    type={'old_apartment'} 
                    placeholder={'Старый дом'} 
                  />
                  <DropdownButton 
                    id={`new_apartment_house_address_${stage.id}`} 
                    type={'new_apartment'} 
                    placeholder={'Новый дом'} 
                  />
                  {stages.length > 1 && (
                    <RemoveStageButton 
                      stageId={stage.id} 
                      onRemove={removeStage} 
                    />
                  )}
                </div>
                {index === stages.length - 1 && (
                  <div className="flex justify-center mt-2">
                    <button 
                      onClick={addStage}
                      className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                      Добавить этап
                    </button>
                  </div>
                )}
              </div>
            ))}

            <div className="m-4 justify-items-center flex">
              <SubmitButton onResponse={handleResponse} type={''} isShadow={isShadow} />
              <SubmitButton onResponse={handleResponse} type={'last'} isShadow={isShadow} />
            </div>
            {/* Чек-бокс "теневой подбор" */}
            <div className="mb-2 flex items-center">
              <input
                type="checkbox"
                id="shadowCheckbox"
                checked={isShadow}
                onChange={() => setIsShadow(!isShadow)}
                className="mr-2"
              />
              <label htmlFor="shadowCheckbox">Теневой подбор</label>
            </div>
            <FileUploader link={`/fisrt_matching/upload-file/`}/>
          </div>
        </DropdownProvider>

        {error && (
          <div className="mt-4 p-4 bg-red-50 text-red-600 rounded-xl w-1/2">
            Ошибка: {error}
          </div>
        )}

        <ResponseDisplay data={responseData} />
      </main>
    </div>
  );
}