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
        inspection_date: null,
        relocation_date: null,
        ranges: [{
          date_range: null,
          time_from: '',
          time_to: ''
        }],
        houses: []
      }
    ];
    
    return initialStages.reduce((acc, stage) => {
      const { id, ...rest } = stage;
      acc[id] = rest;
      return acc;
    }, {});
  });

  const stagesArray = Object.entries(stages).map(([id, data]) => ({
    id: Number(id),
    ...data
  }));

  const formatDateForDisplay = (dateString) => {
    if (!dateString) return '';
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return '';
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = date.getFullYear();
      return `${day}.${month}.${year}`;
    } catch {
      return '';
    }
  };

  const formatRangeForDisplay = (range) => {
    if (!range) return '';
    try {
      const [start, end] = range.split('_');
      return `${formatDateForDisplay(start)} - ${formatDateForDisplay(end)}`;
    } catch {
      return '';
    }
  };

  const handleAddStage = () => {
    const newId = Object.keys(stages).length > 0 
      ? Math.max(...Object.keys(stages).map(Number)) + 1 
      : 1;
    
    setStages(prev => ({
      ...prev,
      [newId]: {
        inspection_date: null,
        relocation_date: null,
        ranges: stages.id === 1 ? [{
          date_range: null,
          time_from: '',
          time_to: ''
        }] : [],
        houses: ['']
      }
    }));
  };

  const handleRemoveStage = (stageId) => {
    if (Object.keys(stages).length <= 1) return;
    
    const newStages = { ...stages };
    delete newStages[stageId];
    
    const renumberedStages = Object.entries(newStages).reduce((acc, [_, stage], index) => {
      const newId = index + 1;
      acc[newId] = stage;
      return acc;
    }, {});
    
    setStages(renumberedStages);
  };

  const handleAddHouse = (stageId) => {
    setStages(prev => ({
      ...prev,
      [stageId]: {
        ...prev[stageId],
        houses: [...prev[stageId].houses, '']
      }
    }));
  };

  const handleRemoveHouse = (stageId, houseIndex) => {
    setStages(prev => ({
      ...prev,
      [stageId]: {
        ...prev[stageId],
        houses: prev[stageId].houses.filter((_, index) => index !== houseIndex)
      }
    }));
  };

  const handleAddRange = (stageId) => {
    setStages(prev => ({
      ...prev,
      [stageId]: {
        ...prev[stageId],
        ranges: [...prev[stageId].ranges, {
          date_range: null,
          time_from: '',
          time_to: ''
        }]
      }
    }));
  };

  const handleRemoveRange = (stageId, rangeIndex) => {
    setStages(prev => ({
      ...prev,
      [stageId]: {
        ...prev[stageId],
        ranges: prev[stageId].ranges.filter((_, index) => index !== rangeIndex)
      }
    }));
  };

  const handleDateChange = (stageId, field, date) => {
    if (!date) return;
    
    try {
      const localDate = new Date(date);
      if (isNaN(localDate.getTime())) return;
      
      const year = localDate.getFullYear();
      const month = String(localDate.getMonth() + 1).padStart(2, '0');
      const day = String(localDate.getDate()).padStart(2, '0');
      const dateString = `${year}-${month}-${day}`;

      setStages(prev => ({
        ...prev,
        [stageId]: {
          ...prev[stageId],
          [field]: dateString
        }
      }));
    } catch (error) {
      console.error('Error handling date change:', error);
    }
  };

  const handleRangeChange = (stageId, rangeIndex, dates) => {
    if (!dates || dates.length !== 2) return;
    
    try {
      const [start, end] = dates;
      if (isNaN(start.getTime()) || isNaN(end.getTime())) return;
      
      const formatDate = (date) => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
      };
      
      const rangeString = `${formatDate(start)}_${formatDate(end)}`;

      setStages(prev => {
        const newRanges = [...prev[stageId].ranges];
        newRanges[rangeIndex].date_range = rangeString;
        
        return {
          ...prev,
          [stageId]: {
            ...prev[stageId],
            ranges: newRanges
          }
        };
      });
    } catch (error) {
      console.error('Error handling range change:', error);
    }
  };

  const handleTimeChange = (stageId, rangeIndex, field, value) => {
    setStages(prev => {
      const newRanges = [...prev[stageId].ranges];
      newRanges[rangeIndex][field] = value;
      
      return {
        ...prev,
        [stageId]: {
          ...prev[stageId],
          ranges: newRanges
        }
      };
    });
  };

  const handleHouseChange = (stageId, houseIndex, value) => {
    setStages(prev => ({
      ...prev,
      [stageId]: {
        ...prev[stageId],
        houses: prev[stageId].houses.map((house, index) => 
          index === houseIndex ? value : house
        )
      }
    }));
  };

  useEffect(() => {
    const pickers = [];
    
    stagesArray.forEach((stage, stageIndex) => {
      const inspectionInput = document.getElementById(`inspection-date-${stage.id}-${stageIndex}`);
      const relocationInput = document.getElementById(`relocation-date-${stage.id}-${stageIndex}`);
      
      if (inspectionInput) {
        const inspectionPicker = new AirDatepicker(inspectionInput, {
          locale: localeRu,
          dateFormat: 'dd.MM.yyyy',
          selectedDates: stage.inspection_date && !isNaN(new Date(stage.inspection_date).getTime())
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
          selectedDates: stage.relocation_date && !isNaN(new Date(stage.relocation_date).getTime())
            ? [new Date(stage.relocation_date)] 
            : [],
          onSelect: ({ date }) => {
            handleDateChange(stage.id, 'relocation_date', date);
          }
        });
        pickers.push(relocationPicker);
      }

      // Инициализация datepicker'ов для периодов отселения (только для первого этапа)
      if (stage.id === 1) {
        stage.ranges.forEach((_, rangeIndex) => {
          const rangeInput = document.getElementById(`date-range-${stage.id}-${rangeIndex}-${stageIndex}`);
          if (rangeInput) {
            const rangePicker = new AirDatepicker(rangeInput, {
              locale: localeRu,
              range: true,
              dateFormat: 'dd.MM.yyyy',
              selectedDates: stage.ranges[rangeIndex].date_range 
                ? stage.ranges[rangeIndex].date_range.split('_').map(d => new Date(d)).filter(d => !isNaN(d.getTime()))
                : [],
              onSelect: ({ date }) => {
                handleRangeChange(stage.id, rangeIndex, date);
              }
            });
            pickers.push(rangePicker);
          }
        });
      }
    });

    return () => {
      pickers.forEach(picker => picker && picker.destroy());
    };
  }, [stagesArray]);

  useEffect(() => {
    const stagesForSave = Object.entries(stages).map(([id, data]) => ({
      id: Number(id),
      ...data
    }));
    
    setFormData(prev => ({
      ...prev,
      relocation_stages: stagesForSave
    }));
  }, [stages, setFormData]);

  return (
    <div className="space-y-6">
      {stagesArray.map((stage, stageIndex) => (
        <div key={`stage-${stage.id}-${stageIndex}`} className="border border-gray-200 rounded-lg p-4">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-medium">Этап {stage.id}</h3>
            {stagesArray.length > 1 && (
              <button
                onClick={() => handleRemoveStage(stage.id)}
                className="text-red-500 hover:text-red-700"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
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
                value={formatDateForDisplay(stage.inspection_date)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                readOnly
                placeholder="Выберите дату"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Дата начала отселения
              </label>
              <input
                id={`relocation-date-${stage.id}-${stageIndex}`}
                type="text"
                value={formatDateForDisplay(stage.relocation_date)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                readOnly
                placeholder="Выберите дату"
              />
            </div>
          </div>

          {/* График работы только для первого этапа */}
          {stage.id === 1 && (
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">
                График работы
              </label>
              
              {stage.ranges.map((range, rangeIndex) => (
                <div key={`range-${stage.id}-${rangeIndex}`} className="flex items-center">
                  <div className="flex items-center gap-2 w-1/2">
                    <div className="flex-1">
                      <input
                        id={`date-range-${stage.id}-${rangeIndex}-${stageIndex}`}
                        type="text"
                        value={formatRangeForDisplay(range.date_range)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        readOnly
                        placeholder="Выберите период"
                      />
                    </div>
                  </div>

                  <div className="flex items-center gap-2 w-1/2">
                    <div className="flex-1 flex items-center gap-2">
                      <label className="text-sm font-medium text-gray-700 ml-2">с</label>
                      <input
                        type="time"
                        value={range.time_from}
                        onChange={(e) => handleTimeChange(stage.id, rangeIndex, 'time_from', e.target.value)}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      />
                      <label className="text-sm font-medium text-gray-700">до</label>
                      <input
                        type="time"
                        value={range.time_to}
                        onChange={(e) => handleTimeChange(stage.id, rangeIndex, 'time_to', e.target.value)}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                  </div>
                  {stage.ranges.length > 1 && (
                    <button
                      onClick={() => handleRemoveRange(stage.id, rangeIndex)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  )}
                </div>
              ))}

              <button
                onClick={() => handleAddRange(stage.id)}
                className="text-blue-500 hover:text-blue-700 text-sm flex items-center"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Добавить период отселения
              </button>
            </div>
          )}

          <div className="space-y-3 mt-4">
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
                    placeholder="Выберите адрес отселяемого дома"
                    className="flex-1"
                  />
                </div>
                {stage.houses.length > 1 && (
                  <button
                    onClick={() => handleRemoveHouse(stage.id, houseIndex)}
                    className="text-red-500 hover:text-red-700"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
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
      <button
        onClick={() => {console.log(stages)}}
        className="mt-4 px-4 py-2 bg-blue-50 text-blue-600 rounded-md hover:bg-blue-100 flex items-center"
      >
        LOG
      </button>
    </div>
  );
}