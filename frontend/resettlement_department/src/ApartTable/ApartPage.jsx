import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import LeftBar from "./LeftBar";
import Aside from "../Navigation/Aside";
import ApartTable from "./ApartTable";

export default function ApartPage() {

  // 1) Локальные состояния
  const [apartType, setApartType] = useState("FamilyStructure");
  const [collapsed, setCollapsed] = useState(false);
  const handleToggleSidebar = () => {
    setCollapsed(!collapsed);
  };

  // Данные для дерева
  const [districts, setDistricts] = useState([]);
  const [municipalDistricts, setMunicipalDistricts] = useState({});
  const [houseAddresses, setHouseAddresses] = useState({});

  // Данные для таблицы и деталей
  const [apartments, setApartments] = useState([]);
  const [apartmentDetails, setApartmentDetails] = useState(null);

  // Кто раскрыт в дереве (ключ = district/municipal, значение = true/false)
  const [expandedNodes, setExpandedNodes] = useState({});

  // Поиск по ID
  const [searchTerm, setSearchTerm] = useState("");

  // Ссылка на панель деталей (чтобы закрывать при клике вне)
  const detailsRef = useRef(null);

  // 2) Эффекты
  // При смене типа сбрасываем дерево и грузим районы
  useEffect(() => {
    resetFilters();
    fetchDistricts();
  }, [apartType]);

  // Закрытие панели деталей при клике вне
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (detailsRef.current && !detailsRef.current.contains(e.target)) {
        setApartmentDetails(null);
      }
    };
    window.addEventListener("click", handleClickOutside);
    return () => window.removeEventListener("click", handleClickOutside);
  }, []);

  // 3) Методы
  const resetFilters = () => {
    setExpandedNodes({});
    setMunicipalDistricts({});
    setHouseAddresses({});
    setApartments([]);
    setApartmentDetails(null);
    setSearchTerm("");
  };

  const fetchDistricts = async () => {
    try {
      const response = await axios.get(`/tables/district?apart_type=${apartType}`);
      setDistricts(response.data);
    } catch (error) {
      console.error("Error fetching districts:", error);
    }
  };

  const fetchMunicipalDistricts = async (district) => {
    try {
      const response = await axios.get(
        `/tables/municipal_district?apart_type=${apartType}&municipal_district=${district}`
      );
      setMunicipalDistricts((prev) => ({ ...prev, [district]: response.data }));
    } catch (error) {
      console.error("Error fetching municipal districts:", error);
    }
  };

  const fetchHouseAddresses = async (municipal) => {
    try {
      const response = await axios.get(
        `/tables/house_addresses?apart_type=${apartType}&areas=${municipal}`
      );
      setHouseAddresses((prev) => ({ ...prev, [municipal]: response.data }));
    } catch (error) {
      console.error("Error fetching house addresses:", error);
    }
  };

  const fetchApartments = async (addresses) => {
    try {
      const response = await axios.get(
        `/tables/apartments?apart_type=${apartType}&house_addresses=${addresses.join(",")}`
      );
      setApartments(response.data);
    } catch (error) {
      console.error("Error fetching apartments:", error);
    }
  };


  const fetchApartmentDetails = async (apartmentId) => {
    try {
      const response = await axios.get(
        `/tables/apartment/${apartmentId}?apart_type=${apartType}`
      );
      setApartmentDetails(response.data);
      console.log(response.data);
    } catch (error) {
      console.error("Error fetching apartment details:", error);
    }
  };



  // 4) Фильтрация квартир по ID (new_apart_id)
  const filteredApartments = apartments.filter((apt) =>
    String(apt.new_apart_id).toLowerCase().includes(searchTerm.toLowerCase())
  );

  const headers = [
    "Адрес",
    "Кв.",
    "Квадратура"
  ];


  // 5) Рендер
  return (
    <div className="bg-muted/60 flex min-h-screen w-full flex-col">
      <Aside />
      <main className="relative flex flex-1 flex-col gap-2 p-2 sm:pl-16 bg-neutral-100">
        <div className="flex bg-white text-gray-800" style={{minHeight: 98+'vh'}}>
          {/* ======== Сайдбар с деревом ======== */}
          <LeftBar        
              apartType={apartType}
              setApartType={setApartType}
              collapsed={collapsed}
              handleToggleSidebar={handleToggleSidebar}
              districts={districts}
              municipalDistricts={municipalDistricts}
              fetchMunicipalDistricts={fetchMunicipalDistricts}
              houseAddresses={houseAddresses}
              fetchHouseAddresses={fetchHouseAddresses}
              expandedNodes={expandedNodes}
              setExpandedNodes={setExpandedNodes}
              fetchApartments={fetchApartments}
            />
            <ApartTable data={apartments} />
        </div>
      </main>
    </div>
  );
}