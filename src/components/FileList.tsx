
import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { supabase } from '@/integrations/supabase/client';
import { DownloadCloud, Edit, Trash2, Eye, Search, FileSpreadsheet, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatDistanceToNow } from 'date-fns';
import Papa from 'papaparse';

interface FileListProps {
  refreshTrigger: number;
}

interface CoordinateFile {
  id: string;
  user_id: string;
  file_name: string;
  file_path: string;
  description: string | null;
  coordinate_system: string;
  total_points: number;
  created_at: string;
  updated_at: string;
}

interface CSVRow {
  [key: string]: any;
}

const FileList: React.FC<FileListProps> = ({ refreshTrigger }) => {
  const { user } = useAuth();
  const [files, setFiles] = useState<CoordinateFile[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFile, setSelectedFile] = useState<CoordinateFile | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);
  const [editedFileName, setEditedFileName] = useState('');
  const [editedDescription, setEditedDescription] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [previewData, setPreviewData] = useState<CSVRow[]>([]);
  const [headers, setHeaders] = useState<string[]>([]);
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);

  useEffect(() => {
    fetchFiles();
  }, [refreshTrigger, user]);

  const fetchFiles = async () => {
    if (!user) return;

    setIsLoading(true);
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
      setIsLoading(false);
    }
  };

  const handleEdit = (file: CoordinateFile) => {
    setSelectedFile(file);
    setEditedFileName(file.file_name);
    setEditedDescription(file.description || '');
    setIsEditDialogOpen(true);
  };

  const handleDelete = (file: CoordinateFile) => {
    setSelectedFile(file);
    setIsDeleteDialogOpen(true);
  };

  const handleView = async (file: CoordinateFile) => {
    setSelectedFile(file);
    setIsLoadingPreview(true);
    setIsViewDialogOpen(true);

    try {
      // Download file from Supabase Storage
      const { data, error } = await supabase.storage
        .from('csv_files')
        .download(file.file_path);

      if (error) throw error;

      if (data) {
        // Parse CSV data
        Papa.parse(data, {
          header: true,
          skipEmptyLines: true,
          complete: (result) => {
            setPreviewData(result.data.slice(0, 100) as CSVRow[]); // Limit to 100 rows
            if (result.meta.fields) {
              setHeaders(result.meta.fields);
            }
            setIsLoadingPreview(false);
          },
          error: (error) => {
            throw error;
          }
        });
      }
    } catch (error: any) {
      toast.error(`Error previewing file: ${error.message}`);
      setIsViewDialogOpen(false);
      setIsLoadingPreview(false);
    }
  };

  const handleDownload = async (file: CoordinateFile) => {
    try {
      const { data, error } = await supabase.storage
        .from('csv_files')
        .download(file.file_path);

      if (error) throw error;

      if (data) {
        // Create a download link
        const url = URL.createObjectURL(data);
        const a = document.createElement('a');
        a.href = url;
        a.download = file.file_name.endsWith('.csv') ? file.file_name : `${file.file_name}.csv`;
        document.body.appendChild(a);
        a.click();
        
        // Clean up
        setTimeout(() => {
          document.body.removeChild(a);
          URL.revokeObjectURL(url);
        }, 100);
      }
    } catch (error: any) {
      toast.error(`Error downloading file: ${error.message}`);
    }
  };

  const confirmEdit = async () => {
    if (!selectedFile) return;

    setIsUpdating(true);
    try {
      const { error } = await supabase
        .from('coordinate_files')
        .update({
          file_name: editedFileName,
          description: editedDescription
        })
        .eq('id', selectedFile.id);

      if (error) throw error;

      toast.success('File updated successfully');
      setIsEditDialogOpen(false);
      fetchFiles();
    } catch (error: any) {
      toast.error(`Error updating file: ${error.message}`);
    } finally {
      setIsUpdating(false);
    }
  };

  const confirmDelete = async () => {
    if (!selectedFile) return;

    setIsDeleting(true);
    try {
      // First delete the file from storage
      const { error: storageError } = await supabase.storage
        .from('csv_files')
        .remove([selectedFile.file_path]);

      if (storageError) throw storageError;

      // Then delete the metadata from the database
      const { error: dbError } = await supabase
        .from('coordinate_files')
        .delete()
        .eq('id', selectedFile.id);

      if (dbError) throw dbError;

      toast.success('File deleted successfully');
      setIsDeleteDialogOpen(false);
      fetchFiles();
    } catch (error: any) {
      toast.error(`Error deleting file: ${error.message}`);
    } finally {
      setIsDeleting(false);
    }
  };

  const filteredFiles = searchQuery
    ? files.filter(file => 
        file.file_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (file.description && file.description.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    : files;

  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
          <Input
            type="search"
            placeholder="Search files..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <Button
          variant="outline"
          onClick={fetchFiles}
          disabled={isLoading}
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            "Refresh"
          )}
        </Button>
      </div>

      <div className="border rounded-md overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>File Name</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Points</TableHead>
              <TableHead>Updated</TableHead>
              <TableHead className="w-[160px]">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-8">
                  <div className="flex justify-center items-center">
                    <Loader2 className="h-5 w-5 animate-spin mr-2" />
                    <span>Loading files...</span>
                  </div>
                </TableCell>
              </TableRow>
            ) : filteredFiles.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-8">
                  {searchQuery ? (
                    <span>No files match your search</span>
                  ) : (
                    <div>
                      <FileSpreadsheet className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                      <span>No coordinate files uploaded yet</span>
                    </div>
                  )}
                </TableCell>
              </TableRow>
            ) : (
              filteredFiles.map((file) => (
                <TableRow key={file.id}>
                  <TableCell className="font-medium">{file.file_name}</TableCell>
                  <TableCell className="truncate max-w-[200px]">{file.description || '-'}</TableCell>
                  <TableCell>{file.total_points.toLocaleString()}</TableCell>
                  <TableCell>{formatDistanceToNow(new Date(file.updated_at), { addSuffix: true })}</TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Button variant="ghost" size="sm" onClick={() => handleView(file)}>
                        <Eye className="h-4 w-4" />
                        <span className="sr-only">View</span>
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => handleEdit(file)}>
                        <Edit className="h-4 w-4" />
                        <span className="sr-only">Edit</span>
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => handleDownload(file)}>
                        <DownloadCloud className="h-4 w-4" />
                        <span className="sr-only">Download</span>
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => handleDelete(file)}>
                        <Trash2 className="h-4 w-4 text-red-500" />
                        <span className="sr-only">Delete</span>
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit File Details</DialogTitle>
            <DialogDescription>
              Update the name and description of your coordinate file.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div>
              <label className="font-medium text-sm">File Name</label>
              <Input 
                value={editedFileName} 
                onChange={(e) => setEditedFileName(e.target.value)} 
                className="mt-1"
              />
            </div>
            <div>
              <label className="font-medium text-sm">Description (optional)</label>
              <Textarea 
                value={editedDescription} 
                onChange={(e) => setEditedDescription(e.target.value)}
                className="mt-1"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)} disabled={isUpdating}>
              Cancel
            </Button>
            <Button onClick={confirmEdit} disabled={isUpdating}>
              {isUpdating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : 'Save Changes'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirm Deletion</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{selectedFile?.file_name}"? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDeleteDialogOpen(false)} disabled={isDeleting}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={confirmDelete} disabled={isDeleting}>
              {isDeleting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : 'Delete File'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* View File Dialog */}
      <Dialog open={isViewDialogOpen} onOpenChange={setIsViewDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle>{selectedFile?.file_name}</DialogTitle>
            <DialogDescription>
              Coordinate System: {selectedFile?.coordinate_system} • 
              Total Points: {selectedFile?.total_points.toLocaleString()}
              {selectedFile?.description && <p className="mt-2">{selectedFile.description}</p>}
            </DialogDescription>
          </DialogHeader>
          <div className="overflow-y-auto" style={{ maxHeight: 'calc(80vh - 200px)' }}>
            {isLoadingPreview ? (
              <div className="flex justify-center items-center py-12">
                <Loader2 className="h-8 w-8 animate-spin" />
              </div>
            ) : previewData.length > 0 ? (
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
                {previewData.length < (selectedFile?.total_points || 0) && (
                  <p className="text-sm text-center mt-4 text-gray-500">
                    Showing {previewData.length} of {selectedFile?.total_points} total records
                  </p>
                )}
              </div>
            ) : (
              <p className="text-center py-8 text-gray-500">No data available</p>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsViewDialogOpen(false)}>
              Close
            </Button>
            <Button onClick={() => selectedFile && handleDownload(selectedFile)}>
              <DownloadCloud className="mr-2 h-4 w-4" />
              Download
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default FileList;
