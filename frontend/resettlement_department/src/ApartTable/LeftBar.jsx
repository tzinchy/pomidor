import React, { useState, useEffect } from "react";
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
    setLastSelectedAddres,
    setFilters,
    setRowSelection
  }) {

    // Состояния для хранения выбранных элементов для каждого типа
    const [selections, setSelections] = useState({
      OldApart: {
        selectedAddresses: [],
        selectedMunicipals: []
      },
      NewApartment: {
        selectedAddresses: [],
        selectedMunicipals: []
      }
    });

    // Текущие выбранные элементы в зависимости от типа
    const selectedAddresses = selections[apartType].selectedAddresses;
    const selectedMunicipals = selections[apartType].selectedMunicipals;

    const handleResetFilters = () => {
      setSelections(prev => ({
        ...prev,
        [apartType]: {
          selectedAddresses: [],
          selectedMunicipals: []
        }
      }));
    }

    const toggleExpand = (key) => {
        setExpandedNodes((prev) => ({
          ...prev,
          [key]: !prev[key],
        }));
    };

    const handleMunicipalToggle = (municipal) => {
      setSelections(prev => {
        const currentType = apartType;
        const currentSelections = prev[currentType];
        
        const newSelectedMunicipals = currentSelections.selectedMunicipals.includes(municipal)
          ? currentSelections.selectedMunicipals.filter(m => m !== municipal)
          : [...currentSelections.selectedMunicipals, municipal];
        
        // Если выбираем муниципалитет, загружаем его адреса
        if (!currentSelections.selectedMunicipals.includes(municipal)) {
          fetchHouseAddresses(municipal);
        }
        
        setRowSelection({});
        
        return {
          ...prev,
          [currentType]: {
            ...currentSelections,
            selectedMunicipals: newSelectedMunicipals
          }
        };
      });
    };

    const handleAddressToggle = (address, municipal) => {
      setSelections(prev => {
        const currentType = apartType;
        const currentSelections = prev[currentType];
        
        const newSelectedAddresses = currentSelections.selectedAddresses.includes(address)
          ? currentSelections.selectedAddresses.filter(addr => addr !== address)
          : [...currentSelections.selectedAddresses, address];
        
        setRowSelection({});
        
        return {
          ...prev,
          [currentType]: {
            ...currentSelections,
            selectedAddresses: newSelectedAddresses
          }
        };
      });
    };

    useEffect(() => {
      setLastSelectedAddres(selectedAddresses);
    }, [selectedAddresses]);

    useEffect(() => {
      setLastSelectedMunicipal(selectedMunicipals);
    }, [selectedMunicipals]);

    useEffect(() => {
      if (selectedAddresses.length > 0 || selectedMunicipals.length > 0) {
        fetchApartments(selectedAddresses, selectedMunicipals);
      }
    }, [selectedMunicipals, selectedAddresses]);

    const resetSelection = () => {
      setIsDetailsVisible(false); 
      setSelectedRow(false); 
      setLoading(true); 
      setFilters({}); 
      setRowSelection({});
    };

    const switchApartType = (type) => {
      resetSelection();
      setApartType(type);
    };

    return (
      <div className="relative h-[100vh-1rem]s ">
        <div className={`fixed h-[calc(100vh-1rem)] transition-all duration-300 bg-white rounded-lg overflow-hidden z-[100] ${collapsed ? 'w-0' : ''}`}>
          <Sidebar collapsed={collapsed} className={`transition-all duration-300 h-[calc(100vh-1rem)] w-[270px]`}>
            <Menu>
              {!collapsed && (
                <>
                  <div className="flex justify-around mb-4">
                    <button
                      onClick={() => switchApartType("OldApart")}
                      className={`p-8 py-4 rounded-md ${apartType === "OldApart" ? "bg-gray-200 font-semibold" : "bg-white"}`}
                    >
                      Семьи
                    </button>
                    <button
                      onClick={() => switchApartType("NewApartment")}
                      className={`p-8 py-4 rounded-md ${apartType === "NewApartment" ? "bg-gray-200 font-semibold" : "bg-white"}`}
                    >
                      Ресурс
                    </button>
                  </div>

                  <div className="flex-shrink-0 mt-2">
                    <button
                        onClick={handleResetFilters}
                        className="hover:bg-gray-200 inline-flex items-center justify-center whitespace-nowrap text-sm font-medium hover:bg-gray-100 rounded-md px-3 h-8 border-dashed"
                    >
                        Сброс
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            width="24"
                            height="24"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            className="lucide lucide-x ml-2 h-4 w-4"
                        >
                            <path d="M18 6 6 18" />
                            <path d="m6 6 12 12" />
                        </svg>
                    </button>
                  </div>

                  <div className="h-full pr-2 bg-white text-sm">
                    <ul>
                      {districts.map((district) => {
                        const isDistOpen = expandedNodes[district] ?? false;
                        return (
                          <li key={district} className="mb-2 ">
                            <a
                              href="#"
                              onClick={(e) => {
                                e.preventDefault();
                                toggleExpand(district);
                                if (!municipalDistricts[district]) {
                                  fetchMunicipalDistricts(district);
                                }
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
                                  transform: isDistOpen ? "rotate(90deg)" : "rotate(0deg)",
                                  transition: "transform 0.2s",
                                }}
                              >
                                <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
                              </svg>
                              {district}
                            </a>

                            <ul className={`ml-4 !visible ${isDistOpen ? "" : "hidden"}`}>
                              {municipalDistricts[district]?.map((municipal) => {
                                const isMunOpen = expandedNodes[municipal] ?? false;
                                return (
                                  <li key={municipal} className="mb-2">
                                    <label className="flex items-center px-2 cursor-pointer">
                                      <input
                                        type="checkbox"
                                        checked={selectedMunicipals.includes(municipal)}
                                        onChange={() => handleMunicipalToggle(municipal)}
                                        className="mr-2 h-4 w-4 text-blue-600 rounded focus:ring-blue-500"
                                      />
                                      <div 
                                        className="flex items-center flex-1"
                                        onClick={(e) => {
                                          e.preventDefault();
                                          toggleExpand(municipal);
                                        }}
                                      >
                                        <svg
                                          xmlns="http://www.w3.org/2000/svg"
                                          fill="none"
                                          viewBox="0 0 24 24"
                                          strokeWidth="2.5"
                                          stroke="currentColor"
                                          className="h-4 w-4 me-1"
                                          style={{
                                            transform: isMunOpen ? "rotate(90deg)" : "rotate(0deg)",
                                            transition: "transform 0.2s",
                                          }}
                                        >
                                          <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
                                        </svg>
                                        {municipal}
                                      </div>
                                    </label>

                                    <ul className={`ml-4 !visible ${isMunOpen ? "" : "hidden"}`}>
                                      {houseAddresses[municipal]?.map((address) => (
                                        <li key={address} className="px-2">
                                          <label className="flex items-center px-2 cursor-pointer text-xs">
                                            <input
                                              type="checkbox"
                                              checked={selectedAddresses.includes(address)}
                                              onChange={() => handleAddressToggle(address, municipal)}
                                              className="mr-2 text-blue-600 rounded focus:ring-blue-500"
                                            />
                                            <span>{address}</span>
                                          </label>
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
          className={`fixed top-1/2 left-14 z-[101] w-8 h-8 rounded-full flex items-center justify-center shadow-md transition-transform duration-300 ${
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
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 12l-6 6m0-12l6 6" />
          </svg>
        </button>
      </div>
    );
}

export default LeftBar;