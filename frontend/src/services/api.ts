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
  jd_id?: number;
  jd_match_score?: number;
  matched_skills?: string[];
  missing_skills?: string[];
  final_score?: number;
  processing_status: string;
  created_at: string;
  cv_analysis?: any;
  cover_letter_analysis?: any;
  online_presence?: any;
  social_media_presence?: any;
  work_verification?: any;
}

export interface JobDescription {
  id: number;
  title: string;
  description_text: string;
  created_at: string;
}

export const candidatesApi = {
  uploadDocuments: async (cvFile: File, coverLetterFile?: File) => {
    const formData = new FormData();
    formData.append('cv_file', cvFile);
    if (coverLetterFile) {
      formData.append('cover_letter_file', coverLetterFile);
    }

    const response = await api.post('/api/candidates/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  analyzeCandidate: async (candidateId: number, jdId?: number) => {
    const url = jdId 
      ? `/api/candidates/${candidateId}/analyze?jd_id=${jdId}`
      : `/api/candidates/${candidateId}/analyze`;
    const response = await api.post(url);
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

export const jobDescriptionsApi = {
  createJobDescription: async (title: string, descriptionText?: string, descriptionFile?: File) => {
    const formData = new FormData();
    formData.append('title', title);
    
    if (descriptionFile) {
      formData.append('description_file', descriptionFile);
    } else if (descriptionText) {
      formData.append('description_text', descriptionText);
    }

    const response = await api.post('/api/job-descriptions/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  listJobDescriptions: async () => {
    const response = await api.get('/api/job-descriptions/');
    return response.data;
  },

  getJobDescription: async (jdId: number) => {
    const response = await api.get(`/api/job-descriptions/${jdId}`);
    return response.data;
  },

  deleteJobDescription: async (jdId: number) => {
    const response = await api.delete(`/api/job-descriptions/${jdId}`);
    return response.data;
  },
};

export default api;
