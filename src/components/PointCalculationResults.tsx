import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { RefreshCw, Download } from 'lucide-react';
import { getJobStatusWithProgress } from '@/services/apiService';

interface PointTask {
  taskId: string;
  calculatorType: string;
  startTime: Date;
}

interface PointCalculationResultsProps {
  activeTasks: PointTask[];
  onTaskComplete: (taskId: string) => void;
}

const PointCalculationResults: React.FC<PointCalculationResultsProps> = ({ 
  activeTasks, 
  onTaskComplete 
}) => {
  const [taskStatuses, setTaskStatuses] = useState<Record<string, any>>({});
  const [isPolling, setIsPolling] = useState(false);

  useEffect(() => {
    let intervalId: NodeJS.Timeout;
    
    const pollTaskStatuses = async () => {
      if (activeTasks.length === 0) return;
      
      setIsPolling(true);
      
      try {
        const statusPromises = activeTasks.map(task => 
          getJobStatusWithProgress(task.taskId)
        );
        
        const statuses = await Promise.all(statusPromises);
        
        const statusMap: Record<string, any> = {};
        statuses.forEach((status, index) => {
          const taskId = activeTasks[index].taskId;
          statusMap[taskId] = status;
          
          if (status.status === 'SUCCESS' || status.status === 'FAILURE') {
            onTaskComplete(taskId);
          }
        });
        
        setTaskStatuses(statusMap);
      } catch (error) {
        console.error('Error polling task statuses:', error);
      } finally {
        setIsPolling(false);
      }
    };
    
    if (activeTasks.length > 0) {
      pollTaskStatuses();
      intervalId = setInterval(pollTaskStatuses, 3000);
    }
    
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [activeTasks, onTaskComplete]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'SUCCESS':
        return <Badge className="bg-green-500">Completed</Badge>;
      case 'FAILURE':
        return <Badge variant="destructive">Failed</Badge>;
      case 'PROGRESS':
        return <Badge className="bg-blue-500">Processing</Badge>;
      case 'PENDING':
      case 'STARTED':
        return <Badge className="bg-yellow-500">Running</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const downloadResults = (taskId: string) => {
    const status = taskStatuses[taskId];
    if (status?.result && status.status === 'SUCCESS') {
      const dataStr = JSON.stringify(status.result, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `point_calculation_${taskId}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }
  };

  if (activeTasks.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Point Calculation Results</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-center text-muted-foreground py-4">
            No active calculations
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Point Calculation Results</CardTitle>
        <Button 
          variant="outline" 
          size="sm" 
          disabled={isPolling}
        >
          <RefreshCw className={`h-4 w-4 mr-1 ${isPolling ? 'animate-spin' : ''}`} />
          {isPolling ? 'Updating...' : 'Auto-updating'}
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activeTasks.map((task) => {
            const status = taskStatuses[task.taskId];
            const progress = status?.progress;
            
            return (
              <div key={task.taskId} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <h4 className="font-medium">
                      {task.calculatorType.replace('_', ' ').toUpperCase()} Calculation
                    </h4>
                    <p className="text-sm text-muted-foreground">
                      Started: {task.startTime.toLocaleTimeString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    {status && getStatusBadge(status.status)}
                    {status?.status === 'SUCCESS' && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => downloadResults(task.taskId)}
                      >
                        <Download className="h-4 w-4 mr-1" />
                        Download
                      </Button>
                    )}
                  </div>
                </div>
                
                {progress && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>{progress.status}</span>
                      <span>{progress.current}/{progress.total}</span>
                    </div>
                    <Progress 
                      value={(progress.current / progress.total) * 100} 
                      className="w-full"
                    />
                  </div>
                )}
                
                {status?.status === 'FAILURE' && status.result && (
                  <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm">
                    <strong>Error:</strong> {status.result.error || 'Unknown error'}
                  </div>
                )}
                
                <div className="mt-2 text-xs text-muted-foreground">
                  Task ID: {task.taskId}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default PointCalculationResults;
