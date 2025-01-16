import React from "react";
import { Sidebar, Menu } from 'react-pro-sidebar';

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
<Sidebar collapsed={collapsed} className={`transition-all duration-300 ${collapsed ? 'w-4' : 'w-80'} overflow-y-auto`} >
  <Menu>
    {/* Кнопки выбора типа */}
    {!collapsed && (
      <>
        <div className="flex justify-around mb-4">
          <button
            onClick={() => setApartType("FamilyStructure")}
            className={`p-8 py-4 rounded-md ${
              apartType === "FamilyStructure"
                ? "bg-gray-200"
                : "bg-white"
            }`}
          >
            Семьи
          </button>
          <button
            onClick={() => setApartType("NewApartment")}
            className={`p-8 py-4 rounded-md ${
              apartType === "NewApartment"
                ? "bg-gray-200"
                : "bg-white"
            }`}
          >
            Ресурс
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
  <button
    onClick={handleToggleSidebar}
    className={`absolute top-1/2 transform -translate-y-1/2 right-0 z-50 w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center shadow-md transition-transform duration-300`}
    style={{
      transform: collapsed
        ? "rotate(0deg)"
        : "rotate(180deg)",
    }}
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth="2.5"
      stroke="currentColor"
      className="h-4 w-4 text-gray-600"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M15 12l-6 6m0-12l6 6"
      />
    </svg>
  </button>

</Sidebar> )}

export default LeftBar;