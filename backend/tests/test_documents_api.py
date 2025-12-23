import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from src.database.db import get_db
from src.database.models import Document

# Mock DB dependency
def override_get_db():
    try:
        db = MagicMock(spec=Session)
        yield db
    finally:
        pass

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def mock_db_session():
    return next(override_get_db())

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@patch('src.database.crud.DocumentCRUD.create')
@patch('builtins.open', new_callable=MagicMock)
@patch('os.path.exists', return_value=False)
def test_upload_document(mock_exists, mock_open, mock_create):
    """Test document upload endpoint"""
    # Mock DocumentCRUD.create response
    mock_doc = MagicMock(spec=Document)
    mock_doc.id = "123"
    mock_doc.filename = "test.txt"
    mock_create.return_value = mock_doc

    # Create dummy file
    files = {'file': ('test.txt', b'test content', 'text/plain')}
    
    response = client.post("/api/documents/upload", files=files)
    
    # Assertions
    assert response.status_code == 200
    assert "document_id" in response.json()
    assert response.json()["filename"] == "test.txt"

@patch('src.database.crud.DocumentCRUD.get_all')
def test_get_documents(mock_get_all):
    """Test get documents endpoint"""
    # Mock data
    doc1 = MagicMock(spec=Document)
    doc1.id = "1"
    doc1.filename = "doc1.txt"
    doc1.upload_date = "2023-01-01"
    
    doc2 = MagicMock(spec=Document)
    doc2.id = "2"
    doc2.filename = "doc2.txt"
    doc2.upload_date = "2023-01-02"
    
    mock_get_all.return_value = [doc1, doc2]

    response = client.get("/api/documents")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["documents"]) == 2

@patch('src.database.crud.DocumentCRUD.delete')
def test_delete_document(mock_delete):
    """Test delete document endpoint"""
    response = client.delete("/api/documents/123")
    
    assert response.status_code == 200
    assert response.json() == {"message": "Document deleted"}
    mock_delete.assert_called_once()
