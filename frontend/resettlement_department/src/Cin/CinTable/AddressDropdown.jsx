import { useState, useEffect, useRef } from "react";
import { Menu } from '@headlessui/react';

export default function AddressDropdown({ addresses, value, onChange, placeholder }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  const filteredAddresses = addresses.filter(address =>
    address.toLowerCase().includes(searchTerm.toLowerCase())
  );

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
        setSearchTerm('');
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    } else {
      document.removeEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  return (
    <div ref={dropdownRef}>
      <Menu as="div" className="relative">
        <Menu.Button
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-left focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          onClick={() => setIsOpen(!isOpen)}
        >
          {value || placeholder}
        </Menu.Button>
        {isOpen && (
          <Menu.Items
            static
            className="absolute z-10 mt-1 w-full bg-white shadow-lg rounded-md py-1 ring-1 ring-black ring-opacity-5 focus:outline-none max-h-60 overflow-auto"
          >
            <div className="px-3 py-2 sticky top-[-4px] bg-white">
              <input
                type="text"
                placeholder="Поиск адреса..."
                className="w-full px-2 py-1 border border-gray-300 rounded-md text-sm"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                autoFocus
              />
            </div>
            {filteredAddresses.length > 0 ? (
              filteredAddresses.map((address) => (
                <Menu.Item key={address}>
                  {({ active }) => (
                    <button
                      className={`${
                        active ? 'bg-gray-100' : ''
                      } block px-4 py-2 text-sm text-gray-700 w-full text-left`}
                      onClick={() => {
                        onChange(address);
                        setIsOpen(false);
                        setSearchTerm('');
                      }}
                    >
                      {address}
                    </button>
                  )}
                </Menu.Item>
              ))
            ) : (
              <div className="px-4 py-2 text-sm text-gray-500">Адресов не найдено</div>
            )}
          </Menu.Items>
        )}
      </Menu>
    </div>
  );
};