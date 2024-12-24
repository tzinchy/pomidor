import React, { useState, useEffect, useRef } from "react";
import { Sidebar, Menu, MenuItem } from 'react-pro-sidebar';

import axios from "axios";

function LeftBar({
    apartType,
    setApartType,
    collapsed,
    handleToggleSidebar,
    districts,
    municipalDistricts,
    fetchMunicipalDistricts,
    houseAddresses,
    fetchHouseAddresses,
    expandedNodes,
    setExpandedNodes,
    fetchApartments,
  }) {



    // Переключаем раскрытие для конкретного узла (district или municipal)
    const toggleExpand = (key) => {
        setExpandedNodes((prev) => ({
          ...prev,
          [key]: !prev[key],
        }));
      };

return (
<Sidebar collapsed={collapsed} className={`transition-all duration-300 ${collapsed ? 'w-16' : 'w-80'}`} >
<Menu>


  {/* Кнопки выбора типа */}
  {!collapsed && (<>
  <div className="flex justify-between mb-4">
    
    <button
      onClick={() => setApartType("NewApartment")}
      className={`px-16 py-4 rounded-md ${
        apartType === "NewApartment"
          ? "bg-blue-500 text-white"
          : "bg-gray-200"
      }`}
    >
      Ресурс
    </button>
    <button
      onClick={() => setApartType("FamilyStructure")}
      className={`px-16 py-4 rounded-md ${
        apartType === "FamilyStructure"
          ? "bg-blue-500 text-white"
          : "bg-gray-200"
      }`}
    >
      Семьи
    </button>
  </div>
  
  {/* ======== Дерево район → муниципалитет → адрес ======== */}
  <ul>
    {districts.map((district) => {
      const isDistOpen = expandedNodes[district] ?? false;
      return (
        <li key={district} className="mb-2">
          {/* Шапка района */}
          <a
            href="#"
            onClick={(e) => {
              e.preventDefault(); // убираем переход по ссылке
              toggleExpand(district);

              // Ленивая загрузка муниципальных округов
              if (!municipalDistricts[district]) {
                fetchMunicipalDistricts(district);
              }
            }}
            className="flex items-center px-2 hover:bg-secondary-100 focus:text-primary active:text-primary"
          >
            {/* Стрелка, поворачиваем при раскрытии */}
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth="2.5"
              stroke="currentColor"
              className="h-4 w-4 me-1"
              style={{
                transform: isDistOpen ? "rotate(90deg)" : "rotate(0deg)",
                transition: "transform 0.2s",
              }}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M8.25 4.5l7.5 7.5-7.5 7.5"
              />
            </svg>
            {district}
          </a>

          {/* Список муниципалитетов */}
          <ul className={`ml-4 !visible ${isDistOpen ? "" : "hidden"}`}>
            {municipalDistricts[district]?.map((municipal) => {
              const isMunOpen = expandedNodes[municipal] ?? false;
              return (
                <li key={municipal} className="mb-2">
                  <a
                    href="#"
                    onClick={(e) => {
                      e.preventDefault();
                      toggleExpand(municipal);
                      // Ленивая загрузка адресов
                      if (!houseAddresses[municipal]) {
                        fetchHouseAddresses(municipal);
                      }
                    }}
                    className="flex items-center px-2 hover:bg-secondary-100 focus:text-primary active:text-primary"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth="2.5"
                      stroke="currentColor"
                      className="h-4 w-4 me-1"
                      style={{
                        transform: isMunOpen
                          ? "rotate(90deg)"
                          : "rotate(0deg)",
                        transition: "transform 0.2s",
                      }}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M8.25 4.5l7.5 7.5-7.5 7.5"
                      />
                    </svg>
                    {municipal}
                  </a>

                  {/* Список адресов */}
                  <ul
                    className={`ml-4 !visible ${
                      isMunOpen ? "" : "hidden"
                    }`}
                  >
                    {houseAddresses[municipal]?.map((address) => (
                      <li
                        key={address}
                        className="px-2 hover:bg-secondary-100"
                      >
                        <a
                          href="#"
                          onClick={(e) => {
                            e.preventDefault();
                            // По клику грузим квартиры этого адреса
                            fetchApartments([address]);
                          }}
                          className="flex items-center px-2 hover:bg-secondary-100 focus:text-primary active:text-primary"
                        >
                          {address}
                        </a>
                      </li>
                    ))}
                  </ul>
                </li>
              );
            })}
          </ul>
        </li>
      );
    })}
  </ul>
</>
)}

</Menu>
<button onClick={handleToggleSidebar}>Toggle Sidebar</button>
</Sidebar> )}

export default LeftBar;