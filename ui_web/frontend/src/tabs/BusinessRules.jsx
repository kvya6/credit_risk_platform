import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

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

export default function BusinessRules() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    fetch('/api/rules')
      .then(r => r.json())
      .then(d => { if (d.error) setError(d.error); else setData(d); setLoading(false); })
      .catch(() => { setError('Failed to load business rules.'); setLoading(false); });
  }, []);

  if (loading) return <div className="loading-text"><span className="spinner" />Deriving business rules from ML model...</div>;
  if (error)   return <div className="alert alert-error">{error}</div>;

  const { top_features, high_risk_rules, low_risk_rules, raw_rules } = data;

  return (
    <div>
      <div className="hero-glass">
        <div className="hero-title">Business Decision Rules</div>
        <div className="hero-sub">IF-THEN credit policy rules derived from ML — readable by analysts, auditors & regulators</div>
      </div>

      <div className="alert alert-info">
        A shallow decision tree is fitted on LightGBM's predictions to produce transparent IF-THEN rules
        suitable for credit policy documentation and regulatory review.
      </div>

      {/* Top features */}
      <div className="section-title">Top Features Used in Rules</div>
      <div className="charts-grid-2">
        <div className="glass">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={[...top_features].reverse()} layout="vertical"
              margin={{ top: 5, right: 20, left: 160, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,179,237,0.08)" />
              <XAxis type="number" stroke="#475569" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis type="category" dataKey="feature" stroke="#475569"
                tick={{ fill: '#94a3b8', fontSize: 11 }} width={160} />
              <Tooltip {...GLASS_TOOLTIP} formatter={v => [v.toFixed(5), 'Importance']} />
              <Bar dataKey="importance" fill="#a78bfa" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="glass">
          <strong style={{ color: '#63b3ed', fontSize: '0.85rem' }}>How rules are derived</strong>
          <div style={{ color: '#64748b', fontSize: '0.83rem', lineHeight: 1.85, marginTop: '0.8rem' }}>
            <p>1. LightGBM predicts default probability on training data</p>
            <p>2. A shallow decision tree (depth ≤ 4) is fitted on those predictions</p>
            <p>3. Each path from root to leaf becomes a business rule</p>
            <p>4. Rules with ≥ 500 applicants are kept for statistical stability</p>
          </div>
        </div>
      </div>

      <hr />

      {/* Rules */}
      <div className="section-title">Derived IF-THEN Rules</div>
      <div className="charts-grid-2">
        <div>
          <div style={{ color: '#f87171', fontSize: '0.82rem', fontWeight: 700, marginBottom: '0.7rem' }}>
            🔴 High-Risk Rules (Decline / Review)
          </div>
          {high_risk_rules.map((rule, i) => (
            <RuleCard rule={rule} variant="high" key={i} />
          ))}
        </div>
        <div>
          <div style={{ color: '#2dd4bf', fontSize: '0.82rem', fontWeight: 700, marginBottom: '0.7rem' }}>
            🟢 Low-Risk Rules (Approve)
          </div>
          {low_risk_rules.map((rule, i) => (
            <RuleCard rule={rule} variant="low" key={i} />
          ))}
        </div>
      </div>

      {/* Raw rules expander */}
      {raw_rules && (
        <>
          <div className="expander-header" onClick={() => setExpanded(e => !e)}>
            <span>📄 View Full Rule Tree (Raw)</span>
            <span>{expanded ? '▲' : '▼'}</span>
          </div>
          {expanded && <div className="expander-body">{raw_rules}</div>}
        </>
      )}
    </div>
  );
}

function RuleCard({ rule, variant }) {
  return (
    <div className={`rule-card rule-${variant}`}>
      <div className="rule-outcome">
        {variant === 'high' ? '❌' : '✅'} {rule.outcome}
      </div>
      <div className="rule-conditions">
        {rule.conditions.map((c, i) => (
          <div key={i}>IF {c}</div>
        ))}
      </div>
      <div className="rule-stat">
        {rule.samples?.toLocaleString()} applicants · {rule.default_rate}% default rate
      </div>
    </div>
  );
}
