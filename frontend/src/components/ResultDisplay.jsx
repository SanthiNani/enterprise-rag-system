import React from 'react';
import { formatLatency, getConfidenceColor, formatDate } from '../services/utils';
import './ResultDisplay.css';

const ResultDisplay = ({ result }) => {
    if (!result) {
        return (
            <div className="no-results">
                <p>📭 No results yet. Ask a question to get started.</p>
            </div>
        );
    }

    return (
        <div className="result-container">
            {/* Answer Section */}
            <div className="result-section answer-section">
                <h3>📝 Answer</h3>
                <div className="answer-text">
                    {result.answer}
                </div>
            </div>

            {/* Confidence & Latency */}
            <div className="result-meta">
                <div className="meta-item">
                    <span className="meta-label">Confidence:</span>
                    <span
                        className="meta-value confidence-badge"
                        style={{ backgroundColor: getConfidenceColor(result.confidence) }}
                    >
                        {(result.confidence * 100).toFixed(0)}%
                    </span>
                </div>
                <div className="meta-item">
                    <span className="meta-label">Latency:</span>
                    <span className="meta-value">
                        {formatLatency(result.latency?.total_ms || 0)}
                    </span>
                </div>
            </div>

            {/* Citations */}
            <div className="result-section">
                <h3>📖 Sources</h3>
                <div className="citations-list">
                    {result.citations?.map((citation, idx) => (
                        <div key={idx} className="citation-item">
                            <div className="citation-number">[{idx + 1}]</div>
                            <div className="citation-content">
                                <p className="citation-text">{citation.sentence}</p>
                                <p className="citation-source">
                                    Source: {citation.source_file}
                                    {citation.similarity && ` (Similarity: ${(citation.similarity * 100).toFixed(0)}%)`}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Support Details */}
            {result.support_details && (
                <div className="result-section">
                    <h3>✓ Grounding Details</h3>
                    <div className="support-list">
                        {result.support_details.map((detail, idx) => (
                            <div
                                key={idx}
                                className={`support-item ${detail.is_supported ? 'supported' : 'unsupported'}`}
                            >
                                <span className="support-icon">
                                    {detail.is_supported ? '✓' : '✗'}
                                </span>
                                <span className="support-text">{detail.sentence}</span>
                                <span className="support-similarity">
                                    {(detail.max_similarity * 100).toFixed(0)}%
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default ResultDisplay;
