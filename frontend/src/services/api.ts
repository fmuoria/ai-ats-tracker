import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Candidate {
  id: number;
  name: string;
  email: string;
  phone?: string;
  linkedin_url?: string;
  overall_score?: number;
  cv_score?: number;
  cover_letter_score?: number;
  processing_status: string;
  created_at: string;
  jd_match_score?: number | null;
  jd_id?: number | null;
  matched_skills?: Record<string, any> | null;
  missing_skills?: Record<string, any> | null;
  cv_analysis?: any;
  cover_letter_analysis?: any;
  online_presence?: any;
  social_media_presence?: any;
  work_verification?: any;
}

export const candidatesApi = {
  uploadDocuments: async (cvFile: File, coverLetterFile?: File, jobId?: number, adhocJobText?: string) => {
    const formData = new FormData();
    formData.append('cv_file', cvFile);
    if (coverLetterFile) {
      formData.append('cover_letter_file', coverLetterFile);
    }
    if (typeof jobId !== 'undefined' && jobId !== null) {
      formData.append('job_id', String(jobId));
    }
    if (adhocJobText) {
      formData.append('job_text', adhocJobText);
    }

    const response = await api.post('/api/candidates/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  analyzeCandidate: async (candidateId: number) => {
    const response = await api.post(`/api/candidates/${candidateId}/analyze`);
    return response.data;
  },

  listCandidates: async () => {
    const response = await api.get('/api/candidates/');
    return response.data;
  },

  getCandidateDetails: async (candidateId: number) => {
    const response = await api.get(`/api/candidates/${candidateId}`);
    return response.data;
  },

  deleteCandidate: async (candidateId: number) => {
    const response = await api.delete(`/api/candidates/${candidateId}`);
    return response.data;
  },

  triggerMatch: async (candidateId: number, jobId?: number, adhocJobText?: string) => {
    const payload: any = {};
    if (typeof jobId !== 'undefined') payload.job_id = jobId;
    if (adhocJobText) payload.job_text = adhocJobText;
    const response = await api.post(`/api/candidates/${candidateId}/match`, payload);
    return response.data;
  },
};
