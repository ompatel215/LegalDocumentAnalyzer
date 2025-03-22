import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext.js';
import Layout from './components/Layout.js';
import PrivateRoute from './components/PrivateRoute.js';
import Login from './pages/Login.js';
import Register from './pages/Register.js';
import Dashboard from './pages/Dashboard.js';
import DocumentAnalysis from './pages/DocumentAnalysis.js';

function App() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={
          isAuthenticated ? <Navigate to="/dashboard" /> : <Navigate to="/login" />
        } />
        <Route path="login" element={
          !isAuthenticated ? <Login /> : <Navigate to="/dashboard" />
        } />
        <Route path="register" element={
          !isAuthenticated ? <Register /> : <Navigate to="/dashboard" />
        } />
        <Route path="dashboard" element={
          <PrivateRoute>
            <Dashboard />
          </PrivateRoute>
        } />
        <Route path="document/:id" element={
          <PrivateRoute>
            <DocumentAnalysis />
          </PrivateRoute>
        } />
      </Route>
    </Routes>
  );
}

export default App; 