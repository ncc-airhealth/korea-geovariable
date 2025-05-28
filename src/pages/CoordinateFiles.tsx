
import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import Header from '@/components/Header';
import FileUploader from '@/components/FileUploader';
import FileList from '@/components/FileList';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';

const CoordinateFiles: React.FC = () => {
  const { user } = useAuth();
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleFileUploaded = () => {
    toast.success("File uploaded successfully!");
    // Refresh the file list after upload
    setRefreshTrigger(prev => prev + 1);
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="container mx-auto px-4 py-6">
          <div className="flex justify-center items-center h-64">
            <div className="text-center">
              <h2 className="text-2xl font-bold mb-2">Please Sign In</h2>
              <p className="text-gray-600 mb-4">You need to be logged in to manage coordinate files.</p>
              <Button variant="default" onClick={() => window.location.href = '/auth'}>
                Sign In
              </Button>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto px-4 py-6">
        <h1 className="text-3xl font-bold mb-6">Coordinate File Management</h1>
        
        <Tabs defaultValue="files" className="w-full">
          <TabsList className="mb-4">
            <TabsTrigger value="files">My Files</TabsTrigger>
            <TabsTrigger value="upload">Upload New File</TabsTrigger>
          </TabsList>
          
          <TabsContent value="files">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h2 className="text-xl font-semibold mb-4">My Coordinate Files</h2>
              <FileList refreshTrigger={refreshTrigger} />
            </div>
          </TabsContent>
          
          <TabsContent value="upload">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h2 className="text-xl font-semibold mb-4">Upload New File</h2>
              <FileUploader onFileUploaded={handleFileUploaded} />
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default CoordinateFiles;
