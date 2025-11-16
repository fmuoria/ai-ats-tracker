import React from 'react';
import {
  User,
  Mail,
  Phone,
  Linkedin,
  FileText,
  TrendingUp,
  CheckCircle,
  XCircle,
  AlertCircle,
  ArrowLeft,
} from 'lucide-react';
import { Candidate } from '../services/api';

interface CandidateDetailsProps {
  candidate: Candidate;
  onBack: () => void;
}

export default function CandidateDetails({ candidate, onBack }: CandidateDetailsProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={onBack}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <h2 className="text-2xl font-bold text-gray-900">Candidate Report</h2>
      </div>

      {/* Overall Score */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-primary-50 mb-4">
            <span className={`text-4xl font-bold ${getScoreColor(candidate.final_score || candidate.overall_score || 0)}`}>
              {(candidate.final_score || candidate.overall_score)?.toFixed(0) || 0}
            </span>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            {candidate.final_score ? 'Final Score (Job-Aware)' : 'Overall Score'}
          </h3>
          <div className="flex flex-wrap justify-center gap-4 text-sm">
            <div>
              <span className="text-gray-600">CV Score:</span>
              <span className="ml-2 font-semibold">{candidate.cv_score?.toFixed(0) || 0}/60</span>
            </div>
            {candidate.cover_letter_score !== null && (
              <div>
                <span className="text-gray-600">Cover Letter:</span>
                <span className="ml-2 font-semibold">
                  {candidate.cover_letter_score?.toFixed(0) || 0}/40
                </span>
              </div>
            )}
            {candidate.jd_match_score !== null && candidate.jd_match_score !== undefined && (
              <div>
                <span className="text-gray-600">JD Match:</span>
                <span className="ml-2 font-semibold">
                  {candidate.jd_match_score?.toFixed(0) || 0}%
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Job Match Section */}
      {candidate.jd_id && (candidate.matched_skills || candidate.missing_skills) && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <TrendingUp className="h-5 w-5 mr-2" />
            Job Description Match Analysis
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Matched Skills */}
            {candidate.matched_skills && candidate.matched_skills.length > 0 && (
              <div>
                <div className="flex items-center mb-3">
                  <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
                  <h4 className="font-semibold text-green-700">Matched Skills</h4>
                </div>
                <div className="flex flex-wrap gap-2">
                  {candidate.matched_skills.map((skill, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Missing Skills */}
            {candidate.missing_skills && candidate.missing_skills.length > 0 && (
              <div>
                <div className="flex items-center mb-3">
                  <AlertCircle className="h-5 w-5 text-orange-600 mr-2" />
                  <h4 className="font-semibold text-orange-700">Missing Skills</h4>
                </div>
                <div className="flex flex-wrap gap-2">
                  {candidate.missing_skills.map((skill, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          {candidate.jd_match_score !== null && candidate.jd_match_score !== undefined && (
            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>Semantic Similarity Score:</strong> {candidate.jd_match_score.toFixed(1)}%
                <br />
                <span className="text-xs text-blue-600">
                  This score represents how well the candidate's resume semantically matches the job description using AI embeddings.
                </span>
              </p>
            </div>
          )}
        </div>
      )}

      {/* Candidate Summary */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <User className="h-5 w-5 mr-2" />
          Candidate Summary
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <span className="text-sm text-gray-600">Name:</span>
            <p className="font-medium">{candidate.name || 'N/A'}</p>
          </div>
          {candidate.email && (
            <div>
              <span className="text-sm text-gray-600">Email:</span>
              <p className="font-medium flex items-center">
                <Mail className="h-4 w-4 mr-1" />
                {candidate.email}
              </p>
            </div>
          )}
          {candidate.phone && (
            <div>
              <span className="text-sm text-gray-600">Phone:</span>
              <p className="font-medium flex items-center">
                <Phone className="h-4 w-4 mr-1" />
                {candidate.phone}
              </p>
            </div>
          )}
          {candidate.linkedin_url && (
            <div>
              <span className="text-sm text-gray-600">LinkedIn:</span>
              <p className="font-medium flex items-center">
                <Linkedin className="h-4 w-4 mr-1" />
                <a
                  href={candidate.linkedin_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:underline"
                >
                  Profile
                </a>
              </p>
            </div>
          )}
        </div>
      </div>

      {/* CV Analysis */}
      {candidate.cv_analysis && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <FileText className="h-5 w-5 mr-2" />
            CV Analysis
          </h3>

          {candidate.cv_analysis.breakdown && (
            <div className="mb-4">
              <h4 className="font-medium text-gray-700 mb-2">Score Breakdown:</h4>
              <div className="space-y-2">
                {Object.entries(candidate.cv_analysis.breakdown).map(([key, value]) => (
                  <div key={key} className="flex justify-between text-sm">
                    <span className="text-gray-600 capitalize">
                      {key.replace(/_/g, ' ')}:
                    </span>
                    <span className="font-medium">{value as number}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {candidate.cv_analysis.strengths && candidate.cv_analysis.strengths.length > 0 && (
            <div className="mb-4">
              <h4 className="font-medium text-gray-700 mb-2 flex items-center">
                <CheckCircle className="h-4 w-4 mr-1 text-green-600" />
                Strengths:
              </h4>
              <ul className="list-disc list-inside space-y-1">
                {candidate.cv_analysis.strengths.map((strength: string, idx: number) => (
                  <li key={idx} className="text-sm text-gray-600">
                    {strength}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {candidate.cv_analysis.areas_for_improvement &&
            candidate.cv_analysis.areas_for_improvement.length > 0 && (
              <div className="mb-4">
                <h4 className="font-medium text-gray-700 mb-2 flex items-center">
                  <AlertCircle className="h-4 w-4 mr-1 text-yellow-600" />
                  Areas for Improvement:
                </h4>
                <ul className="list-disc list-inside space-y-1">
                  {candidate.cv_analysis.areas_for_improvement.map(
                    (area: string, idx: number) => (
                      <li key={idx} className="text-sm text-gray-600">
                        {area}
                      </li>
                    )
                  )}
                </ul>
              </div>
            )}

          {candidate.cv_analysis.summary && (
            <div className="bg-gray-50 rounded p-3">
              <p className="text-sm text-gray-700">{candidate.cv_analysis.summary}</p>
            </div>
          )}
        </div>
      )}

      {/* Cover Letter Analysis */}
      {candidate.cover_letter_analysis && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <FileText className="h-5 w-5 mr-2" />
            Cover Letter Analysis
          </h3>

          {candidate.cover_letter_analysis.breakdown && (
            <div className="mb-4">
              <h4 className="font-medium text-gray-700 mb-2">Score Breakdown:</h4>
              <div className="space-y-2">
                {Object.entries(candidate.cover_letter_analysis.breakdown).map(
                  ([key, value]) => (
                    <div key={key} className="flex justify-between text-sm">
                      <span className="text-gray-600 capitalize">
                        {key.replace(/_/g, ' ')}:
                      </span>
                      <span className="font-medium">{value as number}</span>
                    </div>
                  )
                )}
              </div>
            </div>
          )}

          {candidate.cover_letter_analysis.summary && (
            <div className="bg-gray-50 rounded p-3">
              <p className="text-sm text-gray-700">{candidate.cover_letter_analysis.summary}</p>
            </div>
          )}
        </div>
      )}

      {/* Online Presence */}
      {candidate.online_presence && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <TrendingUp className="h-5 w-5 mr-2" />
            Online Presence
          </h3>
          <div className="space-y-3 text-sm">
            {candidate.online_presence.search_attempted && (
              <div className="bg-blue-50 border border-blue-200 rounded p-3">
                <p className="text-gray-700">{candidate.online_presence.recommendation}</p>
                {candidate.online_presence.note && (
                  <p className="text-gray-600 text-xs mt-1">{candidate.online_presence.note}</p>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Social Media Presence */}
      {candidate.social_media_presence && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Social Media Presence</h3>
          <div className="space-y-2 text-sm">
            {candidate.social_media_presence.results?.map((result: any, idx: number) => (
              <div key={idx} className="flex items-center justify-between py-2 border-b">
                <span className="font-medium capitalize">{result.platform}</span>
                <span className="text-gray-600">{result.status.replace(/_/g, ' ')}</span>
              </div>
            ))}
            {candidate.social_media_presence.note && (
              <p className="text-gray-600 text-xs mt-3">
                {candidate.social_media_presence.note}
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
