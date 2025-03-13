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
    setSelectedRow,
    setIsDetailsVisible,
    setLoading,
    setLastSelectedMunicipal,
    setLastSelectedAddres
  }) {

    const toggleExpand = (key) => {
        setExpandedNodes((prev) => ({
          ...prev,
          [key]: !prev[key],
        }));
      };

    return (
      <div className="relative h-[100vh-1rem]s ">
        {/* Основной контейнер сайдбара */}
        <div className={`fixed h-[calc(100vh-1rem)] transition-all duration-300 bg-white rounded-lg overflow-hidden z-[100] ${collapsed ? 'w-0' : ''}`}>
          <Sidebar collapsed={collapsed} className={`transition-all duration-300 h-[calc(100vh-1rem)] w-[270px] `} >
            <Menu>
              {!collapsed && (
                <>
                  <div className="flex justify-around mb-4">
                    <button
                      onClick={() => {setIsDetailsVisible(false); setSelectedRow(false); setApartType("OldApart"); setLoading(true); setFilters({});}}
                      className={`p-8 py-4 rounded-md ${apartType === "OldApart" ? "bg-gray-200 font-semibold" : "bg-white"}`}
                    >
                      Семьи
                    </button>
                    <button
                      onClick={() => {setIsDetailsVisible(false); setSelectedRow(false); setApartType("NewApartment"); setLoading(true); setFilters({});}}
                      className={`p-8 py-4 rounded-md ${ apartType === "NewApartment" ? "bg-gray-200 font-semibold" : "bg-white"}`}
                    >
                      Ресурс
                    </button>
                  </div>

                  {/* ======== Дерево район → муниципалитет → адрес ======== */}
                  <div
                    className="h-full pr-2 bg-white"
                  >
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
                              className="flex items-center px-2"
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
                                  transform: isDistOpen
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
                                        setLastSelectedMunicipal(municipal);
                                        setLastSelectedAddres(null);
                                        fetchHouseAddresses(municipal);
                                        fetchApartments(null, municipal);
                                      }}
                                      className="flex items-center px-2"
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
                                          className="px-2"
                                        >
                                          <a
                                            href="#"
                                            onClick={(e) => {
                                              e.preventDefault();
                                              // По клику грузим квартиры этого адреса
                                              setLastSelectedAddres(address);
                                              fetchApartments([address], municipal);
                                            }}
                                            className="flex items-center px-2"
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
                  </div>
                </>
              )}
            </Menu>
          </Sidebar>
        </div>
        <button
          onClick={handleToggleSidebar}
          className={`fixed top-1/2 left-14 z-[101] w-8 h-8  rounded-full flex items-center justify-center shadow-md transition-transform duration-300 ${
            collapsed ? '' : 'translate-x-80'
          }`}
          style={{
            transform: `translateY(-50%) ${collapsed ? '' : 'translateX(210px)'}`
          }}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth="2.5"
            stroke="currentColor"
            className={`h-4 w-4 text-gray-600 transform transition-transform ${
              collapsed ? '' : 'rotate-180'
            }`}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M15 12l-6 6m0-12l6 6"
            />
          </svg>
        </button>
      </div>
    );
}

export default LeftBar;
