import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  ScatterChart, Scatter, ZAxis,
} from 'recharts';

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

export default function Explainability() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/explainability')
      .then(r => r.json())
      .then(d => { if (d.error) setError(d.error); else setData(d); setLoading(false); })
      .catch(() => { setError('Failed to load explainability data.'); setLoading(false); });
  }, []);

  if (loading) return <div className="loading-text"><span className="spinner" />Computing SHAP on 500-applicant sample...</div>;
  if (error)   return <div className="alert alert-error">{error}</div>;

  const { global_importance, beeswarm } = data;
  const sortedImp = [...global_importance].sort((a, b) => a.importance - b.importance);

  return (
    <div>
      <div className="hero-glass">
        <div className="hero-title">Model Explainability — SHAP</div>
        <div className="hero-sub">Understand which features drive each prediction · Satisfies audit & regulatory requirements</div>
      </div>

      <div className="alert alert-info">
        SHAP (SHapley Additive exPlanations) assigns each feature a contribution score.
        Red = pushes risk up · Blue = pushes risk down.
      </div>

      {/* Global Feature Importance */}
      <div className="section-title">Global Feature Importance</div>
      <div className="glass">
        <ResponsiveContainer width="100%" height={440}>
          <BarChart data={sortedImp} layout="vertical" margin={{ top: 5, right: 20, left: 160, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,179,237,0.08)" />
            <XAxis type="number" stroke="#475569" tick={{ fill: '#64748b', fontSize: 11 }} />
            <YAxis type="category" dataKey="feature" stroke="#475569"
              tick={{ fill: '#94a3b8', fontSize: 11 }} width={160} />
            <Tooltip {...GLASS_TOOLTIP} formatter={v => [v.toFixed(5), 'Mean |SHAP|']} />
            <Bar dataKey="importance" fill="#8b5cf6" radius={[0, 6, 6, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Beeswarm approximation using scatter */}
      <div className="section-title">SHAP Beeswarm Summary (Top 10 Features)</div>
      <div className="glass">
        <BeeswarmChart beeswarm={beeswarm} />
      </div>

      <hr />
      <div className="charts-grid-2">
        <div className="glass">
          <strong style={{ color: '#63b3ed', fontSize: '0.85rem' }}>How to read this chart</strong>
          <ul style={{ color: '#64748b', fontSize: '0.82rem', lineHeight: 2, marginTop: '0.6rem', paddingLeft: '1.2rem' }}>
            <li>Features ranked top-to-bottom by total impact</li>
            <li><span style={{ color: '#ef4444' }}>Red dots</span> = high feature value → higher default risk</li>
            <li><span style={{ color: '#3b82f6' }}>Blue dots</span> = low feature value → lower default risk</li>
            <li>Wider spread = more variable impact across applicants</li>
          </ul>
        </div>
        <div className="glass">
          <strong style={{ color: '#a78bfa', fontSize: '0.85rem' }}>Key predictors</strong>
          <ul style={{ color: '#64748b', fontSize: '0.82rem', lineHeight: 2, marginTop: '0.6rem', paddingLeft: '1.2rem' }}>
            <li><code>Credit Bureau Scores 1/2/3</code> — External credit history scores</li>
            <li><code>Repayment-to-Income Ratio</code> — Higher burden = higher risk</li>
            <li><code>Applicant Age (years)</code> — Younger applicants = higher risk</li>
            <li><code>Loan Amount</code> — Larger loans = higher risk</li>
            <li><code>Years Employed</code> — Longer employment = lower risk</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

// Visual approximation of beeswarm using horizontal scatter strips
function BeeswarmChart({ beeswarm }) {
  if (!beeswarm?.length) return null;

  return (
    <div>
      {beeswarm.map((feat, fi) => {
        const vals = feat.shap_values;
        const fVals = feat.feature_values;
        const minF = Math.min(...fVals.filter(v => v != null));
        const maxF = Math.max(...fVals.filter(v => v != null)) || 1;

        return (
          <div key={fi} style={{ marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ width: '175px', textAlign: 'right', fontSize: '0.78rem', color: '#94a3b8', flexShrink: 0 }}>
              {feat.feature}
            </div>
            <div style={{ flex: 1, height: '18px', position: 'relative', background: 'rgba(255,255,255,0.03)', borderRadius: '4px', overflow: 'hidden' }}>
              {vals.slice(0, 150).map((sv, i) => {
                const fv = fVals[i];
                const norm = maxF === minF ? 0.5 : ((fv ?? minF) - minF) / (maxF - minF);
                // color: red for high feat value, blue for low
                const r = Math.round(norm * 239 + (1 - norm) * 59);
                const g = Math.round(norm * 68  + (1 - norm) * 130);
                const b = Math.round(norm * 68  + (1 - norm) * 246);
                // x position based on shap value
                const minSv = Math.min(...vals);
                const maxSv = Math.max(...vals);
                const range = maxSv - minSv || 0.001;
                const x = ((sv - minSv) / range) * 100;
                return (
                  <div key={i} style={{
                    position: 'absolute',
                    left: `${x}%`,
                    top: '50%',
                    transform: 'translate(-50%, -50%)',
                    width: '4px', height: '4px',
                    borderRadius: '50%',
                    background: `rgb(${r},${g},${b})`,
                    opacity: 0.7,
                  }} />
                );
              })}
            </div>
          </div>
        );
      })}
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '16px', marginTop: '8px', fontSize: '0.72rem', color: '#475569' }}>
        <span style={{ color: '#3b82f6' }}>● Low feature value</span>
        <span style={{ color: '#ef4444' }}>● High feature value</span>
      </div>
    </div>
  );
}
