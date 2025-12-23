import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import QueryPage from './pages/QueryPage';
import DocumentsPage from './pages/DocumentsPage';
import EvaluationPage from './pages/EvaluationPage';
import './App.css';

function App() {
    return (
        <Router>
            <div className="App">
                <Navbar />
                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<Navigate to="/query" replace />} />
                        <Route path="/query" element={<QueryPage />} />
                        <Route path="/documents" element={<DocumentsPage />} />
                        <Route path="/evaluation" element={<EvaluationPage />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App;
