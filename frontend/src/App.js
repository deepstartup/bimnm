import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Header from './components/common/Header';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import Dashboard from './pages/Dashboard';
import COEProcessor from './pages/COEProcessor';
import SQLAnalysis from './pages/SQLAnalysis';
import ReportConsolidation from './pages/ReportConsolidation';
import ProtectedRoute from './components/auth/ProtectedRoute';

function App() {
  const { loading, isAuthenticated } = useAuth();

  if (loading) {
    return (
      <div className="app">
        <div className="loader">Loading...</div>
      </div>
    );
  }

  return (
    <div className="app">
      <Routes>
        <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/dashboard" replace />} />
        <Route path="/register" element={!isAuthenticated ? <Register /> : <Navigate to="/dashboard" replace />} />
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <Header />
              <Routes>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/coe" element={<COEProcessor />} />
                <Route path="/sql" element={<SQLAnalysis />} />
                <Route path="/consolidation" element={<ReportConsolidation />} />
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </ProtectedRoute>
          }
        />
      </Routes>
    </div>
  );
}

export default App;
