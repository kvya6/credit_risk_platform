import React, { useState, useEffect } from 'react';
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  LineChart, Line, Legend,
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

export default function EDA() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/eda/summary')
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false); })
      .catch(() => { setError('Failed to load EDA data.'); setLoading(false); });
  }, []);

  if (loading) return <div className="loading-text"><span className="spinner" />Loading EDA data...</div>;
  if (error)   return <div className="alert alert-error">{error}</div>;
  if (data?.error) return <div className="alert alert-error">{data.error}</div>;

  const { kpis, target_dist, gender_default, age_default, edu_default,
          income_type_default, insights } = data;

  return (
    <div>
      <div className="hero-glass">
        <div className="hero-title">Exploratory Data Analysis</div>
        <div className="hero-sub">Home Credit Default Risk — 300K applicants · 122 features · 8% default rate</div>
      </div>

      {/* KPIs */}
      <div className="kpi-grid">
        <div className="kpi-glass kpi-blue">
          <div className="kpi-label">Total Applicants</div>
          <div className="kpi-value">{kpis.total_applicants.toLocaleString()}</div>
        </div>
        <div className="kpi-glass kpi-rose">
          <div className="kpi-label">Default Rate</div>
          <div className="kpi-value">{kpis.default_rate}%</div>
        </div>
        <div className="kpi-glass kpi-purple">
          <div className="kpi-label">Avg Loan Amount</div>
          <div className="kpi-value">₹{(kpis.avg_loan / 1e5).toFixed(1)}L</div>
        </div>
        <div className="kpi-glass kpi-teal">
          <div className="kpi-label">Avg Annual Income</div>
          <div className="kpi-value">₹{(kpis.avg_income / 1e5).toFixed(1)}L</div>
        </div>
      </div>

      {/* Row 1 */}
      <div className="charts-grid-2">
        <div className="glass">
          <div className="section-title">Target Distribution</div>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={target_dist} dataKey="value" nameKey="name" cx="50%" cy="50%"
                   innerRadius={65} outerRadius={95} paddingAngle={3}>
                <Cell fill="#3b82f6" />
                <Cell fill="#ef4444" />
              </Pie>
              <Tooltip {...GLASS_TOOLTIP} />
              <Legend wrapperStyle={{ color: '#64748b', fontSize: '0.8rem' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="glass">
          <div className="section-title">Default Rate by Gender</div>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={gender_default} margin={{ top: 10, right: 10, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,179,237,0.08)" />
              <XAxis dataKey="gender" stroke="#475569" tick={{ fill: '#64748b', fontSize: 12 }} />
              <YAxis stroke="#475569" tick={{ fill: '#64748b', fontSize: 12 }} unit="%" />
              <Tooltip {...GLASS_TOOLTIP} formatter={v => [`${v}%`, 'Default Rate']} />
              <Bar dataKey="rate" fill="#3b82f6" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Row 2 */}
      <div className="charts-grid-2">
        <div className="glass">
          <div className="section-title">Age vs Default Rate</div>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={age_default} margin={{ top: 10, right: 10, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,179,237,0.08)" />
              <XAxis dataKey="age_group" stroke="#475569" tick={{ fill: '#64748b', fontSize: 12 }} />
              <YAxis stroke="#475569" tick={{ fill: '#64748b', fontSize: 12 }} unit="%" />
              <Tooltip {...GLASS_TOOLTIP} formatter={v => [`${v}%`, 'Default Rate']} />
              <Line type="monotone" dataKey="rate" stroke="#a78bfa" strokeWidth={2.5} dot={{ fill: '#a78bfa', r: 5 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="glass">
          <div className="section-title">Default Rate by Education</div>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={edu_default} layout="vertical" margin={{ top: 5, right: 10, left: 130, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,179,237,0.08)" />
              <XAxis type="number" stroke="#475569" tick={{ fill: '#64748b', fontSize: 11 }} unit="%" />
              <YAxis type="category" dataKey="education" stroke="#475569" tick={{ fill: '#64748b', fontSize: 10 }} width={130} />
              <Tooltip {...GLASS_TOOLTIP} formatter={v => [`${v}%`, 'Default Rate']} />
              <Bar dataKey="rate" fill="#8b5cf6" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Row 3 */}
      <div className="glass">
        <div className="section-title">Default Rate by Income Type</div>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={income_type_default} margin={{ top: 5, right: 10, left: 0, bottom: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,179,237,0.08)" />
            <XAxis dataKey="income_type" stroke="#475569" tick={{ fill: '#64748b', fontSize: 11 }} angle={-20} textAnchor="end" />
            <YAxis stroke="#475569" tick={{ fill: '#64748b', fontSize: 12 }} unit="%" />
            <Tooltip {...GLASS_TOOLTIP} formatter={v => [`${v}%`, 'Default Rate']} />
            <Bar dataKey="rate" fill="#14b8a6" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Insights */}
      <hr />
      <div className="section-title" style={{ color: '#f1f5f9' }}>💡 Key Business Insights</div>
      <div className="insights-grid">
        {insights.map((ins, i) => (
          <div className="insight-card" key={i}>
            <div className="insight-title">{ins.title}</div>
            <div className="insight-text">{ins.text}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
