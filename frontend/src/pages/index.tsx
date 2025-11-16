import { useState, useEffect } from 'react';
import Head from 'next/head';
import { Users, Upload as UploadIcon, Briefcase } from 'lucide-react';
import FileUpload from '@/components/FileUpload';
import CandidateList from '@/components/CandidateList';
import CandidateDetails from '@/components/CandidateDetails';
import JobDescriptionManager from '@/components/JobDescriptionManager';
import { candidatesApi, Candidate } from '@/services/api';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'upload' | 'dashboard' | 'jobs'>('dashboard');
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  const [selectedJdId, setSelectedJdId] = useState<number | null>(null);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCandidates();
  }, []);

  const loadCandidates = async () => {
    try {
      setLoading(true);
      const data = await candidatesApi.listCandidates();
      setCandidates(data.candidates || []);
    } catch (err) {
      console.error('Error loading candidates:', err);
      setError('Failed to load candidates');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (cvFile: File, coverLetterFile?: File, jobId?: number, jobText?: string) => {
    try {
      setIsUploading(true);
      setError(null);
      
      // Upload documents with optional job matching
      const uploadResponse = await candidatesApi.uploadDocuments(cvFile, coverLetterFile, jobId, jobText);
      const candidateId = uploadResponse.candidate_id;
      
      // Analysis is now done in background, just wait a bit and reload
      setIsAnalyzing(true);
      
      // Wait a moment then reload to show processing status
      setTimeout(async () => {
        await loadCandidates();
        setIsAnalyzing(false);
      }, 2000);
      // Start analysis (with optional job description)
      setIsAnalyzing(true);
      await candidatesApi.analyzeCandidate(candidateId, selectedJdId || undefined);
      
      // Reload candidates
      await loadCandidates();
      
      // Switch to dashboard
      setActiveTab('dashboard');
      
      alert('Candidate uploaded successfully! Analysis is running in the background.');
    } catch (err: any) {
      console.error('Error uploading candidate:', err);
      setError(err.response?.data?.detail || 'Failed to upload and analyze candidate');
      alert('Error: ' + (err.response?.data?.detail || 'Failed to upload and analyze candidate'));
    } finally {
      setIsUploading(false);
    }
  };

  const handleSelectCandidate = async (candidate: Candidate) => {
    try {
      // Fetch full details
      const details = await candidatesApi.getCandidateDetails(candidate.id);
      setSelectedCandidate(details);
    } catch (err) {
      console.error('Error loading candidate details:', err);
      setError('Failed to load candidate details');
    }
  };

  return (
    <>
      <Head>
        <title>AI ATS Tracker - Applicant Tracking System</title>
        <meta name="description" content="AI-Powered Applicant Tracking System" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Users className="h-8 w-8 text-primary-600" />
                <h1 className="text-2xl font-bold text-gray-900">AI ATS Tracker</h1>
              </div>
              <div className="flex space-x-4">
                <button
                  onClick={() => {
                    setActiveTab('dashboard');
                    setSelectedCandidate(null);
                  }}
                  className={`px-4 py-2 rounded-lg transition-colors font-medium ${
                    activeTab === 'dashboard'
                      ? 'bg-primary-600 text-white'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  Dashboard
                </button>
                <button
                  onClick={() => window.location.href = '/jobs'}
                  className="px-4 py-2 rounded-lg transition-colors font-medium text-gray-600 hover:bg-gray-100"
                >
                  Jobs
                </button>
                <button
                  onClick={() => {
                    setActiveTab('jobs');
                    setSelectedCandidate(null);
                  }}
                  className={`px-4 py-2 rounded-lg transition-colors font-medium flex items-center space-x-2 ${
                    activeTab === 'jobs'
                      ? 'bg-primary-600 text-white'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Briefcase className="h-4 w-4" />
                  <span>Job Descriptions</span>
                </button>
                <button
                  onClick={() => {
                    setActiveTab('upload');
                    setSelectedCandidate(null);
                  }}
                  className={`px-4 py-2 rounded-lg transition-colors font-medium flex items-center space-x-2 ${
                    activeTab === 'upload'
                      ? 'bg-primary-600 text-white'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <UploadIcon className="h-4 w-4" />
                  <span>Upload Candidate</span>
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

          {isAnalyzing && (
            <div className="mb-4 bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded">
              Analyzing candidate... This may take a minute.
            </div>
          )}

          {selectedCandidate ? (
            <CandidateDetails
              candidate={selectedCandidate}
              onBack={() => setSelectedCandidate(null)}
            />
          ) : activeTab === 'jobs' ? (
            <div className="max-w-4xl mx-auto">
              <JobDescriptionManager 
                selectedJdId={selectedJdId}
                onSelectJd={setSelectedJdId}
                onJobDescriptionCreated={() => {
                  // Optionally refresh or do something
                }}
              />
              {selectedJdId && (
                <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-blue-800">
                    <strong>Selected Job Description ID: {selectedJdId}</strong>
                    <br />
                    New candidates will be analyzed against this job description.
                  </p>
                </div>
              )}
            </div>
          ) : activeTab === 'upload' ? (
            <div className="max-w-2xl mx-auto">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-6">
                  Upload Candidate Documents
                </h2>
                {selectedJdId && (
                  <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-sm text-green-800">
                      <strong>Job Description Selected:</strong> ID {selectedJdId}
                      <br />
                      <span className="text-xs">This candidate will be analyzed against the selected job description.</span>
                    </p>
                  </div>
                )}
                <FileUpload onUpload={handleUpload} isUploading={isUploading || isAnalyzing} />
              </div>
            </div>
          ) : (
            <div>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900">
                  Candidates ({candidates.length})
                </h2>
                <button
                  onClick={loadCandidates}
                  disabled={loading}
                  className="text-primary-600 hover:text-primary-700 font-medium text-sm"
                >
                  {loading ? 'Loading...' : 'Refresh'}
                </button>
              </div>
              <CandidateList
                candidates={candidates}
                onSelectCandidate={handleSelectCandidate}
              />
            </div>
          )}
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <p className="text-center text-sm text-gray-600">
              AI-Powered ATS Tracker © 2024
            </p>
          </div>
        </footer>
      </div>
    </>
  );
}
