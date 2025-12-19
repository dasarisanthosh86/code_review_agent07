import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'https://code-review-agent07.onrender.com';

// Configure axios defaults
axios.defaults.timeout = 30000;

export const reviewCode = async (repoUrl, file, githubToken = '') => {
  const form = new FormData();
  form.append('repo_url', repoUrl);
  if (file) form.append('scan_report', file);
  if (githubToken) form.append('github_token', githubToken);
  
  const res = await axios.post(`${API_BASE}/review`, form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return res.data;
};

export const getReviews = async () => {
  try {
    const res = await axios.get(`${API_BASE}/reviews`);
    return res.data;
  } catch (error) {
    throw new Error('Failed to fetch reviews');
  }
};

export const getReview = async (id) => {
  try {
    const res = await axios.get(`${API_BASE}/reviews/${id}`);
    return res.data;
  } catch (error) {
    throw new Error('Failed to fetch review');
  }
};

export const checkHealth = async () => {
  try {
    const res = await axios.get(`${API_BASE}/`);
    return res.data;
  } catch (error) {
    throw new Error('Backend not available');
  }
};