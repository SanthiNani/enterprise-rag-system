import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
    return (
        <nav className="navbar">
            <div className="navbar-container">
                <Link to="/" className="navbar-logo">
                    📚 RAG System
                </Link>
                <ul className="nav-menu">
                    <li className="nav-item">
                        <Link to="/" className="nav-link">Home</Link>
                    </li>
                    <li className="nav-item">
                        <Link to="/documents" className="nav-link">Documents</Link>
                    </li>
                    <li className="nav-item">
                        <Link to="/query" className="nav-link">Query</Link>
                    </li>
                    <li className="nav-item">
                        <Link to="/evaluation" className="nav-link">Evaluation</Link>
                    </li>
                </ul>
            </div>
        </nav>
    );
};

export default Navbar;
