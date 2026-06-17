import React, { useState, useEffect } from 'react';
import EDA from './tabs/EDA';
import RiskPredictor from './tabs/RiskPredictor';
import Explainability from './tabs/Explainability';
import BusinessRules from './tabs/BusinessRules';
import TalkToData from './tabs/TalkToData';

const TABS = [
  { key: 'eda',   label: '📊  EDA Dashboard' },
  { key: 'risk',  label: '🎯  Risk Predictor' },
  { key: 'shap',  label: '🔍  Explainability' },
  { key: 'rules', label: '📋  Business Rules' },
  { key: 'chat',  label: '💬  Talk-to-Data' },
];

export default function App() {
  const [tab, setTab] = useState('eda');
  const [status, setStatus] = useState({ model_loaded: false, db_ready: false, data_ready: false });

  useEffect(() => {
    fetch('/api/status').then(r => r.json()).then(setStatus).catch(() => {});
  }, []);

  const statusColor = (status.model_loaded && status.db_ready) ? '#10b981' : '#ef4444';
  const statusText  = (status.model_loaded && status.db_ready) ? 'Ready' : 'Setup needed';

  return (
    <div className="app-layout">
      {/* ── Sidebar ── */}
      <nav className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-icon">🏦</div>
          <div className="logo-name">Credit Risk</div>
          <div className="logo-tag">Intelligence Platform</div>
        </div>

        {TABS.map(t => (
          <button
            key={t.key}
            className={`nav-btn${tab === t.key ? ' active' : ''}`}
            onClick={() => setTab(t.key)}
          >
            {t.label}
          </button>
        ))}

        <div className="sidebar-divider" />

        <div className="sidebar-status">
          Model &nbsp;&nbsp; LightGBM + SHAP<br />
          LLM &nbsp;&nbsp;&nbsp;&nbsp; Groq · Llama-3<br />
          DB &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; DuckDB<br />
          Data &nbsp;&nbsp; Home Credit<br />
          <span className="status-dot" style={{ background: statusColor }} />
          Status &nbsp; {statusText}
        </div>
      </nav>

      {/* ── Main ── */}
      <main className="main-content">
        {tab === 'eda'   && <EDA />}
        {tab === 'risk'  && <RiskPredictor />}
        {tab === 'shap'  && <Explainability />}
        {tab === 'rules' && <BusinessRules />}
        {tab === 'chat'  && <TalkToData />}
      </main>
    </div>
  );
}
