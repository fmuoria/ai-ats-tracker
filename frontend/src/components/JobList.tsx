import React from 'react';
import { Briefcase, Trash2, Calendar } from 'lucide-react';
import { JobDescription } from '@/services/api';

interface JobListProps {
  jobs: JobDescription[];
  onSelectJob: (job: JobDescription) => void;
  onDeleteJob?: (jobId: number) => void;
  selectedJobId?: number;
}

export default function JobList({ jobs, onSelectJob, onDeleteJob, selectedJobId }: JobListProps) {
  if (jobs.length === 0) {
    return (
      <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
        <Briefcase className="mx-auto h-12 w-12 text-gray-400 mb-3" />
        <p className="text-gray-600 font-medium">No job descriptions yet</p>
        <p className="text-gray-500 text-sm mt-1">Create your first job description to start matching candidates</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {jobs.map((job) => (
        <div
          key={job.id}
          className={`bg-white rounded-lg border-2 p-4 transition-all cursor-pointer hover:shadow-md ${
            selectedJobId === job.id
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-200 hover:border-primary-300'
          }`}
          onClick={() => onSelectJob(job)}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-2">
                <Briefcase className="h-5 w-5 text-primary-600" />
                <h3 className="text-lg font-semibold text-gray-900">{job.title}</h3>
              </div>
              <p className="text-sm text-gray-600 line-clamp-2 mb-2">
                {job.description_text}
              </p>
              <div className="flex items-center text-xs text-gray-500">
                <Calendar className="h-3 w-3 mr-1" />
                Created {new Date(job.created_at).toLocaleDateString()}
              </div>
            </div>
            {onDeleteJob && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  if (window.confirm('Are you sure you want to delete this job description?')) {
                    onDeleteJob(job.id);
                  }
                }}
                className="ml-4 text-red-500 hover:text-red-700 p-2 hover:bg-red-50 rounded transition-colors"
                title="Delete job"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
