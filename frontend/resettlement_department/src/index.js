import React from 'react';
import ReactDOM from "react-dom/client";
import reportWebVitals from './reportWebVitals';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './index.css'
import Table_page from './PloshadkiTable/Table_page';
import Dashboard_page from './Dashboard/Dashboard_page';
import ApartPage from './ApartTable/ApartPage';
import ApartTable from './ApartTable/ApartTable';


const rootElement = document.getElementById("root");
const root = ReactDOM.createRoot(rootElement); 

root.render(
    <BrowserRouter>
      <Routes>
        <Route path="/table_page" element={<Table_page />} />
        <Route path="/dashboard" element={<Dashboard_page />} />
        <Route path="/aparts" element={<ApartPage />} />
        <Route path="/try" element={<ApartTable />} />
      </Routes>
    </BrowserRouter>,
  document.getElementById('root')
);

reportWebVitals();
