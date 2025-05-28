
import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import Header from '@/components/Header';
import ApiCategorySelector from '@/components/ApiCategorySelector';
import ApiTestForm from '@/components/ApiTestForm';
import ApiTestResults from '@/components/ApiTestResults';
import { ApiEndpoint } from '@/types/supabase';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [selectedEndpoints, setSelectedEndpoints] = useState<ApiEndpoint[]>([]);
  const [activeTests, setActiveTests] = useState<{ endpoint: ApiEndpoint; task_id: string }[]>([]);

  const toggleEndpoint = (endpoint: ApiEndpoint) => {
    setSelectedEndpoints(prev => {
      const isSelected = prev.some(e => e.path === endpoint.path);
      if (isSelected) {
        return prev.filter(e => e.path !== endpoint.path);
      } else {
        return [...prev, endpoint];
      }
    });
  };

  const handleTestsStarted = (testRuns: { endpoint: ApiEndpoint; task_id: string }[]) => {
    setActiveTests(prev => [...testRuns, ...prev]);
    // Reset selected endpoints after running tests
    setSelectedEndpoints([]);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <ApiCategorySelector
              selectedEndpoints={selectedEndpoints}
              toggleEndpoint={toggleEndpoint}
            />
            <div className="mt-6">
              <ApiTestResults activeTests={activeTests} />
            </div>
          </div>
          <div>
            <ApiTestForm
              selectedEndpoints={selectedEndpoints}
              onTestsStarted={handleTestsStarted}
            />
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
