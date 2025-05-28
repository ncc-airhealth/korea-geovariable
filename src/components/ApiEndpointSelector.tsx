
import React from 'react';
import { Checkbox } from '@/components/ui/checkbox';
import { ApiEndpoint } from '@/types/supabase';

interface ApiEndpointSelectorProps {
  endpoints: ApiEndpoint[];
  selectedEndpoints: ApiEndpoint[];
  toggleEndpoint: (endpoint: ApiEndpoint) => void;
}

const ApiEndpointSelector: React.FC<ApiEndpointSelectorProps> = ({
  endpoints,
  selectedEndpoints,
  toggleEndpoint,
}) => {
  const isSelected = (endpoint: ApiEndpoint) => {
    return selectedEndpoints.some(e => e.path === endpoint.path);
  };

  return (
    <div className="space-y-2">
      {endpoints.map((endpoint) => (
        <div key={endpoint.path} className="flex items-start space-x-2">
          <Checkbox
            id={`endpoint-${endpoint.path}`}
            checked={isSelected(endpoint)}
            onCheckedChange={() => toggleEndpoint(endpoint)}
          />
          <div className="grid gap-1.5 leading-none">
            <label
              htmlFor={`endpoint-${endpoint.path}`}
              className="text-sm font-medium leading-none cursor-pointer"
            >
              {endpoint.name}
            </label>
            <p className="text-xs text-muted-foreground">
              {endpoint.description}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ApiEndpointSelector;
