import React, { useState, useEffect } from 'react';
import api from '../../services/api';

export default function ReportList() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      const { data } = await api.get('/api/reports/');
      setReports(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loader">Loading reports...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="report-list">
      <h3>Reports</h3>
      {reports.length === 0 ? (
        <p style={{ color: 'var(--text-muted)' }}>No reports yet.</p>
      ) : (
        <div className="reports-grid">
          {reports.map((report) => (
            <div key={report.id} className="report-card">
              <h3>{report.name}</h3>
              <p>{report.description || '—'}</p>
              <div className="report-meta">
                {report.complexity_score != null && (
                  <span className="complexity">Complexity: {report.complexity_score}</span>
                )}
                {report.source_system && (
                  <span className="source">Source: {report.source_system}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
