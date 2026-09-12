import React, { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '../services/api';

interface Message {
  role: 'user' | 'ai';
  text: string;
  provider?: string;
  timestamp: string;
}

export default function AdvisorChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'ai',
      text: 'Hello! I\'m GridPulse AI, your intelligent power grid advisor. Ask me about asset risks, crew deployment, weather impacts, or cascade failures.',
      provider: 'IBM Granite',
      timestamp: new Date().toISOString(),
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const send = async () => {
    if (!input.trim() || loading) return;
    const userMsg: Message = { role: 'user', text: input, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    const userInput = input;
    setInput('');
    setLoading(true);

    try {
      const resp = await sendChatMessage(userInput);
      setMessages(prev => [...prev, {
        role: 'ai',
        text: resp.response,
        provider: resp.provider,
        timestamp: resp.timestamp,
      }]);
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'ai',
        text: 'Unable to reach GridPulse AI backend. Please check the API server.',
        provider: 'Error',
        timestamp: new Date().toISOString(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
  };

  const suggestions = [
    'Which asset should we inspect first?',
    'What critical facilities are at risk?',
    'How does weather affect risk scores?',
    'What maintenance is needed this week?',
  ];

  return (
    <div className="flex-col" style={{ height: '100%', gap: 0 }}>
      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {messages.map((msg, i) => (
          <div key={i} style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
            <div style={{
              maxWidth: '80%',
              padding: '12px 16px',
              borderRadius: msg.role === 'user' ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
              background: msg.role === 'user'
                ? 'rgba(59,130,246,0.25)'
                : 'rgba(15,30,60,0.8)',
              border: '1px solid ' + (msg.role === 'user' ? 'rgba(59,130,246,0.3)' : 'var(--glass-border)'),
              fontSize: '13px',
              lineHeight: '1.6',
            }}>
              <div>{msg.text}</div>
              {msg.provider && (
                <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '6px' }}>
                  {msg.provider} · {new Date(msg.timestamp).toLocaleTimeString()}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center', color: 'var(--text-muted)' }}>
            <div className="spinner" />
            <span style={{ fontSize: '12px' }}>GridPulse AI is thinking...</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Suggestions */}
      {messages.length <= 2 && (
        <div style={{ padding: '8px 16px', display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
          {suggestions.map((s, i) => (
            <button key={i} className="btn btn-ghost" style={{ fontSize: '11px', padding: '4px 10px' }}
              onClick={() => { setInput(s); }}>
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input area */}
      <div style={{ padding: '12px 16px', borderTop: '1px solid var(--glass-border)', display: 'flex', gap: '8px' }}>
        <input
          className="input"
          style={{ flex: 1 }}
          placeholder="Ask about assets, risks, weather, crew deployment..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          disabled={loading}
        />
        <button className="btn btn-primary" onClick={send} disabled={loading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}
