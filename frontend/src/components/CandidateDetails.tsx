import React from 'react';
import { Candidate } from '@/services/api';

interface Props {
  candidate: Candidate;
  onBack: () => void;
}

const CandidateDetails: React.FC<Props> = ({ candidate, onBack }) => {
  const {
    name,
    email,
    phone,
    overall_score,
    cv_score,
    jd_match_score,
    final_score,
    matched_skills,
    missing_skills,
    cv_analysis,
    processing_status,
  } = candidate as any; // keep flexible; real types are in api.ts

  return (
    <div className="max-w-4xl mx-auto">
      <button onClick={onBack} className="text-primary-600 mb-4">← Back</button>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-xl font-semibold mb-2">Candidate Report</h2>
        <div className="flex items-center space-x-6">
          <div className="text-4xl font-bold text-red-600">{overall_score ?? '—'}</div>
          <div>
            <div className="text-sm text-gray-500">Overall Score</div>
            <div className="text-sm text-gray-500">CV Score: {cv_score ?? '—'}</div>
            <div className="text-sm text-gray-500">JD Match: {jd_match_score ?? '—'}</div>
            {typeof final_score !== 'undefined' && final_score !== null && (
              <div className="text-sm text-gray-700">Final Score: {final_score}</div>
            )}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h3 className="font-semibold mb-2">Candidate Summary</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-xs text-gray-500">Name</div>
            <div className="font-medium">{name}</div>
          </div>
          <div>
            <div className="text-xs text-gray-500">Email</div>
            <div className="font-medium">{email}</div>
          </div>
          <div>
            <div className="text-xs text-gray-500">Phone</div>
            <div className="font-medium">{phone}</div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h3 className="font-semibold mb-2">CV Analysis</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-sm text-gray-600">Matched Skills</div>
            {matched_skills && Array.isArray(matched_skills) ? (
              <ul className="list-disc ml-5">
                {matched_skills.map((s: string, i: number) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            ) : (
              <div className="text-sm text-gray-500">No matched skills or not computed yet</div>
            )}
          </div>
          <div>
            <div className="text-sm text-gray-600">Missing Skills</div>
            {missing_skills && Array.isArray(missing_skills) ? (
              <ul className="list-disc ml-5">
                {missing_skills.map((s: string, i: number) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            ) : (
              <div className="text-sm text-gray-500">No missing skills or not computed yet</div>
            )}
          </div>
        </div>

        <div className="mt-4">
          <h4 className="font-medium">AI Notes</h4>
          {cv_analysis ? (
            <pre className="bg-gray-50 p-3 rounded text-sm overflow-auto">{JSON.stringify(cv_analysis, null, 2)}</pre>
          ) : (
            <div className="text-sm text-gray-500">Analysis not available yet{processing_status === 'pending_analysis' ? ' (pending)' : ''}</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CandidateDetails;
