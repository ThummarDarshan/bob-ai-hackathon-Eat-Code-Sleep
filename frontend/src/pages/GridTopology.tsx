import React, { useEffect, useState } from 'react';
import { getGridTopology, getCascadeImpact } from '../services/api';
import type { GridTopology, GridNode, GridEdge, CascadeImpact } from '../types';
import RiskBadge from '../components/RiskBadge';

const RISK_COLORS: Record<string, string> = {
  CRITICAL: '#ef4444',
  HIGH: '#f97316',
  MEDIUM: '#f59e0b',
  LOW: '#10b981',
  undefined: '#3b82f6',
};

const TYPE_SHAPES: Record<string, string> = {
  Substation: '■',
  Transformer: '◆',
  Feeder: '—',
  CriticalFacility: '✚',
};

function normalizeCoords(nodes: GridNode[], width: number, height: number) {
  if (nodes.length === 0) return {};
  const lats = nodes.map(n => n.latitude ?? 0).filter(Boolean);
  const lons = nodes.map(n => n.longitude ?? 0).filter(Boolean);
  if (!lats.length || !lons.length) {
    // Evenly space nodes in a circle if no coords
    const pos: Record<string, { x: number; y: number }> = {};
    nodes.forEach((n, i) => {
      const angle = (2 * Math.PI * i) / nodes.length - Math.PI / 2;
      pos[n.id] = { x: width / 2 + (width * 0.35) * Math.cos(angle), y: height / 2 + (height * 0.35) * Math.sin(angle) };
    });
    return pos;
  }
  const minLat = Math.min(...lats), maxLat = Math.max(...lats);
  const minLon = Math.min(...lons), maxLon = Math.max(...lons);
  const pad = 60;
  const pos: Record<string, { x: number; y: number }> = {};
  nodes.forEach(n => {
    const latRange = maxLat - minLat || 0.01;
    const lonRange = maxLon - minLon || 0.01;
    const x = pad + ((n.longitude ?? minLon) - minLon) / lonRange * (width - 2 * pad);
    const y = pad + (1 - ((n.latitude ?? minLat) - minLat) / latRange) * (height - 2 * pad);
    pos[n.id] = { x, y };
  });
  return pos;
}

