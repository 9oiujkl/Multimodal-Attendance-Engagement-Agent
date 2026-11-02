import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './layouts/Layout';
import Overview from './pages/Overview';
import Participants from './pages/Participants';
import Sessions from './pages/Sessions';
import Attendance from './pages/Attendance';
import Engagement from './pages/Engagement';
import Recommendations from './pages/Recommendations';
import Reports from './pages/Reports';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Overview />} />
          <Route path="participants" element={<Participants />} />
          <Route path="sessions" element={<Sessions />} />
          <Route path="attendance" element={<Attendance />} />
          <Route path="engagement" element={<Engagement />} />
          <Route path="recommendations" element={<Recommendations />} />
          <Route path="reports" element={<Reports />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
