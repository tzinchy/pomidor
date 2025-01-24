import React, { useState, useEffect, useRef } from "react";
import { TableHead, TableBody } from "./Components";
import { HOSTLINK } from '../../index';

export default function Table({ filters, searchQuery }) {
  const headers = [
    "Район",
    "Адрес формируемой площадки",
    "Тип и срок",
    "Статус",
    "Отселяемые дома на площадке",
    "Тип и срок",
    "Статус",
    "Старт",
    "Ход работы"
  ];
  const [data, setData] = useState([]); // Все данные
  const [filteredData, setFilteredData] = useState([]); // Отфильтрованные данные
  const [displayData, setDisplayData] = useState([]); // Данные для отображения
  const [page, setPage] = useState(1); // Текущая страница
  const loaderRef = useRef(null); // Реф для отслеживания конца таблицы

  const itemsPerPage = 50; // Количество строк на страницу

  useEffect(() => { 
    fetch(`${HOSTLINK}/dashboard/table`)
      .then((res) => res.json())
      .then((fetchedData) => {
        setData(fetchedData);
        setFilteredData(fetchedData);
        setDisplayData(fetchedData.slice(0, itemsPerPage));
      });
  }, []);

  // Фильтрация данных
  useEffect(() => {
    if (data.length > 0) {
      const filterByQuery = (item) => 
        !searchQuery || item[3].toLowerCase().includes(searchQuery.toLowerCase());

      const filterByFilters = (item) => {
        const matchesFilter1 = filters['okrugs']?.length ? filters['okrugs'].includes(item[1]) : true;
        const matchesFilter2 = filters['districts']?.length ? filters['districts'].includes(item[2]) : true;
        const matchesFilter5 = filters['deviation']?.length ? filters['deviation'].includes(item[5]) : true;
        const matchesFilter6 = filters['otsel_type']?.length ? filters['otsel_type'].includes(item[6]) : true;
        const matchesFilter7 = filters['relocationAge']?.length ? filters['relocationAge'].includes(item[7]) : true;
        return matchesFilter1 && matchesFilter2 && matchesFilter5 && matchesFilter6 && matchesFilter7;
      };

      const filtered = data.filter((item) => filterByQuery(item) && filterByFilters(item));

      setFilteredData(filtered);
      setDisplayData(filtered.slice(0, itemsPerPage)); // Сброс отображаемых данных
      setPage(1); // Сбрасываем страницу
    }
  }, [filters, data, searchQuery]); // Добавляем зависимость от `searchQuery`

  const loadMoreData = () => {
    const startIndex = page * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;

    if (startIndex < filteredData.length) {
      const newData = filteredData.slice(startIndex, endIndex);
      setDisplayData((prev) => [...prev, ...newData]); // Добавляем новые данные
      setPage((prev) => prev + 1); // Увеличиваем страницу
    }
  };

  // Обработчик пересечения с "loader"
  const handleObserver = (entries) => {
    const target = entries[0];
    if (target.isIntersecting) {
      loadMoreData(); // Загружаем больше данных
    }
  };

  useEffect(() => {
    const observer = new IntersectionObserver(handleObserver, {
      root: null,
      rootMargin: "20px",
      threshold: 1.0,
    });
    if (loaderRef.current) observer.observe(loaderRef.current);
    return () => {
      if (loaderRef.current) observer.unobserve(loaderRef.current);
    };
  }, [filteredData, page]);

  if (!data || data.length === 0) {
    return <div>Загрузка данных...</div>;
  }

  return (
    <div className="relative flex h-[calc(100vh-3.5rem)] w-full">
      <div className="overflow-auto rounded-md border absolute left-0 h-full transition-all ease-in-out w-[calc(100%)]">
        <table className="text-sm caption-bottom w-full border-collapse bg-white">
          <TableHead headers={headers} />
          <TableBody data={displayData} /> {/* Передаём отображаемые данные */}
        </table>
        <div ref={loaderRef} className="loader text-center py-4"></div>
      </div>
    </div>
  );
}
