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
import HistoryPage from './History/HistoryPage';
import LoginPage from './Auth/LoginPage'
import PrivateRoute from './Auth/PrivateRoute';

const rootElement = document.getElementById("root");
const root = ReactDOM.createRoot(rootElement); 
export const HOSTLINK = process.env.REACT_APP_HOST_LINK;
export const ASIDELINK = process.env.REACT_APP_REACT_LINK;

root.render(
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<PrivateRoute><Koren /></PrivateRoute>} />
        <Route path="/table_page" element={<PrivateRoute><Table_page /></PrivateRoute>} />
        <Route path="/dashboard" element={<PrivateRoute><Dashboard_page /></PrivateRoute>} />
        <Route path="/aparts" element={<PrivateRoute><ApartPage /></PrivateRoute>} />
        <Route path="/balance" element={<PrivateRoute><BalancePage /></PrivateRoute>} />
        <Route path="/history" element={<PrivateRoute></PrivateRoute>} />
        <Route path="/login" element={<LoginPage />} />
      </Routes>
    </BrowserRouter>,
  document.getElementById('root')
);

reportWebVitals();