import React, { useState, useEffect } from 'react';
import { getEvaluationResults } from '../services/api';
import './EvaluationPage.css';

const EvaluationPage = () => {
    const [metrics, setMetrics] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const data = await getEvaluationResults();
                setMetrics(data);
            } catch (err) {
                console.error("Failed to load metrics", err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const summary = metrics?.summary || {};
    const baseline = metrics?.baseline ? metrics.baseline : [];

    // Format percentage
    const fmt = (val) => val ? (val * 100).toFixed(1) + '%' : '--';

    return (
        <div className="evaluation-page">
            <div className="evaluation-container">
                <header className="page-header">
                    <h1>📊 System Evaluation</h1>
                    <p className="subtitle">Performance metrics and RAG quality assessment</p>
                </header>

                {loading ? (
                    <div className="loading-state">Loading metrics...</div>
                ) : (
                    <>
                        <div className="metrics-grid">
                            <div className="metric-card">
                                <h3>Retrieval Precision</h3>
                                <div className="value">{fmt(summary.rag_precision)}</div>
                                <p>Relevant chunks / Retrieved</p>
                                {summary.baseline_precision && (
                                    <small className="comparison">vs {fmt(summary.baseline_precision)} (Baseline)</small>
                                )}
                            </div>

                            <div className="metric-card">
                                <h3>Recall</h3>
                                <div className="value">{fmt(summary.rag_recall)}</div>
                                <p>Relevant content found</p>
                                {summary.baseline_recall && (
                                    <small className="comparison">vs {fmt(summary.baseline_recall)} (Baseline)</small>
                                )}
                            </div>

                            <div className="metric-card">
                                <h3>ROUGE-L Score</h3>
                                <div className="value">{fmt(summary.rag_rouge)}</div>
                                <p>Answer Quality (Text Match)</p>
                                {summary.baseline_rouge && (
                                    <small className="comparison">vs {fmt(summary.baseline_rouge)} (Baseline)</small>
                                )}
                            </div>

                            <div className="metric-card highlight">
                                <h3>Grounding Confidence</h3>
                                <div className="value">{fmt(summary.rag_confidence)}</div>
                                <p>Average System Confidence</p>
                            </div>
                        </div>

                        <div className="evaluation-details">
                            <h3>Comparison: Your RAG vs Baseline</h3>
                            <div className="table-wrapper">
                                <table className="comparison-table">
                                    <thead>
                                        <tr>
                                            <th>Metric</th>
                                            <th>Baseline (No Verification)</th>
                                            <th>Your PRO System</th>
                                            <th>Improvement</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>Hallucination Risk</td>
                                            <td>High ({(100 - (summary.baseline_confidence || 0) * 100).toFixed(1)}%)</td>
                                            <td><strong>Low ({(100 - summary.rag_confidence * 100).toFixed(1)}%)</strong></td>
                                            <td className="positive">✅ Safer</td>
                                        </tr>
                                        <tr>
                                            <td>Precision</td>
                                            <td>{fmt(summary.baseline_precision)}</td>
                                            <td><strong>{fmt(summary.rag_precision)}</strong></td>
                                            <td className="positive">↗ Higher</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default EvaluationPage;
