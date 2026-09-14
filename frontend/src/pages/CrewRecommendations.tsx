import React, { useEffect, useState } from 'react';
import { getRecommendations, getAssetWorkOrders, getCrewPrepositionPlan } from '../services/api';
import WorkOrderRow from '../components/WorkOrderRow';
import type { WorkOrder } from '../types';
import RiskBadge from '../components/RiskBadge';

export default function CrewRecommendations() {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [crewPlan, setCrewPlan] = useState<any | null>(null);
  const [workOrders, setWorkOrders] = useState<WorkOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      getRecommendations().catch(() => ({ work_orders: [] })),
      getCrewPrepositionPlan().catch(() => null),
    ])
      .then(([recs, plan]) => {
        setRecommendations(recs.work_orders ?? []);
        setCrewPlan(plan);
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
                      <tr key={r.asset_id} className={`risk-row-${(r.risk_level ?? 'LOW').toLowerCase()}`}>
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
                <span className="section-title">⚡ 48-Hour Crew Pre-Positioning Plan</span>
                {crewPlan?.summary && (
                  <span className="text-muted text-sm" style={{ marginLeft: 'auto' }}>
                    {crewPlan.summary}
                  </span>
                )}
              </div>

              {crewPlan?.assignments && crewPlan.assignments.length > 0 ? (
                <div style={{ overflowX: 'auto' }}>
                  <table className="data-table mb-4">
                    <thead>
                      <tr>
                        <th>Crew</th>
                        <th>Target Asset</th>
                        <th>Priority</th>
                        <th>Staging Hub</th>
                        <th>Staging Window</th>
                        <th>Weather Threat</th>
                        <th>Reason</th>
                      </tr>
                    </thead>
                    <tbody>
                      {crewPlan.assignments.map((asgn: any) => (
                        <tr key={asgn.crew_id}>
                          <td>
                            <strong>{asgn.crew_name}</strong>
                            <div className="text-muted text-xs">{asgn.crew_id}</div>
                          </td>
                          <td>
                            <span style={{ color: 'var(--blue-glow)', fontWeight: 600 }}>{asgn.target_asset_id}</span>
                            <div className="text-muted text-xs">{asgn.target_asset_name}</div>
                          </td>
                          <td>
                            <span className={`risk-badge ${asgn.priority?.toUpperCase()}`}>{asgn.priority}</span>
                          </td>
                          <td>
                            <span style={{ color: 'var(--text-primary)' }}>{asgn.suggested_staging_hub}</span>
                          </td>
                          <td>
                            <span className="text-sm font-mono">{asgn.recommended_staging_window}</span>
                          </td>
                          <td className="text-sm">
                            {asgn.weather_threat}
                          </td>
                          <td className="text-xs text-muted" style={{ maxWidth: '300px' }}>
                            {asgn.reason}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : null}

              <div className="grid-3 gap-6">
                {[
                  { name: 'North Operations Center', zone: 'North Sector', description: 'Covers High-Voltage Substations & Industrial feeds' },
                  { name: 'East Metro Depot',         zone: 'East Metro',  description: 'Covers Critical Facilities & Hospital Feeders' },
                  { name: 'West Valley Station',      zone: 'West Rural',  description: 'Covers Heavy Rainfall & Wind-Exposed Lines' },
                ].map(hub => {
                  const hubCount = crewPlan?.assignments?.filter((a: any) => a.suggested_staging_hub?.toLowerCase().includes(hub.name.toLowerCase().split(' ')[0].toLowerCase())).length ?? 0;
                  return (
                    <div key={hub.name} className="weather-alert-item" style={{ background: 'rgba(15,23,42,0.6)', border: '1px solid var(--glass-border)' }}>
                      <div className="font-semibold" style={{ marginBottom: '4px' }}>{hub.name}</div>
                      <div className="text-muted text-xs">{hub.zone} · {hub.description}</div>
                      <div style={{ marginTop: '8px' }} className="text-sm">
                        <span style={{ color: hubCount > 0 ? 'var(--risk-critical)' : 'var(--green)', fontWeight: 600 }}>
                          {hubCount} crew{hubCount !== 1 ? 's' : ''} pre-positioned
                        </span>
                      </div>
                    </div>
                  );
                })}
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

