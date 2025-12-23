import React, { useState, useEffect } from 'react';
import QueryInterface from '../components/QueryInterface';
import ResultDisplay from '../components/ResultDisplay';
import { useQuery } from '../hooks/useQuery';
import { getIndexStatus } from '../services/api';
import './QueryPage.css';

const QueryPage = () => {
    const { result, loading, error, askQuestion } = useQuery();
    const [indexStatus, setIndexStatus] = useState(null);
    const [indexLoading, setIndexLoading] = useState(true);

    useEffect(() => {
        const fetchIndexStatus = async () => {
            try {
                const status = await getIndexStatus();
                setIndexStatus(status);
            } catch (err) {
                console.error('Failed to fetch index status:', err);
            } finally {
                setIndexLoading(false);
            }
        };

        fetchIndexStatus();
    }, []);

    return (
        <div className="query-page">
            <div className="query-page-container">
                <h1>🔍 Query Documents</h1>
                <p className="subtitle">Ask questions about your uploaded documents</p>

                <QueryInterface
                    onQuery={askQuestion}
                    loading={loading}
                    indexStatus={indexStatus}
                />

                {error && (
                    <div className="error-box">
                        ❌ Error: {error}
                    </div>
                )}

                <div className="result-wrapper">
                    <ResultDisplay result={result} />
                </div>
            </div>
        </div>
    );
};

export default QueryPage;