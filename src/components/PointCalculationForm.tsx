import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import { runPointCalculation } from '@/services/apiService';

interface PointCalculationFormProps {
  onTaskSubmitted: (taskId: string, calculatorType: string) => void;
}

const PointCalculationForm: React.FC<PointCalculationFormProps> = ({ onTaskSubmitted }) => {
  const [coordinates, setCoordinates] = useState<string>('');
  const [calculatorType, setCalculatorType] = useState<string>('');
  const [bufferSize, setBufferSize] = useState<string>('');
  const [year, setYear] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!coordinates || !calculatorType || !bufferSize || !year) {
      toast.error('Please fill in all fields');
      return;
    }

    try {
      setIsSubmitting(true);
      
      const coordPairs = coordinates.split(';').map(pair => {
        const [x, y] = pair.trim().split(',').map(Number);
        if (isNaN(x) || isNaN(y)) {
          throw new Error('Invalid coordinate format');
        }
        return [x, y];
      });

      const taskId = await runPointCalculation(
        coordPairs,
        calculatorType,
        parseInt(bufferSize),
        parseInt(year)
      );

      onTaskSubmitted(taskId, calculatorType);
      toast.success('Point calculation started successfully');
      
      setCoordinates('');
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
        <CardTitle>Point-based Calculation</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">
              Coordinates (format: x1,y1;x2,y2;...)
            </label>
            <Input
              value={coordinates}
              onChange={(e) => setCoordinates(e.target.value)}
              placeholder="127.0276,37.4979;127.0286,37.4989"
              className="font-mono"
            />
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

          <Button type="submit" disabled={isSubmitting} className="w-full">
            {isSubmitting ? 'Starting Calculation...' : 'Start Calculation'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default PointCalculationForm;
