import React, { useCallback, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X, Briefcase } from 'lucide-react';
import { jobsApi, JobDescription } from '@/services/api';

interface FileUploadProps {
  onUpload: (cvFile: File, coverLetterFile?: File, jobId?: number, jobText?: string) => void;
  isUploading: boolean;
}

export default function FileUpload({ onUpload, isUploading }: FileUploadProps) {
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [coverLetterFile, setCoverLetterFile] = useState<File | null>(null);
  const [jobs, setJobs] = useState<JobDescription[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<number | undefined>(undefined);
  const [adHocJobText, setAdHocJobText] = useState<string>('');
  const [useAdHocJob, setUseAdHocJob] = useState<boolean>(false);

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    try {
      const data = await jobsApi.listJobs();
      setJobs(data);
    } catch (err) {
      console.error('Error loading jobs:', err);
    }
  };

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
      const jobId = useAdHocJob ? undefined : selectedJobId;
      const jobText = useAdHocJob && adHocJobText.trim() ? adHocJobText : undefined;
      onUpload(cvFile, coverLetterFile || undefined, jobId, jobText);
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

      {/* Job Selection */}
      <div className="border-t pt-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Job Description for Matching (Optional)
        </label>
        
        <div className="space-y-4">
          {/* Job Dropdown */}
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <input
                type="radio"
                id="use-existing-job"
                checked={!useAdHocJob}
                onChange={() => setUseAdHocJob(false)}
                disabled={isUploading}
                className="h-4 w-4 text-primary-600"
              />
              <label htmlFor="use-existing-job" className="text-sm text-gray-700">
                Select from existing jobs
              </label>
            </div>
            <select
              value={selectedJobId || ''}
              onChange={(e) => setSelectedJobId(e.target.value ? Number(e.target.value) : undefined)}
              disabled={useAdHocJob || isUploading}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              <option value="">-- No job selected --</option>
              {jobs.map((job) => (
                <option key={job.id} value={job.id}>
                  {job.title}
                </option>
              ))}
            </select>
          </div>

          {/* Ad-hoc Job Text */}
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <input
                type="radio"
                id="use-adhoc-job"
                checked={useAdHocJob}
                onChange={() => setUseAdHocJob(true)}
                disabled={isUploading}
                className="h-4 w-4 text-primary-600"
              />
              <label htmlFor="use-adhoc-job" className="text-sm text-gray-700">
                Paste job description
              </label>
            </div>
            <textarea
              value={adHocJobText}
              onChange={(e) => setAdHocJobText(e.target.value)}
              disabled={!useAdHocJob || isUploading}
              placeholder="Paste job description text here for one-time matching..."
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100 disabled:cursor-not-allowed resize-vertical"
            />
          </div>
        </div>

        <p className="mt-2 text-xs text-gray-500">
          Selecting a job will compute matching scores and identify skills gaps
        </p>
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
