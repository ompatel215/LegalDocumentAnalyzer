import React, { useCallback, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import {
  DocumentArrowUpIcon,
  DocumentTextIcon,
  XCircleIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';

const DocumentUpload: React.FC = () => {
  const navigate = useNavigate();
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [error, setError] = useState<string>('');
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'processing' | 'success' | 'error'>('idle');

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setSelectedFile(file);
    setIsUploading(true);
    setError('');
    setUploadProgress(0);
    setUploadStatus('uploading');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const token = localStorage.getItem('token');
      setUploadStatus('uploading');
      const response = await axios.post(
        '/api/v1/documents/upload',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            Authorization: `Bearer ${token}`,
          },
          onUploadProgress: (progressEvent) => {
            const progress = progressEvent.loaded / (progressEvent.total ?? 0) * 100;
            setUploadProgress(Math.round(progress));
          },
        }
      );

      setUploadStatus('success');
      // Navigate to the analysis page for the uploaded document
      setTimeout(() => {
        navigate(`/analysis/${response.data.id}`);
      }, 1000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload document');
      setUploadStatus('error');
    } finally {
      setIsUploading(false);
    }
  }, [navigate]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg'],
    },
    maxFiles: 1,
    multiple: false,
  });

  const getStatusDisplay = () => {
    switch (uploadStatus) {
      case 'uploading':
        return (
          <div className="mt-4">
            <div className="relative pt-1">
              <div className="flex mb-2 items-center justify-between">
                <div>
                  <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-indigo-600 bg-indigo-200">
                    Uploading
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-xs font-semibold inline-block text-indigo-600">
                    {uploadProgress}%
                  </span>
                </div>
              </div>
              <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-indigo-200">
                <div
                  style={{ width: `${uploadProgress}%` }}
                  className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-indigo-500 transition-all duration-300"
                />
              </div>
            </div>
          </div>
        );
      case 'processing':
        return (
          <div className="mt-4 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mx-auto"></div>
            <p className="mt-2 text-sm text-gray-600">Processing document...</p>
          </div>
        );
      case 'success':
        return (
          <div className="mt-4 text-center text-green-600">
            <CheckCircleIcon className="h-8 w-8 mx-auto" />
            <p className="mt-2">Upload successful! Redirecting to analysis...</p>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Upload Document</h1>
        <p className="mt-2 text-sm text-gray-600">
          Upload your legal document for analysis. Supported formats: PDF, DOCX, TXT, PNG, JPG
        </p>
      </div>

      <div
        {...getRootProps()}
        className={`mt-4 flex justify-center px-6 pt-5 pb-6 border-2 border-dashed rounded-lg ${
          isDragActive
            ? 'border-indigo-500 bg-indigo-50'
            : 'border-gray-300 hover:border-indigo-500'
        }`}
      >
        <div className="space-y-1 text-center">
          <input {...getInputProps()} />
          <div className="flex justify-center">
            {selectedFile ? (
              <DocumentTextIcon className="h-12 w-12 text-indigo-500" />
            ) : (
              <DocumentArrowUpIcon className="h-12 w-12 text-gray-400" />
            )}
          </div>
          <div className="flex text-sm text-gray-600">
            {selectedFile ? (
              <div className="flex items-center space-x-2">
                <span>{selectedFile.name}</span>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedFile(null);
                    setUploadStatus('idle');
                  }}
                  className="text-red-500 hover:text-red-700"
                >
                  <XCircleIcon className="h-5 w-5" />
                </button>
              </div>
            ) : (
              <div>
                <span className="text-indigo-600 hover:text-indigo-500">
                  Click to upload
                </span>{' '}
                or drag and drop
              </div>
            )}
          </div>
        </div>
      </div>

      {getStatusDisplay()}

      {error && (
        <div className="mt-4 bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <XCircleIcon className="h-5 w-5 text-red-400" aria-hidden="true" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Upload failed</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload; 