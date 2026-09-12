import React, { useEffect, useState } from 'react';
import { getAllRiskScores } from '../services/api';
import type { RiskSummaryItem } from '../types';
import RiskBadge from '../components/RiskBadge';
import { useNavigate } from 'react-router-dom';

export default function RiskAnalysis() {
  const [data, setData] = useState<{ risk_scores: RiskSummaryItem[]; critical_count: number; high_count: number; medium_count: number; low_count: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    getAllRiskScores()
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div><div className="top-bar"><h2>Risk Analysis</h2></div>
      <div className="page-content"><div className="loading-state"><div className="spinner" /> Computing risk scores...</div></div></div>
  );
  if (error) return (
    <div><div className="top-bar"><h2>Risk Analysis</h2></div>
      <div className="page-content"><div className="error-state">⚠ {error}</div></div></div>
  );

  const scores = data?.risk_scores ?? [];

  return (
    <div>
      <div className="top-bar"><h2>📊 Risk Analysis</h2>
        <span style={{ marginLeft: 'auto', fontSize: '12px', color: 'var(--text-muted)' }}>{scores.length} assets ranked</span>
      </div>
      <div className="page-content">
        {/* Summary */}
        <div className="grid-4 mb-6">
          {[
            { label: 'CRITICAL', count: data?.critical_count ?? 0, color: 'var(--risk-critical)' },
            { label: 'HIGH',     count: data?.high_count ?? 0,     color: 'var(--risk-high)' },
            { label: 'MEDIUM',   count: data?.medium_count ?? 0,   color: 'var(--risk-medium)' },
            { label: 'LOW',      count: data?.low_count ?? 0,      color: 'var(--risk-low)' },
          ].map(item => (
            <div key={item.label} className="stat-card">
              <div className="stat-label">{item.label}</div>
              <div className="stat-value" style={{ color: item.color }}>{item.count}</div>
            </div>
          ))}
        </div>

        {/* Risk table */}
        <div className="glass-card">
          <div className="section-title mb-4">Risk Score Rankings</div>
          <table className="data-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Asset</th>
                <th>Type</th>
                <th>Risk Level</th>
                <th>Final Score</th>
                <th>Failure Prob</th>
                <th>Grid Impact</th>
                <th>Cascade Risk</th>
              </tr>
            </thead>
            <tbody>
              {scores.length === 0 ? (
                <tr><td colSpan={8}><div className="empty-state">No risk scores available. Ensure the database is seeded.</div></td></tr>
              ) : (
                scores.map((s, idx) => (
                  <tr key={s.asset_id} style={{ cursor: 'pointer' }} onClick={() => navigate(`/assets/${s.asset_id}`)}>
                    <td className="text-muted">{idx + 1}</td>
                    <td>
                      <span style={{ color: 'var(--blue-glow)', fontFamily: 'monospace' }}>{s.asset_id}</span>
                      <div className="text-muted text-sm">{s.asset_name}</div>
                    </td>
                    <td className="text-muted">{s.asset_type}</td>
                    <td><RiskBadge level={s.risk_level} /></td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div style={{ width: '60px', height: '6px', background: 'rgba(99,179,237,0.1)', borderRadius: '3px' }}>
                          <div style={{ width: `${s.final_risk_score * 100}%`, height: '100%', background: s.risk_level === 'CRITICAL' ? 'var(--risk-critical)' : s.risk_level === 'HIGH' ? 'var(--risk-high)' : s.risk_level === 'MEDIUM' ? 'var(--risk-medium)' : 'var(--risk-low)', borderRadius: '3px' }} />
                        </div>
                        <span style={{ fontWeight: 600 }}>{(s.final_risk_score * 100).toFixed(1)}%</span>
                      </div>
                    </td>
                    <td>{(s.failure_probability * 100).toFixed(1)}%</td>
                    <td>{(s.grid_impact * 100).toFixed(1)}%</td>
                    <td>{(s.cascade_risk * 100).toFixed(1)}%</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
