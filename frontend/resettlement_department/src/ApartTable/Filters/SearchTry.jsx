import React from "react";

export default function SearchTry({ placeholder, setSearchQuery }) {
  return (
    <div className="relative flex items-center w-40 mr-4">
      <input
        type="search"
        className="border-input flex rounded-md border py-2 text-sm focus-visible:outline-none h-8 px-2 lg:px-3 w-full"
        placeholder={placeholder}
        onChange={setSearchQuery}
      />
    </div>
  );
}
