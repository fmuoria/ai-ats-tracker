import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X } from 'lucide-react';

interface FileUploadProps {
  onUpload: (cvFile: File, coverLetterFile?: File) => void;
  isUploading: boolean;
}

export default function FileUpload({ onUpload, isUploading }: FileUploadProps) {
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [coverLetterFile, setCoverLetterFile] = useState<File | null>(null);

  const onCvDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setCvFile(acceptedFiles[0]);
    }
  }, []);

  const onCoverLetterDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setCoverLetterFile(acceptedFiles[0]);
    }
  }, []);

  const cvDropzone = useDropzone({
    onDrop: onCvDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
    disabled: isUploading,
  });

  const coverLetterDropzone = useDropzone({
    onDrop: onCoverLetterDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
    disabled: isUploading,
  });

  const handleSubmit = () => {
    if (cvFile) {
      onUpload(cvFile, coverLetterFile || undefined);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          CV/Resume (Required) *
        </label>
        <div
          {...cvDropzone.getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            cvDropzone.isDragActive
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-300 hover:border-primary-400'
          } ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input {...cvDropzone.getInputProps()} />
          <Upload className="mx-auto h-12 w-12 text-gray-400 mb-3" />
          {cvFile ? (
            <div className="flex items-center justify-center space-x-2">
              <File className="h-5 w-5 text-primary-600" />
              <span className="text-sm text-gray-700">{cvFile.name}</span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setCvFile(null);
                }}
                className="text-red-500 hover:text-red-700"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <div>
              <p className="text-sm text-gray-600">
                Drag & drop CV here, or click to select
              </p>
              <p className="text-xs text-gray-500 mt-1">PDF, DOCX, or TXT</p>
            </div>
          )}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Cover Letter (Optional)
        </label>
        <div
          {...coverLetterDropzone.getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            coverLetterDropzone.isDragActive
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-300 hover:border-primary-400'
          } ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input {...coverLetterDropzone.getInputProps()} />
          <Upload className="mx-auto h-12 w-12 text-gray-400 mb-3" />
          {coverLetterFile ? (
            <div className="flex items-center justify-center space-x-2">
              <File className="h-5 w-5 text-primary-600" />
              <span className="text-sm text-gray-700">{coverLetterFile.name}</span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setCoverLetterFile(null);
                }}
                className="text-red-500 hover:text-red-700"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <div>
              <p className="text-sm text-gray-600">
                Drag & drop cover letter here, or click to select
              </p>
              <p className="text-xs text-gray-500 mt-1">PDF, DOCX, or TXT</p>
            </div>
          )}
        </div>
      </div>

      <button
        onClick={handleSubmit}
        disabled={!cvFile || isUploading}
        className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
      >
        {isUploading ? 'Uploading...' : 'Upload & Analyze Candidate'}
      </button>
    </div>
  );
}
