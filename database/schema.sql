-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(20) NOT NULL CHECK (file_type IN ('pdf', 'txt', 'docx')),
    file_size INTEGER,
    content TEXT,
    processed BOOLEAN DEFAULT FALSE,
    indexed BOOLEAN DEFAULT FALSE,
    chunk_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Separate index creation for documents table
CREATE INDEX idx_documents_original_filename ON documents(original_filename);
CREATE INDEX idx_documents_processed ON documents(processed);
CREATE INDEX idx_documents_indexed ON documents(indexed);
CREATE INDEX idx_documents_created_at ON documents(created_at);

-- Queries table
CREATE TABLE queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    question TEXT NOT NULL,
    answer TEXT,
    confidence FLOAT,
    latency_ms FLOAT,
    retrieved_chunks JSONB,
    citations JSONB,
    support_details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Separate index creation for queries table
CREATE INDEX idx_queries_document_id ON queries(document_id);
CREATE INDEX idx_queries_created_at ON queries(created_at);
CREATE INDEX idx_queries_confidence ON queries(confidence);

-- Index metadata table
CREATE TABLE index_metadata (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    index_name VARCHAR(255) UNIQUE NOT NULL,
    document_ids JSONB,
    total_chunks INTEGER DEFAULT 0,
    index_size_mb FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_indexed TIMESTAMP
);

-- Create indexes for JSON queries
CREATE INDEX idx_queries_citations ON queries USING gin (citations);
CREATE INDEX idx_queries_support_details ON queries USING gin (support_details);
CREATE INDEX idx_index_metadata_document_ids ON index_metadata USING gin (document_ids);

-- Create triggers for updated_at
CREATE TRIGGER trigger_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_index_metadata_updated_at
    BEFORE UPDATE ON index_metadata
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- Function for updating timestamp
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create indexes for common queries
CREATE INDEX idx_documents_file_type ON documents(file_type);
CREATE INDEX idx_queries_question_trgm ON queries USING gin(question gin_trgm_ops);
