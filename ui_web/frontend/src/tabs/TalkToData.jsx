import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const EXAMPLE_QUESTIONS = [
  "What is the overall default rate?",
  "Which income type has the highest default rate?",
  "Average loan: male vs female?",
  "Default rate by education level?",
  "Top 5 occupations by applicant count?",
  "Average income: defaulters vs non-defaulters?",
  "How many own a car AND property?",
  "Default rate by region rating?",
  "What % of applicants have children?",
  "Loan amount distribution by contract type?",
];

const GLASS_TOOLTIP = {
  contentStyle: {
    background: 'rgba(8,15,30,0.92)',
    border: '1px solid rgba(99,179,237,0.2)',
    borderRadius: '10px',
    color: '#94a3b8',
    fontFamily: 'Syne, sans-serif',
    fontSize: '0.8rem',
  },
};

export default function TalkToData() {
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const ask = async (q) => {
    const query = q || question;
    if (!query.trim()) return;
    setLoading(true); setError(null); setResult(null);
    try {
      const res = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: query }),
      });
      const data = await res.json();
      if (data.error) setError(data.error);
      else setResult(data);
    } catch {
      setError('Failed to connect to backend.');
    }
    setLoading(false);
  };

  // Determine chart data
  const chartData = result?.data;
  let canChart = false, xKey = null, yKey = null;
  if (chartData?.length > 1 && chartData.length <= 50) {
    const keys = Object.keys(chartData[0] || {});
    const numKeys = keys.filter(k => typeof chartData[0][k] === 'number');
    const catKeys = keys.filter(k => typeof chartData[0][k] === 'string');
    if (numKeys.length && catKeys.length) {
      canChart = true; xKey = catKeys[0]; yKey = numKeys[0];
    }
  }

  return (
    <div>
      <div className="hero-glass">
        <div className="hero-title">Talk-to-Data Chatbot</div>
        <div className="hero-sub">Ask anything about the dataset in plain English — Groq AI converts it to SQL and explains the result</div>
      </div>

      {/* Connection status */}
      <div style={{ background: 'rgba(20,184,166,0.08)', border: '1px solid rgba(20,184,166,0.25)', borderRadius: '10px', padding: '0.5rem 1.2rem', marginBottom: '1.2rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span className="status-dot" style={{ background: '#14b8a6', flexShrink: 0 }} />
        <span style={{ color: '#2dd4bf', fontSize: '0.83rem' }}>Groq API · Llama-3 70B ready (requires GROQ_API_KEY in .env)</span>
      </div>

      {/* Example questions */}
      <div className="section-title">💡 Try These Questions</div>
      <div style={{ display: 'flex', flexWrap: 'wrap', marginBottom: '1rem' }}>
        {EXAMPLE_QUESTIONS.map((q, i) => (
          <button key={i} className="btn-sm" onClick={() => { setQuestion(q); ask(q); }}>
            ▸ {q}
          </button>
        ))}
      </div>

      <hr />

      {/* Input */}
      <div className="form-group">
        <label className="form-label">Or type your own question:</label>
        <div style={{ display: 'flex', gap: '0.8rem' }}>
          <input
            className="form-input"
            style={{ flex: 1 }}
            type="text"
            value={question}
            placeholder="e.g. Which region has the most defaulters?"
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && ask()}
          />
          <button className="btn-primary" style={{ width: 'auto', minWidth: '120px' }}
            onClick={() => ask()} disabled={loading || !question.trim()}>
            {loading ? <><span className="spinner" />Thinking...</> : '🔍 Ask Groq'}
          </button>
        </div>
      </div>

      {error && <div className="alert alert-error" style={{ marginTop: '1rem' }}>{error}</div>}

      {/* Results */}
      {result && (
        <div style={{ marginTop: '1.5rem' }}>
          <div className="charts-grid-2">
            <div>
              <div className="section-title" style={{ fontSize: '0.82rem' }}>Generated SQL</div>
              <div className="sql-glass">{result.sql}</div>
            </div>
            {result.summary && (
              <div>
                <div className="section-title" style={{ fontSize: '0.82rem' }}>Plain-English Answer</div>
                <div className="summary-glass">💬 {result.summary}</div>
              </div>
            )}
          </div>

          {result.data?.length > 0 && (
            <>
              <div className="section-title" style={{ marginTop: '1rem' }}>Query Results</div>
              <div className="glass" style={{ overflowX: 'auto' }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      {Object.keys(result.data[0]).map(k => <th key={k}>{k}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {result.data.slice(0, 50).map((row, i) => (
                      <tr key={i}>
                        {Object.values(row).map((v, j) => (
                          <td key={j}>{v == null ? '—' : typeof v === 'number' ? v.toLocaleString() : String(v)}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
                {result.data.length > 50 && (
                  <p style={{ color: '#475569', fontSize: '0.78rem', padding: '0.5rem', textAlign: 'center' }}>
                    Showing 50 of {result.data.length} rows
                  </p>
                )}
              </div>

              {canChart && (
                <div className="glass" style={{ marginTop: '0.5rem' }}>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 40 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,179,237,0.08)" />
                      <XAxis dataKey={xKey} stroke="#475569" tick={{ fill: '#64748b', fontSize: 11 }} angle={-20} textAnchor="end" />
                      <YAxis stroke="#475569" tick={{ fill: '#64748b', fontSize: 11 }} />
                      <Tooltip {...GLASS_TOOLTIP} />
                      <Bar dataKey={yKey} fill="#8b5cf6" radius={[6, 6, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
