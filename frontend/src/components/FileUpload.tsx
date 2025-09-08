import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileImage, AlertCircle, CheckCircle } from 'lucide-react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  isUploading?: boolean;
  error?: string | null;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileSelect, isUploading = false, error = null }) => {
  const [dragActive, setDragActive] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles[0]);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png'],
      'application/pdf': ['.pdf']
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
    onDragEnter: () => setDragActive(true),
    onDragLeave: () => setDragActive(false),
  });

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors duration-200
          ${isDragReject || error
            ? 'border-red-300 bg-red-50 text-red-600'
            : dragActive
            ? 'border-primary-400 bg-primary-50 text-primary-600'
            : 'border-secondary-300 bg-white text-secondary-600 hover:border-primary-400 hover:bg-primary-50'
          }
          ${isUploading ? 'pointer-events-none opacity-50' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center">
          {isUploading ? (
            <>
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mb-4"></div>
              <p className="text-lg font-medium">Processing receipt...</p>
              <p className="text-sm text-secondary-500 mt-1">Please wait while we extract the data</p>
            </>
          ) : error ? (
            <>
              <AlertCircle className="h-12 w-12 text-red-500 mb-4" />
              <p className="text-lg font-medium text-red-600">Upload failed</p>
              <p className="text-sm text-red-500 mt-1">{error}</p>
            </>
          ) : (
            <>
              <FileImage className="h-12 w-12 text-secondary-400 mb-4" />
              <p className="text-lg font-medium">
                {dragActive ? 'Drop the receipt here' : 'Drag & drop a receipt here'}
              </p>
              <p className="text-sm text-secondary-500 mt-1">
                or click to select a file
              </p>
              <p className="text-xs text-secondary-400 mt-2">
                Supports JPG, PNG, PDF (max 10MB)
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default FileUpload;
