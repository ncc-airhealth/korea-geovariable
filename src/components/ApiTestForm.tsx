import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { ApiEndpoint, BorderType } from '@/types/supabase';
import { runApiTests } from '@/services/apiService';
import { AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useTranslation } from 'react-i18next';

interface ApiTestFormProps {
  selectedEndpoints: ApiEndpoint[];
  onTestsStarted: (testRuns: { endpoint: ApiEndpoint; task_id: string }[]) => void;
}

const ApiTestForm: React.FC<ApiTestFormProps> = ({ selectedEndpoints, onTestsStarted }) => {
  const [borderType, setBorderType] = useState<BorderType>('sgg');
  const [year, setYear] = useState<number>(2020);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const { t } = useTranslation();
  
  const validYears = [2000, 2005, 2010, 2015, 2020];
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (selectedEndpoints.length === 0) {
      toast.error('Please select at least one API endpoint to test.');
      return;
    }

    setIsLoading(true);
    try {
      const results = await runApiTests(selectedEndpoints, borderType, year);
      toast.success(`Started ${results.length} API test(s).`);
      onTestsStarted(results);
    } catch (error: any) {
      setError(error.message || 'Failed to start API tests.');
      toast.error(error.message || 'Failed to start API tests.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('dashboard.testParameters')}</CardTitle>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          <div className="space-y-2">
            <label htmlFor="border-type" className="text-sm font-medium">{t('dashboard.borderType')}</label>
            <Select
              value={borderType}
              onValueChange={(value: BorderType) => setBorderType(value)}
              disabled={isLoading}
            >
              <SelectTrigger id="border-type">
                <SelectValue placeholder="Select border type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="sgg">{t('dashboard.borderTypes.sgg')}</SelectItem>
                <SelectItem value="emd">{t('dashboard.borderTypes.emd')}</SelectItem>
                <SelectItem value="jgg">{t('dashboard.borderTypes.jgg')}</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <label htmlFor="year" className="text-sm font-medium">{t('dashboard.year')}</label>
            <Select
              value={year.toString()}
              onValueChange={(value) => setYear(parseInt(value, 10))}
              disabled={isLoading}
            >
              <SelectTrigger id="year">
                <SelectValue placeholder="Select year" />
              </SelectTrigger>
              <SelectContent>
                {validYears.map((y) => (
                  <SelectItem key={y} value={y.toString()}>
                    {y}
                    </SelectItem>
                  ))
                }
              </SelectContent>
            </Select>
          </div>
          <div className="pt-2">
            <p className="text-sm font-medium">{t('dashboard.selectedEndpoints')}: {selectedEndpoints.length}</p>
            {selectedEndpoints.length > 0 && (
              <div className="mt-2">
                <ul className="text-xs text-muted-foreground">
                  {selectedEndpoints.slice(0, 3).map((endpoint, index) => (
                    <li key={index}>{endpoint.name}</li>
                  ))}
                  {selectedEndpoints.length > 3 && (
                    <li>+{selectedEndpoints.length - 3} more</li>
                  )}
                </ul>
              </div>
            )}
          </div>
        </CardContent>
        <CardFooter>
          <Button 
            type="submit" 
            className="w-full" 
            disabled={selectedEndpoints.length === 0 || isLoading}
          >
            {isLoading ? t('dashboard.runningTests') : t('dashboard.runTests')}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
};

export default ApiTestForm;
