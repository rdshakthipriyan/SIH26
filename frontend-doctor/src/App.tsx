import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { DoctorAuthProvider } from './services/auth';
import DoctorDashboard from './pages/DoctorDashboard';
import CaseDetail from './pages/CaseDetail';
import DoctorLogin from './pages/DoctorLogin';

function App() {
  return (
    <DoctorAuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<DoctorLogin />} />
          <Route path="/" element={<DoctorDashboard />} />
          <Route path="/case/:sessionId" element={<CaseDetail />} />
          <Route path="*" element={<DoctorDashboard />} />
        </Routes>
      </Router>
    </DoctorAuthProvider>
  );
}

export default App;
