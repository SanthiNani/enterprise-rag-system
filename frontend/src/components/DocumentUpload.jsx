import React, { useState } from 'react';
import './DocumentUpload.css';

const DocumentUpload = ({ onUpload, loading }) => {
    const [file, setFile] = useState(null);
    const [dragActive, setDragActive] = useState(false);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true);
        } else if (e.type === 'dragleave') {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        const droppedFiles = e.dataTransfer.files;
        if (droppedFiles && droppedFiles[0]) {
            setFile(droppedFiles[0]);
        }
    };

    const handleFileChange = (e) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            setFile(selectedFile);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (file) {
            try {
                await onUpload(file);
                setFile(null);
            } catch (error) {
                console.error('Upload error:', error);
            }
        }
    };

    return (
        <div className="upload-container">
            <form onSubmit={handleSubmit} className="upload-form">
                <div
                    className={`drop-zone ${dragActive ? 'active' : ''}`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                >
                    <div className="drop-zone-content">
                        <p className="drop-zone-icon">📄</p>
                        <p className="drop-zone-text">
                            {file ? file.name : 'Drag & drop files or click to select'}
                        </p>
                        <input
                            type="file"
                            onChange={handleFileChange}
                            accept=".pdf,.txt,.docx"
                            style={{ display: 'none' }}
                            id="file-input"
                        />
                        <label htmlFor="file-input" className="file-label">
                            Click to select
                        </label>
                    </div>
                </div>

                <button
                    type="submit"
                    disabled={!file || loading}
                    className="upload-btn"
                >
                    {loading ? 'Uploading...' : 'Upload Document'}
                </button>
            </form>
        </div>
    );
};

export default DocumentUpload;