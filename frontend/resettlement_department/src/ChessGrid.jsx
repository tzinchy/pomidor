import React from 'react';

const data = [
    { id: '1', floor: 1, number: '1', status: 'free', section: 1 },
    { id: '2', floor: 1, number: '2', status: 'sold', section: 1 },
    { id: '3', floor: 1, number: '3', status: 'free', section: 1 },
    { id: '4', floor: 2, number: '5', status: 'reserved', section: 1 },
    { id: '5', floor: 3, number: '8', status: 'free', section: 1 },
    { id: '6', floor: 4, number: '12', status: 'sold', section: 1 },
    { id: '7', floor: 5, number: '14', status: 'free', section: 1 },
];

const statusColors = {
  free: 'bg-green-300',
  sold: 'bg-red-300',
  reserved: 'bg-yellow-300',
};

export default function ChessGrid() {
  // Сортируем данные по этажам и номерам квартир
  const sortedData = [...data].sort((a, b) => a.floor - b.floor || parseInt(a.number) - parseInt(b.number));
  
  // Группируем квартиры по этажам
  const floors = [...new Set(data.map(flat => flat.floor))].sort((a, b) => b - a);
  
  let lastFlatNumber = 0; // Начинаем с 0, так как первый этаж начинается с 1
  const flatsByFloor = floors.map(floor => {
    const floorFlats = sortedData
      .filter(flat => flat.floor === floor)
      .sort((a, b) => parseInt(a.number) - parseInt(b.number));
    
    const resultFlats = [];
    let currentNumber = lastFlatNumber + 1; // Начинаем со следующего после последнего номера
    
    floorFlats.forEach(flat => {
      const flatNumber = parseInt(flat.number);
      
      // Добавляем пустые ячейки до текущей квартиры
      while (currentNumber < flatNumber) {
        resultFlats.push(null);
        currentNumber++;
      }
      
      // Добавляем текущую квартиру
      resultFlats.push(flat);
      currentNumber++;
    });
    
    // Обновляем последний номер квартиры для следующего этажа
    if (floorFlats.length > 0) {
      lastFlatNumber = parseInt(floorFlats[floorFlats.length - 1].number);
    } else {
      lastFlatNumber = currentNumber - 1;
    }
    
    return {
      floor,
      flats: resultFlats
    };
  });

  // Получаем номер секции
  const section = data[0]?.section || 1;

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-2">Секция {section}</h2>
      <div className="grid gap-2">
        {flatsByFloor.map(({ floor, flats }) => (
          <div key={floor} className="flex gap-2 items-center">
            <div className="w-10 text-right font-medium">{floor} этаж</div>
            {flats.map((flat, index) => (
              flat ? (
                <div
                  key={flat.id}
                  className={`w-16 h-16 rounded shadow flex items-center justify-center font-bold text-sm ${statusColors[flat.status]}`}
                  title={`Квартира ${flat.number}, статус: ${flat.status}`}
                >
                  {flat.number}
                </div>
              ) : (
                <div
                  key={`empty-${floor}-${index}`}
                  className="w-16 h-16 rounded shadow flex items-center justify-center font-bold text-sm bg-gray-100 opacity-50"
                >
                  {index + 1}
                </div>
              )
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}