import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import { useAuth } from '@/contexts/AuthContext';
import { supabase } from '@/integrations/supabase/client';
import { runCSVCalculation } from '@/services/apiService';
import { CoordinateFile } from '@/types/supabase';

interface CSVCalculationFormProps {
  onTaskSubmitted: (taskId: string, calculatorType: string) => void;
}

const CSVCalculationForm: React.FC<CSVCalculationFormProps> = ({ onTaskSubmitted }) => {
  const { user } = useAuth();
  const [files, setFiles] = useState<CoordinateFile[]>([]);
  const [selectedFileId, setSelectedFileId] = useState<string>('');
  const [calculatorType, setCalculatorType] = useState<string>('');
  const [bufferSize, setBufferSize] = useState<string>('');
  const [year, setYear] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoadingFiles, setIsLoadingFiles] = useState(true);

  useEffect(() => {
    fetchFiles();
  }, [user]);

  const fetchFiles = async () => {
    if (!user) return;

    try {
      const { data, error } = await supabase
        .from('coordinate_files')
        .select('*')
        .order('updated_at', { ascending: false });

      if (error) throw error;
      setFiles(data || []);
    } catch (error: any) {
      toast.error(`Error fetching files: ${error.message}`);
    } finally {
      setIsLoadingFiles(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedFileId || !calculatorType || !bufferSize || !year) {
      toast.error('Please fill in all fields');
      return;
    }

    try {
      setIsSubmitting(true);
      
      const taskId = await runCSVCalculation(
        selectedFileId,
        calculatorType,
        parseInt(bufferSize),
        parseInt(year)
      );

      onTaskSubmitted(taskId, calculatorType);
      toast.success('CSV calculation started successfully');
      
      setSelectedFileId('');
      setCalculatorType('');
      setBufferSize('');
      setYear('');
      
    } catch (error: any) {
      toast.error(`Failed to start calculation: ${error.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>CSV File Calculation</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Select CSV File</label>
            <Select value={selectedFileId} onValueChange={setSelectedFileId}>
              <SelectTrigger>
                <SelectValue placeholder={isLoadingFiles ? "Loading files..." : "Select a CSV file"} />
              </SelectTrigger>
              <SelectContent>
                {files.map((file) => (
                  <SelectItem key={file.id} value={file.id}>
                    {file.file_name} ({file.total_points} points)
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Calculator Type</label>
            <Select value={calculatorType} onValueChange={setCalculatorType}>
              <SelectTrigger>
                <SelectValue placeholder="Select calculator type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="bus_stop">Bus Stop Count</SelectItem>
                <SelectItem value="hospital">Hospital Count</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Buffer Size (meters)</label>
            <Select value={bufferSize} onValueChange={setBufferSize}>
              <SelectTrigger>
                <SelectValue placeholder="Select buffer size" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="100">100m</SelectItem>
                <SelectItem value="300">300m</SelectItem>
                <SelectItem value="500">500m</SelectItem>
                <SelectItem value="1000">1000m</SelectItem>
                <SelectItem value="5000">5000m</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Year</label>
            <Select value={year} onValueChange={setYear}>
              <SelectTrigger>
                <SelectValue placeholder="Select year" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="2000">2000</SelectItem>
                <SelectItem value="2005">2005</SelectItem>
                <SelectItem value="2010">2010</SelectItem>
                <SelectItem value="2015">2015</SelectItem>
                <SelectItem value="2020">2020</SelectItem>
                <SelectItem value="2023">2023</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Button type="submit" disabled={isSubmitting || isLoadingFiles} className="w-full">
            {isSubmitting ? 'Starting Calculation...' : 'Start Calculation'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default CSVCalculationForm;
