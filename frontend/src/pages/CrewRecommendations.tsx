import React, { useEffect, useState } from 'react';
import { getRecommendations, getAssetWorkOrders } from '../services/api';
import WorkOrderRow from '../components/WorkOrderRow';
import type { WorkOrder } from '../types';
import RiskBadge from '../components/RiskBadge';

export default function CrewRecommendations() {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [workOrders, setWorkOrders] = useState<WorkOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      getRecommendations(),
    ])
      .then(([recs]) => {
        setRecommendations(recs.work_orders ?? []);
        const assetIds = [...new Set((recs.work_orders ?? []).map((r: any) => r.asset_id))] as string[];
        return Promise.all(assetIds.map((aid: string) => getAssetWorkOrders(aid).catch(() => [])));
      })
      .then(wos => setWorkOrders(wos.flat()))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const updateWO = (updated: WorkOrder) => {
    setWorkOrders(prev => prev.map(wo => wo.id === updated.id ? updated : wo));
  };

  const openWorkOrders = workOrders.filter(wo => wo.status !== 'completed' && wo.status !== 'cancelled');
  const completedWorkOrders = workOrders.filter(wo => wo.status === 'completed' || wo.status === 'cancelled');

  return (
    <div>
      <div className="top-bar">
        <h2>👷 Crew & Recommendations</h2>
        <span className="text-muted text-sm" style={{ marginLeft: 'auto' }}>
          {recommendations.filter(r => r.priority === 'critical').length} critical · {recommendations.filter(r => r.priority === 'high').length} high priority
        </span>
      </div>
      <div className="page-content">
        {loading && <div className="loading-state"><div className="spinner" /> Loading...</div>}
        {error && <div className="error-state">⚠ {error}</div>}
        {!loading && !error && (
          <>
            {/* Recommended actions */}
            <div className="glass-card mb-6">
              <div className="section-header">
                <span className="section-title">Auto-Generated Work Order Recommendations</span>
              </div>
              <table className="data-table">
                <thead>
                  <tr><th>Asset</th><th>Risk</th><th>Priority</th><th>Recommended Action</th></tr>
                </thead>
                <tbody>
                  {recommendations.length === 0 ? (
                    <tr><td colSpan={4}><div className="empty-state">No recommendations available</div></td></tr>
                  ) : (
                    recommendations.map((r: any) => (
                      <tr key={r.asset_id}>
                        <td>
                          <span style={{ color: 'var(--blue-glow)' }}>{r.asset_id}</span>
                          <div className="text-muted text-sm">{r.asset_name}</div>
                        </td>
                        <td><RiskBadge level={r.risk_level ?? 'LOW'} score={r.final_risk_score} /></td>
                        <td><span className={`risk-badge ${r.priority?.toUpperCase()}`}>{r.priority}</span></td>
                        <td className="text-sm">{r.action}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* Crew staging plan */}
            <div className="glass-card mb-6">
              <div className="section-header">
                <span className="section-title">48-Hour Crew Staging Plan</span>
              </div>
              <div className="grid-3 gap-6">
                {[
                  { name: 'North Operations Center', zone: 'North', critical: recommendations.filter(r => r.risk_level === 'CRITICAL').length },
                  { name: 'East Metro Depot',         zone: 'East',  critical: recommendations.filter(r => r.risk_level === 'HIGH').length },
                  { name: 'West Valley Station',      zone: 'West',  critical: recommendations.filter(r => r.risk_level === 'MEDIUM').length },
                ].map(hub => (
                  <div key={hub.name} className="weather-alert-item" style={{ background: 'rgba(15,23,42,0.6)', border: '1px solid var(--glass-border)' }}>
                    <div className="font-semibold" style={{ marginBottom: '6px' }}>{hub.name}</div>
                    <div className="text-muted text-sm">Zone: {hub.zone}</div>
                    <div style={{ marginTop: '8px' }} className="text-sm">
                      <span style={{ color: hub.critical > 0 ? 'var(--risk-critical)' : 'var(--green)', fontWeight: 600 }}>
                        {hub.critical} deployment{hub.critical !== 1 ? 's' : ''} needed
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Open Work Orders table */}
            <div className="glass-card mb-6">
              <div className="section-header">
                <span className="section-title">Open Work Orders ({openWorkOrders.length})</span>
              </div>
              {openWorkOrders.length === 0 ? (
                <div className="empty-state">No open work orders</div>
              ) : (
                <table className="data-table">
                  <thead>
                    <tr><th>#</th><th>Asset</th><th>Priority</th><th>Description</th><th>Assigned To</th><th>Status</th></tr>
                  </thead>
                  <tbody>
                    {openWorkOrders.map(wo => (
                      <WorkOrderRow key={wo.id} workOrder={wo} onUpdated={updateWO} />
                    ))}
                  </tbody>
                </table>
              )}
            </div>

            {/* Completed Work Orders table */}
            <div className="glass-card">
              <div className="section-header">
                <span className="section-title">Completed & Closed Work Orders ({completedWorkOrders.length})</span>
              </div>
              {completedWorkOrders.length === 0 ? (
                <div className="empty-state">No completed work orders</div>
              ) : (
                <table className="data-table">
                  <thead>
                    <tr><th>#</th><th>Asset</th><th>Priority</th><th>Description</th><th>Assigned To</th><th>Status</th></tr>
                  </thead>
                  <tbody>
                    {completedWorkOrders.map(wo => (
                      <WorkOrderRow key={wo.id} workOrder={wo} onUpdated={updateWO} />
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

