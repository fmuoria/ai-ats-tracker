import React, { useState } from 'react';
import { Briefcase } from 'lucide-react';

interface JobFormProps {
  onSubmit: (title: string, description: string) => void;
  isSubmitting: boolean;
}

export default function JobForm({ onSubmit, isSubmitting }: JobFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim() && description.trim()) {
      onSubmit(title, description);
      setTitle('');
      setDescription('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
          Job Title *
        </label>
        <input
          type="text"
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="e.g., Senior Software Engineer"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          required
          disabled={isSubmitting}
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
          Job Description *
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Paste the full job description here..."
          rows={12}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-vertical"
          required
          disabled={isSubmitting}
        />
        <p className="mt-1 text-xs text-gray-500">
          Include responsibilities, requirements, and qualifications for better matching
        </p>
      </div>

      <button
        type="submit"
        disabled={!title.trim() || !description.trim() || isSubmitting}
        className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium flex items-center justify-center space-x-2"
      >
        <Briefcase className="h-5 w-5" />
        <span>{isSubmitting ? 'Creating...' : 'Create Job Description'}</span>
      </button>
    </form>
  );
}
