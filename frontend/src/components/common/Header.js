import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="header">
      <h1>BI Modernization Platform</h1>
      <div className="header-right">
        <nav className="header-nav">
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/coe">COE Processor</Link>
          <Link to="/sql">SQL Analysis</Link>
          <Link to="/consolidation">Consolidation</Link>
        </nav>
        <div className="user-info">
          <span>{user?.username}</span>
          <button type="button" className="btn btn-primary" onClick={logout} style={{ width: 'auto', margin: 0 }}>
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
