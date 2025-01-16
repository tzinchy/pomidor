import React, { useState } from "react";

export default function SearchInput({ placeholder, onSearch }) {

  return (
    <div className="relative flex items-center w-40">
      <input
        type="search"
        className="border-input focus-visible:ring-ring flex rounded-md border py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 h-8 px-2 lg:px-3 w-full"
        placeholder={placeholder}
        onChange={onSearch}
      />
    </div>
  );
}
