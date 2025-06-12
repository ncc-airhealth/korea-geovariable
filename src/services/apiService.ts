
import { ApiEndpoint, BorderType } from '@/types/supabase';
import { supabase } from '@/integrations/supabase/client';

// API Endpoint Configuration
// Using a relative URL to work with our proxy middleware
export const API_BASE_URL = '/api'; // This will be handled by our proxy
export const API_KEY = 'nzEzme6DWfutggjukBhegGJHWRyaNnLPqVGAPSqejHlCrfZQO519Hpr6ohb_rxYV';

export const API_ENDPOINTS: ApiEndpoint[] = [
  {
    name: 'River',
    path: '/border/river/',
    description: 'Calculate river area within border',
    category: 'Geographic Features'
  },
  {
    name: 'Emission',
    path: '/border/emission/',
    description: 'Calculate emission variables within border',
    category: 'Environmental'
  },
  {
    name: 'Car Registration',
    path: '/border/car_registration/',
    description: 'Calculate car registration number variable within border',
    category: 'Transport'
  },
  {
    name: 'Landuse Area',
    path: '/border/landuse_area/',
    description: 'Calculate landuse area/ratio variable within border',
    category: 'Geographic Features'
  },
  {
    name: 'Coastline Distance',
    path: '/border/coastline_distance/',
    description: 'Calculate distance from coastline to border centroid',
    category: 'Distance'
  },
  {
    name: 'NDVI',
    path: '/border/ndvi/',
    description: 'Calculate NDVI statistics within border',
    category: 'Environmental'
  },
  {
    name: 'Airport Distance',
    path: '/border/airport_distance/',
    description: 'Calculate nearest airport distance variable',
    category: 'Distance'
  },
  {
    name: 'Military Demarcation Line Distance',
    path: '/border/mdl_distance/',
    description: 'Calculate distance from MDL to border centroid',
    category: 'Distance'
  },
  {
    name: 'Port Distance',
    path: '/border/port_distance/',
    description: 'Calculate distance from port to border centroid',
    category: 'Distance'
  },
  {
    name: 'Rail',
    path: '/border/rail/',
    description: 'Calculate rail length within border',
    category: 'Transport'
  },
  {
    name: 'Road',
    path: '/border/road/',
    description: 'Calculate road length within border',
    category: 'Transport'
  },
  {
    name: 'Topographic Model',
    path: '/border/topographic_model/',
    description: 'Calculate DEM/DSM statistics within border',
    category: 'Geographic Features'
  },
  {
    name: 'Raster Emission',
    path: '/border/raster_emission/',
    description: 'Calculate raster emission variables within border',
    category: 'Environmental'
  },
  {
    name: 'Clinic Count',
    path: '/border/clinic_count/',
    description: 'Calculate clinic count variable within border',
    category: 'Healthcare'
  },
  {
    name: 'Hospital Count',
    path: '/border/hospital_count/',
    description: 'Calculate hospital count variable within border',
    category: 'Healthcare'
  }
];

export const getCategories = (): string[] => {
  return Array.from(new Set(API_ENDPOINTS.map(endpoint => endpoint.category)));
};

export const getEndpointsByCategory = (category: string): ApiEndpoint[] => {
  return API_ENDPOINTS.filter(endpoint => endpoint.category === category);
};

export const runApiTests = async (
  endpoints: ApiEndpoint[],
  borderType: BorderType,
  year: number
): Promise<{ endpoint: ApiEndpoint; task_id: string }[]> => {
  const results = [];
  const userId = (await supabase.auth.getUser()).data.user?.id;

  if (!userId) {
    throw new Error('User not authenticated');
  }

  for (const endpoint of endpoints) {
    try {
      // Make the API call to the proxy path
      const response = await fetch(`${API_BASE_URL}${endpoint.path}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': API_KEY
        },
        body: JSON.stringify({ 
          border_type: borderType, 
          year 
        })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      const task_id = data.task_id;

      // Store the test result in Supabase
      await supabase.from('api_test_results').insert({
        user_id: userId,
        endpoint: endpoint.path,
        border_type: borderType,
        year,
        task_id,
        status: 'PENDING'
      });

      results.push({ endpoint, task_id });
    } catch (error) {
      console.error(`Error running API test for ${endpoint.name}:`, error);
      throw error;
    }
  }

  return results;
};

export const getJobStatus = async (task_id: string): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE_URL}/job_status/${task_id}`, {
      method: 'GET',
      headers: {
        'X-API-Key': API_KEY
      }
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Error getting job status for task ${task_id}:`, error);
    throw error;
  }
};

export const updateTestResultStatus = async (task_id: string, status: string, result?: any): Promise<void> => {
  try {
    await supabase
      .from('api_test_results')
      .update({
        status,
        result: result || null
      })
      .eq('task_id', task_id);
  } catch (error) {
    console.error(`Error updating test result status for task ${task_id}:`, error);
    throw error;
  }
};

export const getTestResults = async () => {
  try {
    const { data, error } = await supabase
      .from('api_test_results')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) throw error;
    
    return data;
  } catch (error) {
    console.error('Error fetching test results:', error);
    throw error;
  }
};

export const POINT_ENDPOINTS = [
  {
    name: 'Bus Stop Count',
    path: '/point/bus_stop/',
    description: 'Calculate bus stop counts within buffer around points',
    category: 'Transport'
  },
  {
    name: 'Hospital Count',
    path: '/point/hospital/',
    description: 'Calculate hospital counts within buffer around points',
    category: 'Healthcare'
  }
];

export const runPointCalculation = async (
  coordinates: number[][],
  calculatorType: string,
  bufferSize: number,
  year: number
): Promise<string> => {
  const userId = (await supabase.auth.getUser()).data.user?.id;

  if (!userId) {
    throw new Error('User not authenticated');
  }

  const endpoint = calculatorType === 'bus_stop' ? '/point/bus_stop/' : '/point/hospital/';
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY
    },
    body: JSON.stringify({ 
      coordinates,
      buffer_size: bufferSize,
      year 
    })
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  const data = await response.json();
  return data.task_id;
};

export const runCSVCalculation = async (
  fileId: string,
  calculatorType: string,
  bufferSize: number,
  year: number
): Promise<string> => {
  const userId = (await supabase.auth.getUser()).data.user?.id;

  if (!userId) {
    throw new Error('User not authenticated');
  }

  const response = await fetch(`${API_BASE_URL}/csv/calculate/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY
    },
    body: JSON.stringify({ 
      file_id: fileId,
      calculator_type: calculatorType,
      buffer_size: bufferSize,
      year 
    })
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  const data = await response.json();
  return data.task_id;
};

export const getJobStatusWithProgress = async (task_id: string): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE_URL}/job_status/${task_id}`, {
      method: 'GET',
      headers: {
        'X-API-Key': API_KEY
      }
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Error getting job status for task ${task_id}:`, error);
    throw error;
  }
};
