import React, { useState, useEffect } from 'react';
import api from '../services/api';
import ReportList from '../components/reports/ReportList';

export default function Dashboard() {
  const [stats, setStats] = useState({
    total_reports: 0,
    reports_migrated: 0,
    migration_progress_percent: 0,
    complexity_breakdown: {},
    estimated_total_hours: 0,
    coe_analyses_count: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const { data } = await api.get('/api/dashboard/stats');
        setStats(data);
      } catch {
        try {
          const { data } = await api.get('/api/reports/');
          setStats({
            total_reports: Array.isArray(data) ? data.length : 0,
            reports_migrated: 0,
            migration_progress_percent: 0,
            complexity_breakdown: {},
            estimated_total_hours: 0,
            coe_analyses_count: 0,
          });
        } catch {
          setStats({ total_reports: 0, reports_migrated: 0, migration_progress_percent: 0, complexity_breakdown: {}, estimated_total_hours: 0, coe_analyses_count: 0 });
        }
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return (
      <main className="main">
        <div className="loader">Loading dashboard...</div>
      </main>
    );
  }

  const breakdown = stats.complexity_breakdown || {};
  return (
    <main className="main">
      <div className="dashboard">
        <h2>Dashboard</h2>
        <div className="dashboard-cards">
          <div className="dashboard-card">
            <h3>Total reports</h3>
            <div className="value">{stats.total_reports}</div>
          </div>
          <div className="dashboard-card">
            <h3>Migrated</h3>
            <div className="value">{stats.reports_migrated}</div>
          </div>
          <div className="dashboard-card">
            <h3>Progress</h3>
            <div className="value">{stats.migration_progress_percent}%</div>
          </div>
          <div className="dashboard-card">
            <h3>Est. hours</h3>
            <div className="value">{stats.estimated_total_hours}</div>
          </div>
          <div className="dashboard-card">
            <h3>COE analyses</h3>
            <div className="value">{stats.coe_analyses_count}</div>
          </div>
        </div>
        {Object.keys(breakdown).length > 0 && (
          <div className="dashboard-card" style={{ marginBottom: '1rem' }}>
            <h3>Complexity</h3>
            <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
              {Object.entries(breakdown).map(([k, v]) => (
                <span key={k}>{k}: <strong>{v}</strong></span>
              ))}
            </div>
          </div>
        )}
        <ReportList />
      </div>
    </main>
  );
}
