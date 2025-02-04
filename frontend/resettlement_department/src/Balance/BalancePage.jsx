import React, { useState } from "react";
import { DropdownProvider } from "./Components/DropdownContext";
import DropdownButton from "./Components/DropdownButton";
import SubmitButton from "./Components/SubmitButton";
import Aside from "../Navigation/Aside";
import Header from "./Components/Header";
import FileUploader from "./Components/FileUploader";

const ResponseDisplay = ({ data }) => {
  if (!data) return null;

  return (
    <div className="mt-4 p-4 bg-white rounded-xl shadow-xl w-1/2">
      <h3 className="text-lg font-semibold mb-4">Результаты подбора:</h3>
      <div className="space-y-3">
        {data.matches?.map((match, index) => (
          <div key={index} className="bg-gray-50 p-3 rounded-md">
            <div className="flex justify-between">
              <span className="font-medium">Совпадение {index + 1}:</span>
              <span className="bg-blue-100 text-blue-800 px-2 rounded">
                {match.match_percent}%
              </span>
            </div>
            <div className="mt-2 text-sm">
              <p>Семья: {match.family}</p>
              <p>Квартира: {match.apartment}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default function BalancePage() {
  const [responseData, setResponseData] = useState(null);
  const [error, setError] = useState(null);

  const handleResponse = (data, error) => {
    if (error) {
      setError(error);
      setResponseData(null);
    } else {
      setResponseData(data);
      setError(null);
    }
  };

  return (
    <div className="bg-muted/60 flex min-h-screen w-full flex-col">
      <Aside />
      <Header />
      <main className="relative flex flex-1 flex-col gap-2 p-2 sm:pl-16 bg-neutral-100 items-center">
        <DropdownProvider>
          <div className="p-4 justify-items-center bg-white w-2/3 h-[50vh] rounded-xl shadow-xl">
            <div className="flex justify-around w-full">
              <DropdownButton id="family_structure_house_address" type={'family_structure'} placeholder={'Старый дом'} />
              <DropdownButton id="new_apartment_house_address" type={'new_apartment'} placeholder={'Новый дом'} />
            </div>
            <div className="m-4 justify-items-center flex">
              <SubmitButton onResponse={handleResponse} type={''} />
              <SubmitButton onResponse={handleResponse} type={'last'} />
            </div>

            <FileUploader />
          </div>
        </DropdownProvider>

        {/* Отображение ошибок */}
        {error && (
          <div className="mt-4 p-4 bg-red-50 text-red-600 rounded-xl w-1/2">
            Ошибка: {error}
          </div>
        )}

        {/* Отображение результатов */}
        <ResponseDisplay data={responseData} />
      </main>
    </div>
  );
}



