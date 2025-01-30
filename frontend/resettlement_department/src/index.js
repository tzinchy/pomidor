import React from 'react';
import ReactDOM from "react-dom/client";
import reportWebVitals from './reportWebVitals';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './index.css'
import Table_page from './PloshadkiTable/Table_page';
import Dashboard_page from './Dashboard/Dashboard_page';
import ApartPage from './ApartTable/ApartPage';
import Koren from './Koren';
import BalancePage from './Balance/BalancePage';


const rootElement = document.getElementById("root");
const root = ReactDOM.createRoot(rootElement); 
export const HOSTLINK = process.env.REACT_APP_HOST_LINK;
// export const HOSTLINK = '';
export const ASIDELINK = process.env.REACT_APP_REACT_LINK;
console.log(ASIDELINK)
//const ASIDELINK = 'http://10.9.96.160:3001';

root.render(
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Koren />} />
        <Route path="/table_page" element={<Table_page />} />
        <Route path="/dashboard" element={<Dashboard_page />} />
        <Route path="/aparts" element={<ApartPage />} />
        <Route path="/balance" element={<BalancePage />} />
      </Routes>
    </BrowserRouter>,
  document.getElementById('root')
);

reportWebVitals();