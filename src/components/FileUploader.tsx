
import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { supabase } from '@/integrations/supabase/client';
import { Upload, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import Papa from 'papaparse';

interface FileUploaderProps {
  onFileUploaded: () => void;
}

interface CSVCoordinate {
  x: number;
  y: number;
  [key: string]: any;
}

const FileUploader: React.FC<FileUploaderProps> = ({ onFileUploaded }) => {
  const { user } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [isUploading, setIsUploading] = useState(false);
  const [previewData, setPreviewData] = useState<CSVCoordinate[]>([]);
  const [coordinateColumns, setCoordinateColumns] = useState<{ x: string; y: string }>({ x: '', y: '' });
  const [headers, setHeaders] = useState<string[]>([]);
  const [isPreviewing, setIsPreviewing] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) {
      setFile(null);
      setPreviewData([]);
      setHeaders([]);
      return;
    }

    const selectedFile = e.target.files[0];
    if (!selectedFile.name.toLowerCase().endsWith('.csv')) {
      toast.error('Please select a CSV file');
      return;
    }

    setFile(selectedFile);
    setFileName(selectedFile.name);
    
    // Parse CSV for preview
    Papa.parse(selectedFile, {
      header: true,
      preview: 5, // Preview first 5 rows
      skipEmptyLines: true,
      complete: (result) => {
        setPreviewData(result.data as CSVCoordinate[]);
        if (result.meta.fields) {
          setHeaders(result.meta.fields);
          // Try to auto-detect x, y columns
          const xCandidates = ['x', 'lon', 'longitude', 'long', 'lng'];
          const yCandidates = ['y', 'lat', 'latitude'];
          
          const detectedX = result.meta.fields.find(field => 
            xCandidates.includes(field.toLowerCase())
          ) || '';
          const detectedY = result.meta.fields.find(field => 
            yCandidates.includes(field.toLowerCase())
          ) || '';
          
          setCoordinateColumns({ x: detectedX, y: detectedY });
        }
      }
    });
  };

  const validateCoordinates = (data: CSVCoordinate[]): boolean => {
    if (!coordinateColumns.x || !coordinateColumns.y) {
      toast.error('Please select both X and Y coordinate columns');
      return false;
    }

    // Check if coordinates are valid numbers
    for (let i = 0; i < data.length; i++) {
      const x = Number(data[i][coordinateColumns.x]);
      const y = Number(data[i][coordinateColumns.y]);
      
      if (isNaN(x) || isNaN(y)) {
        toast.error(`Invalid coordinates in row ${i + 1}`);
        return false;
      }
    }
    
    return true;
  };

  const parseCoordinates = (csvFile: File): Promise<{ data: CSVCoordinate[], count: number }> => {
    return new Promise((resolve, reject) => {
      Papa.parse(csvFile, {
        header: true,
        skipEmptyLines: true,
        complete: (result) => {
          const data = result.data as CSVCoordinate[];
          if (validateCoordinates(data)) {
            resolve({ data, count: data.length });
          } else {
            reject(new Error('Invalid coordinate data'));
          }
        },
        error: (error) => {
          reject(error);
        }
      });
    });
  };

  const handleUpload = async () => {
    if (!file || !user) return;
    
    if (!fileName.trim()) {
      toast.error('Please enter a file name');
      return;
    }

    setIsUploading(true);

    try {
      // Validate and parse the CSV file
      const { data, count } = await parseCoordinates(file);
      
      // Upload file to Supabase Storage
      const fileExt = file.name.split('.').pop();
      const filePath = `${user.id}/${Date.now()}.${fileExt}`;
      const { error: uploadError } = await supabase.storage
        .from('csv_files')
        .upload(filePath, file);

      if (uploadError) throw uploadError;

      // Save metadata to the database
      const { error: insertError } = await supabase
        .from('coordinate_files')
        .insert({
          user_id: user.id,
          file_name: fileName,
          file_path: filePath,
          description,
          coordinate_system: 'WGS84', // Default value
          total_points: count
        });

      if (insertError) throw insertError;

      // Reset the form
      setFile(null);
      setFileName('');
      setDescription('');
      setPreviewData([]);
      setHeaders([]);
      setCoordinateColumns({ x: '', y: '' });
      setIsPreviewing(false);

      // Notify parent component
      onFileUploaded();
    } catch (error: any) {
      toast.error(`Upload failed: ${error.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handlePreview = () => {
    setIsPreviewing(true);
  };

  return (
    <div className="space-y-6">
      <div className="grid gap-4">
        <label className="font-medium text-sm">Select CSV File</label>
        <Input 
          type="file" 
          accept=".csv" 
          onChange={handleFileChange}
          className="cursor-pointer"
        />
      </div>

      {file && !isPreviewing && (
        <div className="flex justify-end">
          <Button 
            variant="outline" 
            onClick={handlePreview}
          >
            Preview Data
          </Button>
        </div>
      )}

      {file && isPreviewing && (
        <>
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-medium mb-2">File Details</h3>
              <p className="text-sm text-gray-600">Name: {file.name}</p>
              <p className="text-sm text-gray-600">Size: {(file.size / 1024).toFixed(2)} KB</p>
            </div>
            
            <div>
              <h3 className="text-lg font-medium mb-2">Preview</h3>
              {previewData.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full border border-gray-200">
                    <thead>
                      <tr className="bg-gray-50">
                        {headers.map((header, index) => (
                          <th key={index} className="px-4 py-2 text-left text-sm font-medium text-gray-500 border-b">
                            {header}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {previewData.map((row, rowIndex) => (
                        <tr key={rowIndex} className="border-b">
                          {headers.map((header, colIndex) => (
                            <td key={colIndex} className="px-4 py-2 text-sm">
                              {String(row[header] || '')}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-gray-500">No data to preview</p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="font-medium text-sm">Select X Coordinate Column</label>
                <select 
                  className="w-full border rounded-md p-2 mt-1"
                  value={coordinateColumns.x}
                  onChange={(e) => setCoordinateColumns(prev => ({ ...prev, x: e.target.value }))}
                >
                  <option value="">Select column</option>
                  {headers.map((header, index) => (
                    <option key={index} value={header}>{header}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="font-medium text-sm">Select Y Coordinate Column</label>
                <select 
                  className="w-full border rounded-md p-2 mt-1"
                  value={coordinateColumns.y}
                  onChange={(e) => setCoordinateColumns(prev => ({ ...prev, y: e.target.value }))}
                >
                  <option value="">Select column</option>
                  {headers.map((header, index) => (
                    <option key={index} value={header}>{header}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="font-medium text-sm">File Name</label>
              <Input 
                value={fileName} 
                onChange={(e) => setFileName(e.target.value)} 
                placeholder="Enter a name for this file"
                className="mt-1"
              />
            </div>
            
            <div>
              <label className="font-medium text-sm">Description (optional)</label>
              <Textarea 
                value={description} 
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Add a description for this coordinate file"
                className="mt-1"
              />
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <Button
              variant="outline"
              onClick={() => {
                setIsPreviewing(false);
                setFile(null);
              }}
              disabled={isUploading}
            >
              Cancel
            </Button>
            <Button
              onClick={handleUpload}
              disabled={isUploading}
            >
              {isUploading ? (
                <>
                  <Upload className="mr-2 h-4 w-4 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Check className="mr-2 h-4 w-4" />
                  Upload File
                </>
              )}
            </Button>
          </div>
        </>
      )}
    </div>
  );
};

export default FileUploader;
