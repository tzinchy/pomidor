import React from 'react';
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './index.css';
import Table_page from './PloshadkiTable/Table_page';
import DashboardPage from './Dashboard/DashboardPage';
import ApartPage from './ApartTable/ApartPage';
import Koren from './Koren';
import BalancePage from './Balance/BalancePage';
import HistoryPage from './History/HistoryPage';
import LoginPage from './Auth/LoginPage';
import PrivateRoute from './Auth/PrivateRoute';
import ParentChildTable from './Test';
import { data } from './MessegeData';
import ChessGrid from './ChessGrid';
import CinPage from './Cin/CinPage';

const rootElement = document.getElementById("root");
const root = ReactDOM.createRoot(rootElement); 

export const HOSTLINK = import.meta.env.VITE_HOST_LINK;
export const ASIDELINK = import.meta.env.VITE_REACT_LINK;

root.render(
  <BrowserRouter>
    <Routes>
      {/* <Route path="/" element={<PrivateRoute><Koren /></PrivateRoute>} />
      <Route path="/table_page" element={<PrivateRoute><Table_page /></PrivateRoute>} />
      <Route path="/dashboard" element={<PrivateRoute><DashboardPage /></PrivateRoute>} />
      <Route path="/aparts" element={<PrivateRoute><ApartPage /></PrivateRoute>} />
      <Route path="/balance" element={<PrivateRoute><BalancePage /></PrivateRoute>} />
      <Route path="/history" element={<PrivateRoute><HistoryPage/></PrivateRoute>} /> */}

      <Route path="/" element={<Koren />} />
      <Route path="/table_page" element={<Table_page />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/aparts" element={<ApartPage />} />
      <Route path="/balance" element={<BalancePage />} />
      <Route path="/history" element={<HistoryPage />} />
      <Route path="/cin" element={<CinPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/test" element={<ChessGrid />} />
    </Routes>
  </BrowserRouter>
);

