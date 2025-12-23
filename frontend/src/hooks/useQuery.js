import { useState, useCallback } from 'react';
import * as api from '../services/api';

export const useQuery = () => {
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const askQuestion = useCallback(async (question) => {
        setLoading(true);
        setError(null);
        try {
            const data = await api.answerQuery(question);
            setResult(data);
            return data;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    return {
        result,
        loading,
        error,
        askQuestion,
    };
};