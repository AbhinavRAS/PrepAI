import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const startInterview = async (data) => {
  try {
    // Convert JSON data to FormData
    const formData = new FormData();
    formData.append('name', data.name);
    formData.append('email', data.email);
    formData.append('interview_type', data.interview_type);
    formData.append('rounds', data.rounds);
    formData.append('level', data.level || 'Entry Level');
    if (data.resume) {
      formData.append('resume', data.resume);
    }

    const response = await api.post('/api/interview/start', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response;
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
};

export const startMockSession = async (data) => {
  try {
    const response = await api.post('/api/interview/start-mock', data);
    return response;
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
};

export const submitAnswer = async (formData) => {
  try {
    const response = await api.post('/api/interview/transcribe', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response;
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
};

export const completeInterview = async (sessionId) => {
  try {
    const formData = new FormData();
    formData.append('session_id', sessionId);

    const response = await api.post('/api/interview/complete', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response;
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
};