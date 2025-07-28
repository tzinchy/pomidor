import React, { useState } from 'react';
import { useDropdown } from './DropdownContext';
import { HOSTLINK } from '../..';

const TestBtn = () => {
  const { selectedItems } = useDropdown();
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  
  return (
    <div className="m-4">
      <button
        onClick={ () => console.log('selectedItems', selectedItems)}
        disabled={loading}
        className={`px-4 py-2 border rounded-md ${
          loading 
            ? 'bg-gray-300 cursor-not-allowed' 
            : 'hover:bg-gray-50 bg-white'
        }`}
      >
        test
      </button>
      {errorMessage && (
        <div className="mt-2 text-red-500 text-sm">
          {errorMessage}
        </div>
      )}
    </div>
  );
};

export default TestBtn;