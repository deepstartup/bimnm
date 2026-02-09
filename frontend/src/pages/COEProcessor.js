import React, { useState, useEffect } from 'react';
import { uploadCOE, getCOEHistory, getCOEResults, deleteCOEResults } from '../services/coeService';
import './COEProcessor.css';

export default function COEProcessor() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [selectedId, setSelectedId] = useState(null);

  useEffect(() => {
    loadHistory();
  }, []);

  useEffect(() => {
    if (selectedId) {
      getCOEResults(selectedId).then(setResult).catch(() => setResult(null));
    } else {
      setResult(null);
    }
  }, [selectedId]);

  const loadHistory = async () => {
    try {
      const list = await getCOEHistory();
      setHistory(list);
    } catch {
      setHistory([]);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Select a CSV file');
      return;
    }
    setError('');
    setLoading(true);
    try {
      const data = await uploadCOE(file);
      setResult(data);
      setSelectedId(data.analysis_id);
      loadHistory();
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteCOEResults(id);
      if (selectedId === id) setResult(null);
      setSelectedId(null);
      loadHistory();
    } catch (err) {
      setError(err.response?.data?.detail || 'Delete failed');
    }
  };

  const dist = result?.complexity_distribution || {};
  const distEntries = Object.entries(dist);

  return (
    <main className="main">
      <div className="coe-page">
        <h2>COE CSV Processor</h2>
        <p className="page-desc">Upload a Center of Excellence export CSV to analyze report complexity and find duplicates.</p>

        <section className="coe-upload-section card">
          <h3>Upload CSV</h3>
          <form onSubmit={handleUpload}>
            <div className="form-group">
              <input
                type="file"
                accept=".csv"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
            </div>
            {error && <p className="error-msg">{error}</p>}
            <button type="submit" className="btn btn-primary" disabled={loading || !file}>
              {loading ? 'Analyzing...' : 'Upload & Analyze'}
            </button>
          </form>
        </section>

        {result && (
          <section className="coe-results card">
            <h3>Results {result.filename && `— ${result.filename}`}</h3>
            <div className="coe-kpis">
              <div className="kpi"><span className="kpi-label">Reports</span><span className="kpi-value">{result.report_count}</span></div>
              <div className="kpi"><span className="kpi-label">Unique</span><span className="kpi-value">{result.unique_count}</span></div>
              <div className="kpi"><span className="kpi-label">Duplicates</span><span className="kpi-value">{result.duplicate_count}</span></div>
              <div className="kpi"><span className="kpi-label">Est. Hours</span><span className="kpi-value">{result.total_estimated_hours}</span></div>
            </div>
            {distEntries.length > 0 && (
              <div className="complexity-dist">
                <h4>Complexity distribution</h4>
                <ul>
                  {distEntries.map(([cat, count]) => (
                    <li key={cat}><strong>{cat}</strong>: {count}</li>
                  ))}
                </ul>
              </div>
            )}
            {result.top_complex_reports?.length > 0 && (
              <div className="top-complex">
                <h4>Top complex reports</h4>
                <ul>
                  {result.top_complex_reports.slice(0, 10).map((r, i) => (
                    <li key={i}>{r.report_name} — Score: {r.complexity_score}, Hours: {r.estimated_hours}</li>
                  ))}
                </ul>
              </div>
            )}
            {result.duplicate_groups?.length > 0 && (
              <div className="duplicate-groups">
                <h4>Duplicate groups</h4>
                {result.duplicate_groups.slice(0, 10).map((g, i) => (
                  <div key={i} className="dup-group">
                    <span className="dup-sim">{g.similarity}%</span> {g.report_names?.join(', ')} — {g.recommendation}
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        <section className="coe-history card">
          <h3>Past analyses</h3>
          {history.length === 0 ? (
            <p className="muted">No past analyses.</p>
          ) : (
            <ul className="history-list">
              {history.map((h) => (
                <li key={h.id} className={selectedId === h.id ? 'selected' : ''}>
                  <button type="button" className="link" onClick={() => setSelectedId(h.id)}>
                    {h.filename} — {h.report_count} reports, {h.total_estimated_hours} hrs
                  </button>
                  <button type="button" className="btn-small btn-danger" onClick={() => handleDelete(h.id)}>Delete</button>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </main>
  );
}
