import React from 'react';
import AdvisorChat from '../components/AdvisorChat';

export default function AIAdvisor() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div className="top-bar">
        <h2>🤖 AI Advisor</h2>
        <span style={{ marginLeft: '12px', fontSize: '12px', color: 'var(--text-muted)', background: 'rgba(59,130,246,0.1)', padding: '2px 8px', borderRadius: '4px', border: '1px solid rgba(59,130,246,0.2)' }}>
          IBM Granite · watsonx.ai
        </span>
        <span style={{ marginLeft: 'auto', fontSize: '12px', color: 'var(--text-muted)' }}>
          Powered by real-time grid data
        </span>
      </div>
      <div style={{ flex: 1, padding: '16px', display: 'flex', gap: '16px', overflow: 'hidden' }}>
        {/* Chat panel */}
        <div className="glass-card" style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '14px 16px', borderBottom: '1px solid var(--glass-border)', fontSize: '13px', fontWeight: 600, color: 'var(--text-secondary)' }}>
            💬 Grid AI Chat
          </div>
          <AdvisorChat />
        </div>

        {/* Info panel */}
        <div style={{ width: '280px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div className="glass-card">
            <div style={{ fontSize: '13px', fontWeight: 600, marginBottom: '12px' }}>What can I ask?</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px', color: 'var(--text-secondary)' }}>
              {[
                '🔴 Which asset needs immediate inspection?',
                '🌩 How does current weather affect risk?',
                '🏥 Which critical facilities are at risk?',
                '👷 What should the maintenance team do today?',
                '🔗 What happens if TX-001 fails?',
                '📈 What is the cascade risk for this asset?',
              ].map((q, i) => (
                <div key={i} style={{ padding: '8px', background: 'rgba(15,23,42,0.5)', borderRadius: '6px' }}>{q}</div>
              ))}
            </div>
          </div>

          <div className="glass-card">
            <div style={{ fontSize: '13px', fontWeight: 600, marginBottom: '8px' }}>AI Model</div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: '1.8' }}>
              <div>Model: <span style={{ color: 'var(--blue-glow)' }}>IBM Granite 13B Instruct</span></div>
              <div>Platform: <span style={{ color: 'var(--blue-glow)' }}>watsonx.ai</span></div>
              <div>Fallback: <span style={{ color: 'var(--green)' }}>Local Rule Engine</span></div>
              <div style={{ marginTop: '8px', fontSize: '11px', color: 'var(--text-muted)' }}>
                Always uses live grid data as context. Never uses hardcoded responses.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
