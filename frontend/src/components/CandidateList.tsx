import React from 'react';
import { User, Mail, Calendar, TrendingUp } from 'lucide-react';
import { Candidate } from '../services/api';

interface CandidateListProps {
  candidates: Candidate[];
  onSelectCandidate: (candidate: Candidate) => void;
}

export default function CandidateList({ candidates, onSelectCandidate }: CandidateListProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'processing':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-4">
      {candidates.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <User className="mx-auto h-12 w-12 text-gray-400 mb-3" />
          <p>No candidates yet. Upload a CV to get started!</p>
        </div>
      ) : (
        candidates.map((candidate) => (
          <div
            key={candidate.id}
            onClick={() => onSelectCandidate(candidate)}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <User className="h-5 w-5 text-gray-400" />
                  <h3 className="font-semibold text-lg text-gray-900">
                    {candidate.name || 'Unknown Candidate'}
                  </h3>
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(
                      candidate.processing_status
                    )}`}
                  >
                    {candidate.processing_status}
                  </span>
                </div>

                <div className="flex items-center space-x-4 text-sm text-gray-600 mb-2">
                  {candidate.email && (
                    <div className="flex items-center space-x-1">
                      <Mail className="h-4 w-4" />
                      <span>{candidate.email}</span>
                    </div>
                  )}
                  <div className="flex items-center space-x-1">
                    <Calendar className="h-4 w-4" />
                    <span>{new Date(candidate.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>

              {candidate.overall_score !== null && candidate.overall_score !== undefined && (
                <div className="text-right">
                  <div className="flex items-center space-x-1 mb-1">
                    <TrendingUp className="h-4 w-4 text-gray-400" />
                    <span className="text-xs text-gray-500">Score</span>
                  </div>
                  <div
                    className={`text-3xl font-bold ${getScoreColor(candidate.overall_score)}`}
                  >
                    {candidate.overall_score.toFixed(0)}
                  </div>
                  <div className="text-xs text-gray-500">out of 100</div>
                </div>
              )}
            </div>
          </div>
        ))
      )}
    </div>
  );
}
