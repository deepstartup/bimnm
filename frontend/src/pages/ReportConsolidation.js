import React, { useState } from 'react';
import api from '../services/api';
import './ReportConsolidation.css';

export default function ReportConsolidation() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const runConsolidation = async () => {
    setError('');
    setResult(null);
    setLoading(true);
    try {
      const { data } = await api.post('/api/reports/consolidate');
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="main">
      <div className="consolidation-page">
        <h2>Report Consolidation</h2>
        <p className="page-desc">Find duplicate and near-duplicate reports to reduce migration scope.</p>

        <section className="card">
          <p>Run duplicate detection on all your reports. Reports with identical or very similar SQL are grouped.</p>
          {error && <p className="error-msg">{error}</p>}
          <button
            type="button"
            className="btn btn-primary"
            onClick={runConsolidation}
            disabled={loading}
          >
            {loading ? 'Analyzing...' : 'Find duplicates'}
          </button>
        </section>

        {result && (
          <section className="card">
            <h3>Results</h3>
            <div className="cons-kpis">
              <div className="kpi"><span className="kpi-label">Total reports</span><span className="kpi-value">{result.total_reports}</span></div>
              <div className="kpi"><span className="kpi-label">Unique</span><span className="kpi-value">{result.unique_reports}</span></div>
              <div className="kpi"><span className="kpi-label">Reports to skip</span><span className="kpi-value">{result.potential_savings?.reports_to_skip ?? 0}</span></div>
              <div className="kpi"><span className="kpi-label">Hours saved</span><span className="kpi-value">{result.potential_savings?.hours_saved ?? 0}</span></div>
            </div>
            {result.duplicate_groups?.length > 0 ? (
              <div className="dup-groups">
                <h4>Duplicate groups</h4>
                {result.duplicate_groups.map((g, i) => (
                  <div key={i} className="dup-group">
                    <span className="dup-sim">Group {g.group_id} — {g.similarity}%</span>
                    <ul>
                      {g.reports?.map((r, j) => <li key={j}>{r.name}</li>)}
                    </ul>
                    <p className="dup-rec">{g.recommendation}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="muted">No duplicate groups found.</p>
            )}
          </section>
        )}
      </div>
    </main>
  );
}
