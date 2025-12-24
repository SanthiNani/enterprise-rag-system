import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
const API_TIMEOUT = parseInt(process.env.REACT_APP_API_TIMEOUT) || 120000;

console.log('API Config:', { API_BASE_URL, API_TIMEOUT }); // DEBUG: Verify URL

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: API_TIMEOUT,
    headers: {
        'Content-Type': 'application/json',
    },
});

// ============ HEALTH CHECK ============
export const healthCheck = async () => {
    try {
        const response = await api.get('/health');
        return response.data;
    } catch (error) {
        console.error('Health check failed:', error);
        throw error;
    }
};

// ============ DOCUMENT ENDPOINTS ============
export const uploadDocument = async (file) => {
    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await api.post('/api/documents/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        console.error('Upload failed:', error);
        throw error;
    }
};

export const getDocuments = async () => {
    try {
        const response = await api.get('/api/documents');
        return response.data;
    } catch (error) {
        console.error('Get documents failed:', error);
        throw error;
    }
};

export const deleteDocument = async (documentId) => {
    try {
        const response = await api.delete(`/api/documents/${documentId}`);
        return response.data;
    } catch (error) {
        console.error('Delete document failed:', error);
        throw error;
    }
};

// ============ INDEX ENDPOINTS ============
export const buildIndex = async () => {
    try {
        const response = await api.post('/api/index/build');
        return response.data;
    } catch (error) {
        console.error('Build index failed:', error);
        throw error;
    }
};

export const getIndexStatus = async () => {
    try {
        const response = await api.get('/api/index/status');
        return response.data;
    } catch (error) {
        console.error('Get index status failed:', error);
        throw error;
    }
};

// ============ QUERY ENDPOINTS ============
export const answerQuery = async (question) => {
    try {
        const response = await api.post('/api/query/answer', null, {
            params: { question },
        });
        return response.data;
    } catch (error) {
        console.error('Answer query failed:', error);
        throw error;
    }
};

export const getQueryHistory = async (limit = 50) => {
    try {
        const response = await api.get('/api/query/history', {
            params: { limit },
        });
        return response.data;
    } catch (error) {
        console.error('Get query history failed:', error);
        throw error;
    }
};

export const getEvaluationResults = async () => {
    try {
        const response = await api.get('/api/evaluation/results');
        return response.data;
    } catch (error) {
        console.error('Error fetching evaluation results:', error);
        throw error;
    }
};

export default api;