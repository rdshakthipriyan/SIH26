import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './services/auth';
import KioskLandingPage from './pages/KioskLandingPage';
import WelcomePage from './pages/WelcomePage';
import LanguagePage from './pages/LanguagePage';
import PatientIdentityPage from './pages/PatientIdentityPage';
import ModeSelectionPage from './pages/ModeSelectionPage';
import ConversationPage from './pages/ConversationPage';
import DocumentUploadPage from './pages/DocumentUploadPage';
import OCRVerifyPage from './pages/OCRVerifyPage';
import QueueStatusPage from './pages/QueueStatusPage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<KioskLandingPage />} />
          <Route path="/welcome" element={<WelcomePage />} />
          <Route path="/language" element={<LanguagePage />} />
          <Route path="/identity" element={<PatientIdentityPage />} />
          <Route path="/mode" element={<ModeSelectionPage />} />
          <Route path="/conversation" element={<ConversationPage />} />
          <Route path="/ayush-intake" element={<Navigate to="/conversation" replace />} />
          <Route path="/documents" element={<DocumentUploadPage />} />
          <Route path="/ocr/verify/:docId" element={<OCRVerifyPage />} />
          <Route path="/queue" element={<QueueStatusPage />} />
          <Route path="*" element={<KioskLandingPage />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
