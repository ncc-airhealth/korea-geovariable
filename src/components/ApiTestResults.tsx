
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ApiEndpoint, ApiTestResult } from '@/types/supabase';
import { getJobStatus, updateTestResultStatus, getTestResults } from '@/services/apiService';
import { Badge } from '@/components/ui/badge';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { ChevronDown, ChevronUp, RefreshCw } from 'lucide-react';

interface ApiTestResultsProps {
  activeTests: { endpoint: ApiEndpoint; task_id: string }[];
}

const ApiTestResults: React.FC<ApiTestResultsProps> = ({ activeTests }) => {
  const [results, setResults] = useState<ApiTestResult[]>([]);
  const [expandedResults, setExpandedResults] = useState<Record<string, boolean>>({});
  const [isPolling, setIsPolling] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<string>("active");

  // Function to toggle result expansion
  const toggleExpand = (id: string) => {
    setExpandedResults(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  // Function to format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  // Function to format JSON
  const formatJSON = (json: any) => {
    return JSON.stringify(json, null, 2);
  };

  // Poll for updates to active tests
  useEffect(() => {
    let intervalId: NodeJS.Timeout;
    
    const pollActiveTests = async () => {
      if (activeTests.length === 0) return;
      
      setIsPolling(true);
      
      try {
        for (const test of activeTests) {
          const statusResponse = await getJobStatus(test.task_id);
          
          if (statusResponse.status !== 'PENDING' && statusResponse.status !== 'STARTED') {
            await updateTestResultStatus(
              test.task_id,
              statusResponse.status,
              statusResponse.result
            );
          }
        }
        
        // Refresh results
        loadTestResults();
      } catch (error) {
        console.error('Error polling test results:', error);
      }
    };
    
    if (activeTests.length > 0) {
      intervalId = setInterval(pollActiveTests, 5000);
    }
    
    return () => {
      if (intervalId) clearInterval(intervalId);
      setIsPolling(false);
    };
  }, [activeTests]);

  // Load test results
  const loadTestResults = async () => {
    setIsLoading(true);
    try {
      const data = await getTestResults();
      setResults(data || []);
    } catch (error) {
      console.error('Error loading test results:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Initial load of results
  useEffect(() => {
    loadTestResults();
  }, []);

  const getStatusBadge = (status: string | null) => {
    if (!status) return <Badge variant="outline">Unknown</Badge>;
    
    switch (status.toUpperCase()) {
      case 'SUCCESS':
        return <Badge className="bg-green-500">Success</Badge>;
      case 'FAILURE':
        return <Badge variant="destructive">Failed</Badge>;
      case 'PENDING':
      case 'STARTED':
        return <Badge className="bg-yellow-500">Running</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };
  
  const activeResults = results.filter(r => 
    r.status === 'PENDING' || r.status === 'STARTED'
  );
  
  const completedResults = results.filter(r => 
    r.status !== 'PENDING' && r.status !== 'STARTED'
  );

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Test Results</CardTitle>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={loadTestResults}
          disabled={isLoading}
        >
          <RefreshCw className={`h-4 w-4 mr-1 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="active" value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="active">
              Active Tests {activeResults.length > 0 && `(${activeResults.length})`}
            </TabsTrigger>
            <TabsTrigger value="completed">
              Completed Tests {completedResults.length > 0 && `(${completedResults.length})`}
            </TabsTrigger>
          </TabsList>
          <TabsContent value="active" className="mt-4">
            {activeResults.length === 0 ? (
              <p className="text-center text-muted-foreground py-4">No active tests</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Endpoint</TableHead>
                    <TableHead>Parameters</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Started</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {activeResults.map((result) => (
                    <TableRow key={result.id}>
                      <TableCell>{result.endpoint}</TableCell>
                      <TableCell>
                        Border: {result.border_type}, Year: {result.year}
                      </TableCell>
                      <TableCell>{getStatusBadge(result.status)}</TableCell>
                      <TableCell>{formatDate(result.created_at)}</TableCell>
                      <TableCell>
                        <Button variant="ghost" size="sm" disabled>
                          Waiting...
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </TabsContent>
          <TabsContent value="completed" className="mt-4">
            {completedResults.length === 0 ? (
              <p className="text-center text-muted-foreground py-4">No completed tests</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Endpoint</TableHead>
                    <TableHead>Parameters</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Completed</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {completedResults.map((result) => (
                    <React.Fragment key={result.id}>
                      <TableRow>
                        <TableCell>{result.endpoint}</TableCell>
                        <TableCell>
                          Border: {result.border_type}, Year: {result.year}
                        </TableCell>
                        <TableCell>{getStatusBadge(result.status)}</TableCell>
                        <TableCell>{formatDate(result.created_at)}</TableCell>
                        <TableCell>
                          <Collapsible
                            open={!!expandedResults[result.id]}
                            onOpenChange={() => toggleExpand(result.id)}
                          >
                            <CollapsibleTrigger asChild>
                              <Button variant="ghost" size="sm">
                                {expandedResults[result.id] ? (
                                  <><ChevronUp className="h-4 w-4 mr-1" /> Hide</>
                                ) : (
                                  <><ChevronDown className="h-4 w-4 mr-1" /> View</>
                                )}
                              </Button>
                            </CollapsibleTrigger>
                          </Collapsible>
                        </TableCell>
                      </TableRow>
                      {expandedResults[result.id] && (
                        <TableRow>
                          <TableCell colSpan={5} className="bg-muted/50">
                            <CollapsibleContent>
                              <div className="p-2">
                                <h4 className="font-semibold mb-1">Result:</h4>
                                <pre className="bg-black text-white p-3 rounded-md overflow-x-auto text-xs">
                                  {formatJSON(result.result)}
                                </pre>
                              </div>
                            </CollapsibleContent>
                          </TableCell>
                        </TableRow>
                      )}
                    </React.Fragment>
                  ))}
                </TableBody>
              </Table>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default ApiTestResults;