export default function GridTopologyPage() {
  const [topology, setTopology] = useState<GridTopology | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<GridNode | null>(null);
  const [cascade, setCascade] = useState<CascadeImpact | null>(null);
  const [cascadeLoading, setCascadeLoading] = useState(false);
  const [cascadeError, setCascadeError] = useState<string | null>(null);
  const SVG_W = 700, SVG_H = 420;

  useEffect(() => {
    getGridTopology()
      .then(setTopology)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const handleCascade = async (node: GridNode) => {
    setCascadeError(null);
    setCascade(null);
    setCascadeLoading(true);
    try {
      const result = await getCascadeImpact(node.id);
      setCascade(result);
    } catch (e: any) {
      setCascadeError(e.response?.data?.detail ?? e.message);
    } finally {
      setCascadeLoading(false);
    }
  };

  if (loading) return (
    <div><div className="top-bar"><h2>Grid Topology</h2></div>
      <div className="page-content"><div className="loading-state"><div className="spinner" /> Loading grid topology...</div></div></div>
  );
  if (error) return (
    <div><div className="top-bar"><h2>Grid Topology</h2></div>
      <div className="page-content"><div className="error-state">⚠ {error}<br /><span className="text-sm text-muted">Ensure Neo4j is running and the grid has been seeded.</span></div></div></div>
  );

  const nodes = topology?.nodes ?? [];
  const edges = topology?.edges ?? [];
  const positions = normalizeCoords(nodes, SVG_W, SVG_H);
  const cascadePath = cascade ? new Set(cascade.cascade_path) : new Set<string>();

  return (
    <div>
      <div className="top-bar">
        <h2>🗺️ Grid Topology</h2>
        <span style={{ marginLeft: 'auto', fontSize: '12px', color: 'var(--text-muted)' }}>
          {nodes.length} nodes · {edges.length} connections
        </span>
      </div>
      <div className="page-content" style={{ display: 'flex', gap: '16px' }}>
        {/* SVG Map */}
        <div className="glass-card" style={{ flex: 1 }}>
          <div className="section-header">
            <span className="section-title">Grid Topology Map</span>
            <span className="text-sm text-muted">Click a node to inspect · Use "Analyze Cascade" for failure simulation</span>
          </div>
          <svg
            width="100%"
            viewBox={`0 0 ${SVG_W} ${SVG_H}`}
            style={{ background: 'rgba(10,14,26,0.5)', borderRadius: '8px', border: '1px solid var(--glass-border)' }}
          >
            {/* Edges */}
            {edges.map((edge, i) => {
              const src = positions[edge.source];
              const tgt = positions[edge.target];
              if (!src || !tgt) return null;
              const isInCascade = cascadePath.has(edge.source) && cascadePath.has(edge.target);
              return (
                <line
                  key={i}
                  x1={src.x} y1={src.y}
                  x2={tgt.x} y2={tgt.y}
                  stroke={isInCascade ? '#ef4444' : 'rgba(99,179,237,0.25)'}
                  strokeWidth={isInCascade ? 3 : 1.5}
                  strokeDasharray={edge.type === 'CONNECTS_TO' ? '6 3' : undefined}
                />
              );
            })}

            {/* Nodes */}
            {nodes.map(node => {
              const pos = positions[node.id];
              if (!pos) return null;
              const color = RISK_COLORS[node.risk_level ?? 'undefined'];
              const isSelected = selected?.id === node.id;
              const inCascade = cascadePath.has(node.id);

              return (
                <g key={node.id} style={{ cursor: 'pointer' }} onClick={() => setSelected(node)}>
                  <circle
                    cx={pos.x} cy={pos.y}
                    r={isSelected ? 16 : 12}
                    fill={color + '33'}
                    stroke={inCascade ? '#ef4444' : isSelected ? color : color + '99'}
                    strokeWidth={isSelected || inCascade ? 3 : 1.5}
                  />
                  <text x={pos.x} y={pos.y + 4} textAnchor="middle" fill={color} fontSize="11" fontWeight="700">
                    {node.type?.charAt(0) ?? '?'}
                  </text>
                  <text x={pos.x} y={pos.y + 24} textAnchor="middle" fill="rgba(241,245,249,0.7)" fontSize="9">
                    {node.id}
                  </text>
                </g>
              );
            })}
          </svg>

          {/* Legend */}
          <div style={{ display: 'flex', gap: '16px', marginTop: '12px', flexWrap: 'wrap', fontSize: '11px', color: 'var(--text-muted)' }}>
            {Object.entries(RISK_COLORS).filter(([k]) => k !== 'undefined').map(([lvl, clr]) => (
              <span key={lvl} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: clr, display: 'inline-block' }} />
                {lvl}
              </span>
            ))}
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <span style={{ width: '20px', height: '2px', background: 'rgba(99,179,237,0.4)', display: 'inline-block', borderTop: '2px dashed rgba(99,179,237,0.4)' }} />
              CONNECTS_TO
            </span>
          </div>
        </div>

        {/* Detail + Cascade panel */}
        <div style={{ width: '320px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {/* Selected node info */}
          {selected ? (
            <div className="glass-card">
              <div className="section-header">
                <span className="section-title">{selected.name ?? selected.id}</span>
              </div>
              <div style={{ fontSize: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div className="flex justify-between"><span className="text-muted">ID</span><span style={{ fontFamily: 'monospace', color: 'var(--blue-glow)' }}>{selected.id}</span></div>
                <div className="flex justify-between"><span className="text-muted">Type</span><span>{selected.type}</span></div>
                <div className="flex justify-between"><span className="text-muted">Status</span><span style={{ color: selected.status === 'active' ? 'var(--green)' : 'var(--amber)' }}>{selected.status}</span></div>
                {selected.risk_level && <div className="flex justify-between"><span className="text-muted">Risk</span><RiskBadge level={selected.risk_level} /></div>}
                {selected.final_risk_score !== undefined && <div className="flex justify-between"><span className="text-muted">Score</span><span style={{ fontWeight: 600 }}>{(selected.final_risk_score * 100).toFixed(1)}%</span></div>}
                {selected.capacity && <div className="flex justify-between"><span className="text-muted">Capacity</span><span>{selected.capacity} MVA</span></div>}
                {selected.critical_facility && <div style={{ marginTop: '4px' }}><span style={{ color: 'var(--risk-critical)', fontSize: '11px' }}>⚠ Critical Facility: {selected.facility_type}</span></div>}
              </div>
              <button
                className="btn btn-danger"
                style={{ width: '100%', marginTop: '12px', justifyContent: 'center' }}
                onClick={() => handleCascade(selected)}
                disabled={cascadeLoading}
              >
                {cascadeLoading ? <><div className="spinner" /> Analyzing...</> : '🔗 Analyze Cascade Failure'}
              </button>
            </div>
          ) : (
            <div className="glass-card" style={{ textAlign: 'center' }}>
              <div className="empty-state" style={{ flexDirection: 'column', gap: '8px' }}>
                <div style={{ fontSize: '24px' }}>🗺️</div>
                <div>Click a node on the map to inspect it</div>
              </div>
            </div>
          )}

          {/* Cascade result */}
          {cascadeError && (
            <div className="glass-card">
              <div className="error-state" style={{ height: 'auto', padding: '12px' }}>⚠ {cascadeError}</div>
            </div>
          )}
          {cascade && (
            <div className="glass-card">
              <div className="section-header">
                <span className="section-title">🔴 Cascade Impact Analysis</span>
              </div>
              <div style={{ fontSize: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div style={{ padding: '8px', background: 'rgba(239,68,68,0.08)', borderRadius: '6px', fontSize: '11px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                  {cascade.explanation}
                </div>
                <div className="grid-2 gap-2">
                  {[
                    ['Affected Assets', cascade.affected_asset_count, 'var(--risk-high)'],
                    ['Critical Facilities', cascade.critical_facility_count, 'var(--risk-critical)'],
                    ['Cascade Risk', (cascade.cascade_risk * 100).toFixed(0) + '%', 'var(--amber)'],
                    ['Grid Impact', (cascade.grid_impact * 100).toFixed(0) + '%', 'var(--blue-glow)'],
                    ['Depth', cascade.dependency_depth, 'var(--text-secondary)'],
                  ].map(([lbl, val, clr]) => (
                    <div key={lbl as string} style={{ padding: '6px', background: 'rgba(15,23,42,0.5)', borderRadius: '6px', textAlign: 'center' }}>
                      <div className="text-muted" style={{ fontSize: '10px' }}>{lbl}</div>
                      <div style={{ color: clr as string, fontWeight: 700 }}>{val}</div>
                    </div>
                  ))}
                </div>
                {cascade.affected_facilities.length > 0 && (
                  <div>
                    <div style={{ fontSize: '11px', color: 'var(--risk-critical)', marginBottom: '4px' }}>Affected Critical Facilities</div>
                    {cascade.affected_facilities.map(f => (
                      <div key={f.asset_id} style={{ fontSize: '11px', padding: '4px 6px', background: 'rgba(239,68,68,0.06)', borderRadius: '4px', marginBottom: '2px' }}>
                        {f.name} ({f.facility_type ?? f.asset_id})
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
