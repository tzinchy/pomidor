import React, { createContext, useContext, useState } from 'react';

const DropdownContext = createContext();

export const DropdownProvider = ({ children }) => {
  const [selectedItems, setSelectedItems] = useState({});

  const updateSelectedItems = (dropdownId, items) => {
    setSelectedItems(prev => ({ ...prev, [dropdownId]: items }));
  };

  const removeSelectedItems = (dropdownId) => {
    setSelectedItems(prev => {
      const newItems = { ...prev };
      delete newItems[dropdownId];
      return newItems;
    });
  };

  return (
    <DropdownContext.Provider value={{ 
      selectedItems, 
      updateSelectedItems, 
      removeSelectedItems 
    }}>
      {children}
    </DropdownContext.Provider>
  );
};

export const useDropdown = () => {
  const context = useContext(DropdownContext);
  if (!context) {
    throw new Error('useDropdown must be used within a DropdownProvider');
  }
  return context;
};