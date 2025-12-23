import React, { useState, useEffect } from 'react';
import DocumentUpload from '../components/DocumentUpload';
import { getDocuments, uploadDocument, deleteDocument, buildIndex, getIndexStatus } from '../services/api';
import './DocumentsPage.css';

const DocumentsPage = () => {
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(false);
    const [indexBuilding, setIndexBuilding] = useState(false);
    const [indexStatus, setIndexStatus] = useState(null);
    const [error, setError] = useState(null);

    const fetchDocuments = async () => {
        try {
            const data = await getDocuments();
            setDocuments(data.documents || []);
        } catch (err) {
            console.error('Failed to fetch documents:', err);
            setError('Failed to load documents');
        }
    };

    const fetchIndexStatus = async () => {
        try {
            const status = await getIndexStatus();
            setIndexStatus(status);
        } catch (err) {
            console.error('Failed to fetch index status:', err);
        }
    };

    useEffect(() => {
        fetchDocuments();
        fetchIndexStatus();
    }, []);

    const handleUpload = async (file) => {
        setLoading(true);
        setError(null);
        try {
            await uploadDocument(file);
            await fetchDocuments();
        } catch (err) {
            setError('Failed to upload document');
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (docId) => {
        if (!window.confirm('Are you sure you want to delete this document?')) return;

        try {
            await deleteDocument(docId);
            await fetchDocuments();
        } catch (err) {
            setError('Failed to delete document');
        }
    };

    const handleBuildIndex = async () => {
        setIndexBuilding(true);
        setError(null);
        try {
            await buildIndex();
            await fetchIndexStatus();
            alert('Index built successfully!');
        } catch (err) {
            setError('Failed to build index');
        } finally {
            setIndexBuilding(false);
        }
    };

    return (
        <div className="documents-page">
            <div className="documents-container">
                <header className="page-header">
                    <h1>📁 Manage Documents</h1>
                    <p className="subtitle">Upload knowledge base documents for your RAG system</p>
                </header>

                <div className="upload-section">
                    <DocumentUpload onUpload={handleUpload} loading={loading} />
                </div>

                {error && <div className="error-message">{error}</div>}

                <div className="actions-section">
                    <div className="index-status">
                        <h3>Index Status</h3>
                        <div className="status-indicator">
                            <span className={`status-dot ${indexStatus?.index_exists ? 'active' : ''}`}></span>
                            <span>{indexStatus?.index_exists ? 'Index Active' : 'Index Missing'}</span>
                            {indexStatus && <span className="doc-count">({indexStatus.doc_count} documents indexed)</span>}
                        </div>
                    </div>

                    <button
                        className="build-index-btn"
                        onClick={handleBuildIndex}
                        disabled={indexBuilding || documents.length === 0}
                    >
                        {indexBuilding ? 'Building Index...' : '🔄 Build Index'}
                    </button>
                </div>

                <div className="documents-list-section">
                    <h3>Uploaded Documents ({documents.length})</h3>
                    {documents.length === 0 ? (
                        <p className="empty-state">No documents uploaded yet.</p>
                    ) : (
                        <ul className="documents-list">
                            {documents.map((doc) => (
                                <li key={doc.id} className="document-item">
                                    <div className="doc-info">
                                        <span className="doc-icon">📄</span>
                                        <span className="doc-name">{doc.filename}</span>
                                        <span className="doc-date">{new Date(doc.upload_date).toLocaleDateString()}</span>
                                    </div>
                                    <button
                                        className="delete-btn"
                                        onClick={() => handleDelete(doc.id)}
                                        title="Delete Document"
                                    >
                                        🗑️
                                    </button>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            </div>
        </div>
    );
};

export default DocumentsPage;
