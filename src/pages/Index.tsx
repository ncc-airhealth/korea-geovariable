
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import Dashboard from './Dashboard';
import ProtectedRoute from '@/components/ProtectedRoute';

const Index = () => {
  const { session } = useAuth();

  // If the user is not authenticated, redirect to landing page
  if (!session) {
    return <Navigate to="/" />;
  }

  return (
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  );
};

export default Index;
