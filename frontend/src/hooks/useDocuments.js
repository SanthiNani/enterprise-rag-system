import { useState, useCallback } from 'react';
import * as api from '../services/api';

export const useDocuments = () => {
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchDocuments = useCallback(async () => {
        setLoading(true);
        try {
            const data = await api.getDocuments();
            setDocuments(data.documents);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    const uploadDocument = useCallback(async (file) => {
        setLoading(true);
        try {
            const result = await api.uploadDocument(file);
            await fetchDocuments();
            return result;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [fetchDocuments]);

    const removeDocument = useCallback(async (documentId) => {
        try {
            await api.deleteDocument(documentId);
            await fetchDocuments();
        } catch (err) {
            setError(err.message);
            throw err;
        }
    }, [fetchDocuments]);

    return {
        documents,
        loading,
        error,
        fetchDocuments,
        uploadDocument,
        removeDocument,
    };
};
