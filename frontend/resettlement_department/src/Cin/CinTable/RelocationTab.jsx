import { useState, useEffect } from "react";
import AirDatepicker from 'air-datepicker';
import 'air-datepicker/air-datepicker.css';
import localeRu from 'air-datepicker/locale/ru';
import AddressDropdown from "./AddressDropdown";

export default function RelocationTab({ addresses, formData, setFormData }) {
  const [stages, setStages] = useState(() => {
    const initialStages = formData.relocation_stages || [
      {
        id: 1,
        inspection_date: '',
        relocation_date: '',
        houses: ['']
      }
    ];
    
    return initialStages.map(stage => ({
      ...stage,
      inspection_date: stage.inspection_date || '',
      relocation_date: stage.relocation_date || ''
    }));
  });

  const formatDateForDisplay = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}.${month}.${year}`;
  };

  const handleAddStage = () => {
    const newId = stages.length > 0 ? Math.max(...stages.map(s => s.id)) + 1 : 1;
    setStages([...stages, {
      id: newId,
      inspection_date: '',
      relocation_date: '',
      houses: ['']
    }]);
  };

  const handleRemoveStage = (stageId) => {
    if (stages.length <= 1) return;
    
    const newStages = stages
      .filter(stage => stage.id !== stageId)
      .map((stage, index) => ({
        ...stage,
        id: index + 1
      }));
    
    setStages(newStages);
  };

  const handleAddHouse = (stageId) => {
    setStages(stages.map(stage => 
      stage.id === stageId 
        ? { ...stage, houses: [...stage.houses, ''] } 
        : stage
    ));
  };

  const handleRemoveHouse = (stageId, houseIndex) => {
    setStages(stages.map(stage => 
      stage.id === stageId 
        ? { 
            ...stage, 
            houses: stage.houses.filter((_, index) => index !== houseIndex) 
          } 
        : stage
    ));
  };

  const handleDateChange = (stageId, field, date) => {
    const localDate = new Date(date);
    const year = localDate.getFullYear();
    const month = String(localDate.getMonth() + 1).padStart(2, '0');
    const day = String(localDate.getDate()).padStart(2, '0');
    const dateString = `${year}-${month}-${day}`;

    setStages(stages.map(stage => 
      stage.id === stageId 
        ? { ...stage, [field]: dateString } 
        : stage
    ));
  };

  const handleHouseChange = (stageId, houseIndex, value) => {
    setStages(stages.map(stage => 
      stage.id === stageId 
        ? { 
            ...stage, 
            houses: stage.houses.map((house, index) => 
              index === houseIndex ? value : house
            ) 
          } 
        : stage
    ));
  };

  useEffect(() => {
    const pickers = [];
    
    stages.forEach((stage, index) => {
      const inspectionInput = document.getElementById(`inspection-date-${stage.id}-${index}`);
      const relocationInput = document.getElementById(`relocation-date-${stage.id}-${index}`);
      
      if (inspectionInput) {
        const inspectionPicker = new AirDatepicker(inspectionInput, {
          locale: localeRu,
          dateFormat: 'dd.MM.yyyy',
          selectedDates: stage.inspection_date 
            ? [new Date(stage.inspection_date)] 
            : [],
          onSelect: ({ date }) => {
            handleDateChange(stage.id, 'inspection_date', date);
          }
        });
        pickers.push(inspectionPicker);
      }
      
      if (relocationInput) {
        const relocationPicker = new AirDatepicker(relocationInput, {
          locale: localeRu,
          dateFormat: 'dd.MM.yyyy',
          selectedDates: stage.relocation_date 
            ? [new Date(stage.relocation_date)] 
            : [],
          onSelect: ({ date }) => {
            handleDateChange(stage.id, 'relocation_date', date);
          }
        });
        pickers.push(relocationPicker);
      }
    });

    return () => {
      pickers.forEach(picker => picker && picker.destroy());
    };
  }, [stages]);

  useEffect(() => {
    setFormData(prev => ({
      ...prev,
      relocation_stages: stages.map(stage => ({
        ...stage,
        inspection_date: stage.inspection_date || null,
        relocation_date: stage.relocation_date || null
      }))
    }));
  }, [stages, setFormData]);

  return (
    <div className="space-y-6">
      {stages.map((stage, stageIndex) => (
        <div key={`stage-${stage.id}-${stageIndex}`} className="border border-gray-200 rounded-lg p-4">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-medium">Этап {stage.id}</h3>
            {stages.length > 1 && (
              <button
                onClick={() => handleRemoveStage(stage.id)}
                className="text-red-500 hover:text-red-700"
              >
                Удалить этап
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Дата выдачи смотрового
              </label>
              <input
                id={`inspection-date-${stage.id}-${stageIndex}`}
                type="text"
                value={stage.inspection_date ? formatDateForDisplay(stage.inspection_date) : ''}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                readOnly
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Дата начала отселения
              </label>
              <input
                id={`relocation-date-${stage.id}-${stageIndex}`}
                type="text"
                value={stage.relocation_date ? formatDateForDisplay(stage.relocation_date) : ''}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                readOnly
              />
            </div>
          </div>

          <div className="space-y-3">
            <label className="block text-sm font-medium text-gray-700">
              Отселяемые дома
            </label>
            
            {stage.houses.map((house, houseIndex) => (
              <div key={`house-${stage.id}-${houseIndex}`} className="flex items-center gap-2">
                <div className="w-full">
                    <AddressDropdown
                        addresses={addresses}
                        value={house}
                        onChange={(value) => handleHouseChange(stage.id, houseIndex, value)}
                        placeholder="Выберите адрес дома"
                        className="flex-1"
                        />
                </div>
                {stage.houses.length > 1 && (
                  <button
                    onClick={() => handleRemoveHouse(stage.id, houseIndex)}
                    className="text-red-500 hover:text-red-700"
                  >
                    ×
                  </button>
                )}
              </div>
            ))}

            <button
              onClick={() => handleAddHouse(stage.id)}
              className="mt-2 text-blue-500 hover:text-blue-700 text-sm flex items-center"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Добавить дом
            </button>
          </div>
        </div>
      ))}

      <button
        onClick={handleAddStage}
        className="mt-4 px-4 py-2 bg-blue-50 text-blue-600 rounded-md hover:bg-blue-100 flex items-center"
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
        Добавить этап отселения
      </button>
      <button onClick={() => {console.log('stages', stages)}} className="bg-blue-300">
        Log
      </button>
    </div>
  );
}