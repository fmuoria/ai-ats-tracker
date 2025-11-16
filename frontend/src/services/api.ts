import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface JobDescription {
  id: number;
  title: string;
  description_text: string;
  created_at: string;
  updated_at?: string;
}

export interface Candidate {
  id: number;
  name: string;
  email: string;
  phone?: string;
  linkedin_url?: string;
  jd_id?: number;
  jd_match_score?: number;
  matched_skills?: string[];
  missing_skills?: string[];
  overall_score?: number;
  cv_score?: number;
  cover_letter_score?: number;
  final_score?: number;
  processing_status: string;
  created_at: string;
  cv_analysis?: any;
  cover_letter_analysis?: any;
  online_presence?: any;
  social_media_presence?: any;
  work_verification?: any;
}

export const jobsApi = {
  createJob: async (title: string, description: string) => {
    const response = await api.post('/api/jobs/', {
      title,
      description_text: description,
    });
    return response.data;
  },

  listJobs: async () => {
    const response = await api.get('/api/jobs/');
    return response.data;
  },

  getJob: async (jobId: number) => {
    const response = await api.get(`/api/jobs/${jobId}`);
    return response.data;
  },

  deleteJob: async (jobId: number) => {
    const response = await api.delete(`/api/jobs/${jobId}`);
    return response.data;
  },
};

export const candidatesApi = {
  uploadDocuments: async (
    cvFile: File, 
    coverLetterFile?: File,
    jobId?: number,
    jobText?: string
  ) => {
    const formData = new FormData();
    formData.append('cv_file', cvFile);
    if (coverLetterFile) {
      formData.append('cover_letter_file', coverLetterFile);
    }
    if (jobId) {
      formData.append('job_id', jobId.toString());
    }
    if (jobText) {
      formData.append('job_text', jobText);
    }

    const response = await api.post('/api/candidates/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  matchCandidateToJob: async (candidateId: number, jobId?: number, jobText?: string) => {
    const formData = new FormData();
    if (jobId) {
      formData.append('job_id', jobId.toString());
    }
    if (jobText) {
      formData.append('job_text', jobText);
    }

    const response = await api.post(`/api/candidates/${candidateId}/match`, formData, {
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
};

export default api;
