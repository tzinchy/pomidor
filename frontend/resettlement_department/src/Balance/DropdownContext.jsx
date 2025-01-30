import React, { createContext, useContext, useState } from 'react';

const DropdownContext = createContext();

export const DropdownProvider = ({ children }) => {
  const [selectedItems, setSelectedItems] = useState({});

  const updateSelectedItems = (dropdownId, items) => {
    setSelectedItems(prev => ({
      ...prev,
      [dropdownId]: items
    }));
  };

  return (
    <DropdownContext.Provider value={{ selectedItems, updateSelectedItems }}>
      {children}
    </DropdownContext.Provider>
  );
};

export const useDropdown = () => useContext(DropdownContext);