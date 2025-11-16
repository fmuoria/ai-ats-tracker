import { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { Briefcase, Plus, List } from 'lucide-react';
import JobForm from '@/components/JobForm';
import JobList from '@/components/JobList';
import { jobsApi, JobDescription } from '@/services/api';

export default function JobsPage() {
  const router = useRouter();
  const [activeView, setActiveView] = useState<'list' | 'create'>('list');
  const [jobs, setJobs] = useState<JobDescription[]>([]);
  const [selectedJob, setSelectedJob] = useState<JobDescription | null>(null);
  const [loading, setLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    try {
      setLoading(true);
      const data = await jobsApi.listJobs();
      setJobs(data);
    } catch (err) {
      console.error('Error loading jobs:', err);
      setError('Failed to load job descriptions');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateJob = async (title: string, description: string) => {
    try {
      setIsSubmitting(true);
      setError(null);
      await jobsApi.createJob(title, description);
      await loadJobs();
      setActiveView('list');
      alert('Job description created successfully!');
    } catch (err: any) {
      console.error('Error creating job:', err);
      setError(err.response?.data?.detail || 'Failed to create job description');
      alert('Error: ' + (err.response?.data?.detail || 'Failed to create job description'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteJob = async (jobId: number) => {
    try {
      await jobsApi.deleteJob(jobId);
      await loadJobs();
      if (selectedJob?.id === jobId) {
        setSelectedJob(null);
      }
    } catch (err) {
      console.error('Error deleting job:', err);
      alert('Failed to delete job description');
    }
  };

  const handleSelectJob = (job: JobDescription) => {
    setSelectedJob(job);
  };

  return (
    <>
      <Head>
        <title>Job Descriptions - AI ATS Tracker</title>
        <meta name="description" content="Manage job descriptions for candidate matching" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Briefcase className="h-8 w-8 text-primary-600" />
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Job Descriptions</h1>
                  <p className="text-sm text-gray-600">Manage job postings for candidate matching</p>
                </div>
              </div>
              <div className="flex space-x-4">
                <button
                  onClick={() => router.push('/')}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors font-medium"
                >
                  Back to Dashboard
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Panel - Job List or Create Form */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                {/* Toggle Buttons */}
                <div className="flex space-x-2 mb-6">
                  <button
                    onClick={() => setActiveView('list')}
                    className={`flex-1 py-2 px-4 rounded-lg transition-colors font-medium flex items-center justify-center space-x-2 ${
                      activeView === 'list'
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    <List className="h-4 w-4" />
                    <span>Job List ({jobs.length})</span>
                  </button>
                  <button
                    onClick={() => setActiveView('create')}
                    className={`flex-1 py-2 px-4 rounded-lg transition-colors font-medium flex items-center justify-center space-x-2 ${
                      activeView === 'create'
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    <Plus className="h-4 w-4" />
                    <span>Create New</span>
                  </button>
                </div>

                {/* Content */}
                {activeView === 'list' ? (
                  <div>
                    <JobList
                      jobs={jobs}
                      onSelectJob={handleSelectJob}
                      onDeleteJob={handleDeleteJob}
                      selectedJobId={selectedJob?.id}
                    />
                  </div>
                ) : (
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900 mb-6">
                      Create Job Description
                    </h2>
                    <JobForm onSubmit={handleCreateJob} isSubmitting={isSubmitting} />
                  </div>
                )}
              </div>
            </div>

            {/* Right Panel - Job Details */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 sticky top-6">
                {selectedJob ? (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Job Details</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="text-sm font-medium text-gray-700">Title</label>
                        <p className="mt-1 text-gray-900">{selectedJob.title}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700">Description</label>
                        <p className="mt-1 text-sm text-gray-600 whitespace-pre-wrap max-h-96 overflow-y-auto">
                          {selectedJob.description_text}
                        </p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700">Created</label>
                        <p className="mt-1 text-sm text-gray-600">
                          {new Date(selectedJob.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <Briefcase className="mx-auto h-12 w-12 text-gray-400 mb-3" />
                    <p className="text-gray-600">Select a job to view details</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>
    </>
  );
}
