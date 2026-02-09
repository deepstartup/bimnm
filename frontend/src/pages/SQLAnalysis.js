import React, { useState } from 'react';
import { analyzeSQL, compareSQL } from '../services/sqlService';
import './SQLAnalysis.css';

export default function SQLAnalysis() {
  const [sql, setSql] = useState('');
  const [sql2, setSql2] = useState('');
  const [mode, setMode] = useState('analyze'); // 'analyze' | 'compare'
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAnalyze = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);
    setLoading(true);
    try {
      const data = await analyzeSQL(sql);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const handleCompare = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);
    setLoading(true);
    try {
      const data = await compareSQL(sql, sql2);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Compare failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="main">
      <div className="sql-page">
        <h2>SQL Complexity Analyzer</h2>
        <p className="page-desc">Analyze SQL complexity, lineage, and migration recommendations, or compare two queries.</p>

        <div className="tabs">
          <button
            type="button"
            className={mode === 'analyze' ? 'active' : ''}
            onClick={() => { setMode('analyze'); setResult(null); setError(''); }}
          >
            Analyze
          </button>
          <button
            type="button"
            className={mode === 'compare' ? 'active' : ''}
            onClick={() => { setMode('compare'); setResult(null); setError(''); }}
          >
            Compare
          </button>
        </div>

        {mode === 'analyze' && (
          <section className="card">
            <form onSubmit={handleAnalyze}>
              <div className="form-group">
                <label>SQL Query</label>
                <textarea
                  value={sql}
                  onChange={(e) => setSql(e.target.value)}
                  rows={12}
                  placeholder="SELECT ... FROM ..."
                  className="sql-textarea"
                />
              </div>
              {error && <p className="error-msg">{error}</p>}
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? 'Analyzing...' : 'Analyze'}
              </button>
            </form>
          </section>
        )}

        {mode === 'compare' && (
          <section className="card">
            <form onSubmit={handleCompare}>
              <div className="form-group">
                <label>Original SQL</label>
                <textarea
                  value={sql}
                  onChange={(e) => setSql(e.target.value)}
                  rows={8}
                  placeholder="Original query..."
                  className="sql-textarea"
                />
              </div>
              <div className="form-group">
                <label>Migrated SQL</label>
                <textarea
                  value={sql2}
                  onChange={(e) => setSql2(e.target.value)}
                  rows={8}
                  placeholder="Migrated query..."
                  className="sql-textarea"
                />
              </div>
              {error && <p className="error-msg">{error}</p>}
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? 'Comparing...' : 'Compare'}
              </button>
            </form>
          </section>
        )}

        {result && mode === 'analyze' && (
          <section className="card result-card">
            <h3>Analysis result</h3>
            <div className="result-kpis">
              <div className="kpi"><span className="kpi-label">Complexity score</span><span className="kpi-value">{result.complexity_score}</span></div>
              <div className="kpi"><span className="kpi-label">Category</span><span className="kpi-value">{result.complexity_category}</span></div>
              <div className="kpi"><span className="kpi-label">Est. hours</span><span className="kpi-value">{result.estimated_hours}</span></div>
              <div className="kpi"><span className="kpi-label">Risk</span><span className="kpi-value">{result.risk_level}</span></div>
            </div>
            {result.lineage?.tables?.length > 0 && (
              <p><strong>Tables:</strong> {result.lineage.tables.join(', ')}</p>
            )}
            {result.recommendations?.length > 0 && (
              <div>
                <strong>Recommendations</strong>
                <ul>
                  {result.recommendations.map((r, i) => <li key={i}>{r}</li>)}
                </ul>
              </div>
            )}
          </section>
        )}

        {result && mode === 'compare' && (
          <section className="card result-card">
            <h3>Comparison result</h3>
            <div className="result-kpis">
              <div className="kpi"><span className="kpi-label">Similarity</span><span className="kpi-value">{result.similarity_percent}%</span></div>
              <div className="kpi"><span className="kpi-label">Identical</span><span className="kpi-value">{result.are_identical ? 'Yes' : 'No'}</span></div>
              <div className="kpi"><span className="kpi-label">Semantically equivalent</span><span className="kpi-value">{result.are_semantically_equivalent ? 'Yes' : 'No'}</span></div>
              <div className="kpi"><span className="kpi-label">Migration quality</span><span className="kpi-value">{result.migration_quality}</span></div>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}
