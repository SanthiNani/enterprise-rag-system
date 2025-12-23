import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './QueryInterface.css';

const QueryInterface = ({ onQuery, loading, indexStatus }) => {
    const [question, setQuestion] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (question.trim() && !loading) {
            onQuery(question);
            setQuestion('');
        }
    };

    const isDisabled = !indexStatus?.index_exists || loading;

    return (
        <div className="query-container">
            <form onSubmit={handleSubmit} className="query-form">
                <textarea
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Ask a question about your documents..."
                    className="query-input"
                    disabled={isDisabled}
                    rows="3"
                />
                <button
                    type="submit"
                    disabled={isDisabled}
                    className="query-btn"
                >
                    {loading ? 'Searching...' : '🔍 Search'}
                </button>
            </form>

            {!indexStatus?.index_exists && (
                <div className="warning-box">
                    <p>⚠️ The search index is empty.</p>
                    <Link to="/documents" className="warning-action-link">
                        Go to Documents to Upload & Build Index →
                    </Link>
                </div>
            )}
        </div>
    );
};

export default QueryInterface;
