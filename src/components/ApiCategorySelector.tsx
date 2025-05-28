
import React from 'react';
import { Card } from '@/components/ui/card';
import { getCategories, getEndpointsByCategory } from '@/services/apiService';
import { ApiEndpoint } from '@/types/supabase';
import ApiEndpointSelector from './ApiEndpointSelector';

interface ApiCategorySelectorProps {
  selectedEndpoints: ApiEndpoint[];
  toggleEndpoint: (endpoint: ApiEndpoint) => void;
}

const ApiCategorySelector: React.FC<ApiCategorySelectorProps> = ({ 
  selectedEndpoints, 
  toggleEndpoint 
}) => {
  const categories = getCategories();

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">API Endpoints</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {categories.map((category) => (
          <Card key={category} className="p-4">
            <h3 className="font-semibold text-lg mb-3">{category}</h3>
            <ApiEndpointSelector
              endpoints={getEndpointsByCategory(category)}
              selectedEndpoints={selectedEndpoints}
              toggleEndpoint={toggleEndpoint}
            />
          </Card>
        ))}
      </div>
    </div>
  );
};

export default ApiCategorySelector;
