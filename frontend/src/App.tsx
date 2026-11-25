import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { TripCreationPage } from './pages/TripCreationPage';
import { AIPlanningScreen } from './pages/AIPlanningScreen';
import { DashboardPage } from './pages/DashboardPage';
import { ItineraryPage } from './pages/ItineraryPage';
import { MapViewPage } from './pages/MapViewPage';
import { BudgetPage } from './pages/BudgetPage';
import { DisruptionCenterPage } from './pages/DisruptionCenterPage';
import { ChatAssistantPage } from './pages/ChatAssistantPage';

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/create-trip" element={<TripCreationPage />} />
          <Route path="/plan-trip/:tripId" element={<AIPlanningScreen />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/dashboard/:tripId" element={<DashboardPage />} />
          <Route path="/itinerary/:tripId" element={<ItineraryPage />} />
          <Route path="/map/:tripId" element={<MapViewPage />} />
          <Route path="/budget/:tripId" element={<BudgetPage />} />
          <Route path="/disruptions/:tripId" element={<DisruptionCenterPage />} />
          <Route path="/chat/:tripId" element={<ChatAssistantPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
