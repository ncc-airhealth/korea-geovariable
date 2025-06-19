import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import FileUploader from '@/components/FileUploader';
import FileList from '@/components/FileList';
import PointCalculationForm from '@/components/PointCalculationForm';
import CSVCalculationForm from '@/components/CSVCalculationForm';
import PointCalculationResults from '@/components/PointCalculationResults';

interface PointTask {
  taskId: string;
  calculatorType: string;
  startTime: Date;
}

const PointCalculations: React.FC = () => {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [activeTasks, setActiveTasks] = useState<PointTask[]>([]);

  const handleFileUploaded = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  const handleTaskSubmitted = (taskId: string, calculatorType: string) => {
    const newTask: PointTask = {
      taskId,
      calculatorType,
      startTime: new Date()
    };
    setActiveTasks(prev => [...prev, newTask]);
  };

  const handleTaskComplete = (taskId: string) => {
    setActiveTasks(prev => prev.filter(task => task.taskId !== taskId));
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Point-based Geovariable Calculations</h1>
        <p className="text-muted-foreground mt-2">
          Calculate geovariables for specific coordinates or CSV files containing multiple points.
        </p>
      </div>

      <Tabs defaultValue="single-point" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="single-point">Single Point</TabsTrigger>
          <TabsTrigger value="csv-calculation">CSV Calculation</TabsTrigger>
          <TabsTrigger value="file-management">File Management</TabsTrigger>
          <TabsTrigger value="results">Results</TabsTrigger>
        </TabsList>

        <TabsContent value="single-point" className="space-y-6">
          <PointCalculationForm onTaskSubmitted={handleTaskSubmitted} />
        </TabsContent>

        <TabsContent value="csv-calculation" className="space-y-6">
          <CSVCalculationForm onTaskSubmitted={handleTaskSubmitted} />
        </TabsContent>

        <TabsContent value="file-management" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h2 className="text-xl font-semibold mb-4">Upload CSV File</h2>
              <FileUploader onFileUploaded={handleFileUploaded} />
            </div>
            <div>
              <h2 className="text-xl font-semibold mb-4">Manage Files</h2>
              <FileList refreshTrigger={refreshTrigger} />
            </div>
          </div>
        </TabsContent>

        <TabsContent value="results" className="space-y-6">
          <PointCalculationResults 
            activeTasks={activeTasks}
            onTaskComplete={handleTaskComplete}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default PointCalculations;
