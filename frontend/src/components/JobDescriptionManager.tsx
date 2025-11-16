import { useState, useEffect } from 'react';
import { Briefcase, Upload, Trash2, FileText } from 'lucide-react';

interface JobDescription {
  id: number;
  title: string;
  description_preview: string;
  has_embedding: boolean;
  created_at: string;
}

interface JobDescriptionManagerProps {
  onJobDescriptionCreated?: () => void;
  selectedJdId?: number | null;
  onSelectJd?: (jdId: number | null) => void;
}

export default function JobDescriptionManager({
  onJobDescriptionCreated,
  selectedJdId,
  onSelectJd
}: JobDescriptionManagerProps) {
  const [jobDescriptions, setJobDescriptions] = useState<JobDescription[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Form state
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState('');
  const [descriptionText, setDescriptionText] = useState('');
  const [descriptionFile, setDescriptionFile] = useState<File | null>(null);

  useEffect(() => {
    loadJobDescriptions();
  }, []);

  const loadJobDescriptions = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/job-descriptions/');
      const data = await response.json();
      setJobDescriptions(data.job_descriptions || []);
    } catch (err) {
      console.error('Error loading job descriptions:', err);
      setError('Failed to load job descriptions');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!title.trim()) {
      setError('Title is required');
      return;
    }
    
    if (!descriptionText.trim() && !descriptionFile) {
      setError('Either description text or file is required');
      return;
    }

    try {
      setUploading(true);
      setError(null);

      const formData = new FormData();
      formData.append('title', title);
      
      if (descriptionFile) {
        formData.append('description_file', descriptionFile);
      } else {
        formData.append('description_text', descriptionText);
      }

      const response = await fetch('http://localhost:8000/api/job-descriptions/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to create job description');
      }

      // Reset form
      setTitle('');
      setDescriptionText('');
      setDescriptionFile(null);
      setShowForm(false);

      // Reload list
      await loadJobDescriptions();
      
      if (onJobDescriptionCreated) {
        onJobDescriptionCreated();
      }

      alert('Job description created successfully!');
    } catch (err: any) {
      console.error('Error creating job description:', err);
      setError(err.message || 'Failed to create job description');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this job description?')) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/job-descriptions/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete job description');
      }

      await loadJobDescriptions();
      
      if (selectedJdId === id && onSelectJd) {
        onSelectJd(null);
      }
    } catch (err) {
      console.error('Error deleting job description:', err);
      setError('Failed to delete job description');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Briefcase className="h-6 w-6 text-primary-600" />
          <h2 className="text-xl font-semibold text-gray-900">Job Descriptions</h2>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Upload className="h-4 w-4" />
          <span>Add Job Description</span>
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {showForm && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold mb-4">Create Job Description</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Job Title *
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="e.g., Senior Software Engineer"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description Text
              </label>
              <textarea
                value={descriptionText}
                onChange={(e) => setDescriptionText(e.target.value)}
                rows={8}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Paste job description here..."
              />
            </div>

            <div className="text-center text-gray-500 text-sm">OR</div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Upload File (PDF, DOCX, TXT)
              </label>
              <input
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={(e) => setDescriptionFile(e.target.files?.[0] || null)}
                className="w-full"
              />
              {descriptionFile && (
                <p className="mt-2 text-sm text-gray-600">
                  Selected: {descriptionFile.name}
                </p>
              )}
            </div>

            <div className="flex space-x-3">
              <button
                type="submit"
                disabled={uploading}
                className="flex-1 bg-primary-600 text-white py-2 px-4 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {uploading ? 'Creating...' : 'Create Job Description'}
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading job descriptions...</p>
        </div>
      ) : jobDescriptions.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
          <Briefcase className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No job descriptions yet</p>
          <p className="text-sm text-gray-500 mt-2">Create one to start matching candidates</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {jobDescriptions.map((jd) => (
            <div
              key={jd.id}
              className={`bg-white rounded-lg shadow-sm border p-4 hover:shadow-md transition-shadow cursor-pointer ${
                selectedJdId === jd.id ? 'border-primary-500 ring-2 ring-primary-200' : 'border-gray-200'
              }`}
              onClick={() => onSelectJd && onSelectJd(jd.id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <FileText className="h-5 w-5 text-primary-600" />
                    <h3 className="font-semibold text-gray-900">{jd.title}</h3>
                    {jd.has_embedding && (
                      <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                        Ready
                      </span>
                    )}
                  </div>
                  <p className="mt-2 text-sm text-gray-600 line-clamp-2">
                    {jd.description_preview}
                  </p>
                  <p className="mt-2 text-xs text-gray-500">
                    Created: {new Date(jd.created_at).toLocaleDateString()}
                  </p>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(jd.id);
                  }}
                  className="ml-4 p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  title="Delete"
                >
                  <Trash2 className="h-5 w-5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
