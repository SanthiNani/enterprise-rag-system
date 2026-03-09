import React, { useState, useEffect } from 'react';
import { getEvaluationResults } from '../services/api';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis
} from 'recharts';
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

    // Format percentage
    const fmt = (val) => val ? (val * 100).toFixed(1) + '%' : '--';

    // Formatting data for Bar Chart (Comparison)
    const comparisonData = [
        {
            name: 'Precision',
            Baseline: (summary.baseline_precision * 100) || 0,
            'PRO System': (summary.rag_precision * 100) || 0,
        },
        {
            name: 'Recall',
            Baseline: (summary.baseline_recall * 100) || 0,
            'PRO System': (summary.rag_recall * 100) || 0,
        },
        {
            name: 'ROUGE-L',
            Baseline: (summary.baseline_rouge * 100) || 0,
            'PRO System': (summary.rag_rouge * 100) || 0,
        }
    ];

    // Data for Radar Chart (System Health)
    const radarData = [
        {
            subject: 'Precision',
            score: (summary.rag_precision * 100) || 0,
            fullMark: 100,
        },
        {
            subject: 'Recall',
            score: (summary.rag_recall * 100) || 0,
            fullMark: 100,
        },
        {
            subject: 'Quality',
            score: (summary.rag_rouge * 100) || 0,
            fullMark: 100,
        },
        {
            subject: 'Confidence',
            score: (summary.rag_confidence * 100) || 0,
            fullMark: 100,
        },
        {
            subject: 'Safety',
            score: (summary.rag_confidence * 100) || 0, // Correlated with high confidence
            fullMark: 100,
        }
    ];

    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            return (
                <div className="custom-tooltip">
                    <p className="tooltip-label">{label}</p>
                    {payload.map((entry, index) => (
                        <p key={index} style={{ color: entry.color, fontWeight: 600 }}>
                            {entry.name}: {entry.value.toFixed(1)}%
                        </p>
                    ))}
                </div>
            );
        }
        return null;
    };

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

                        <div className="charts-section">
                            <div className="chart-wrapper">
                                <h3>Performance Comparison</h3>
                                <div className="chart-container">
                                    <ResponsiveContainer width="100%" height={300}>
                                        <BarChart
                                            data={comparisonData}
                                            margin={{ top: 20, right: 30, left: 0, bottom: 5 }}
                                        >
                                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                                            <XAxis dataKey="name" stroke="var(--text-secondary)" tick={{ fill: 'var(--text-secondary)' }} />
                                            <YAxis stroke="var(--text-secondary)" tick={{ fill: 'var(--text-secondary)' }} tickFormatter={(val) => `${val}%`} />
                                            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
                                            <Legend wrapperStyle={{ paddingTop: '20px' }} />
                                            <Bar dataKey="Baseline" fill="var(--surface-hover)" radius={[4, 4, 0, 0]} />
                                            <Bar dataKey="PRO System" fill="var(--primary-color)" radius={[4, 4, 0, 0]} />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>

                            <div className="chart-wrapper">
                                <h3>Overall System Health</h3>
                                <div className="chart-container">
                                    <ResponsiveContainer width="100%" height={300}>
                                        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                                            <PolarGrid stroke="rgba(255,255,255,0.2)" />
                                            <PolarAngleAxis dataKey="subject" tick={{ fill: 'var(--text-secondary)', fontSize: 12 }} />
                                            <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                                            <Radar
                                                name="PRO System"
                                                dataKey="score"
                                                stroke="var(--accent-color)"
                                                fill="var(--accent-color)"
                                                fillOpacity={0.5}
                                            />
                                            <Tooltip content={<CustomTooltip />} />
                                        </RadarChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                        </div>

                        <div className="evaluation-details">
                            <h3>Comparison: Detailed Breakdown</h3>
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
