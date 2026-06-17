import React, { useState } from 'react';

const INIT = {
  amt_income: 180000, amt_credit: 450000, amt_annuity: 22000, amt_goods: 400000,
  age: 35, employment_years: 5,
  cnt_children: 0, cnt_fam: 2,
  gender: 'F', education: 'Secondary / secondary special',
  income_type: 'Working', own_car: 'N', own_realty: 'Y', region: 2,
  ext1: 0.5, ext2: 0.5, ext3: 0.5,
};

const EDUCATIONS = [
  'Secondary / secondary special', 'Higher education',
  'Incomplete higher', 'Lower secondary', 'Academic degree',
];
const INCOME_TYPES = [
  'Working', 'Commercial associate', 'Pensioner', 'State servant',
  'Unemployed', 'Student', 'Businessman', 'Maternity leave',
];

function Field({ label, children }) {
  return (
    <div className="form-group">
      <label className="form-label">{label}</label>
      {children}
    </div>
  );
}

export default function RiskPredictor() {
  const [form, setForm] = useState(INIT);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = async () => {
    setLoading(true); setError(null); setResult(null);
    try {
      const res = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (data.error) setError(data.error);
      else setResult(data);
    } catch {
      setError('Failed to connect to backend.');
    }
    setLoading(false);
  };

  const bandClass = result ? ({ Low: 'risk-low', Medium: 'risk-medium', High: 'risk-high' }[result.band]) : '';
  const bandColor = result ? ({ Low: '#14b8a6', Medium: '#fbbf24', High: '#ef4444' }[result.band]) : '';

  return (
    <div>
      <div className="hero-glass">
        <div className="hero-title">Loan Default Risk Predictor</div>
        <div className="hero-sub">Enter applicant details for an instant AI-powered risk assessment</div>
      </div>

      {/* Metrics row (shown if metrics available from a past predict) */}
      {result?.metrics && (
        <div className="kpi-grid" style={{ marginBottom: '1.5rem' }}>
          <div className="kpi-glass kpi-blue">
            <div className="kpi-label">ROC-AUC</div>
            <div className="kpi-value">{result.metrics.roc_auc}</div>
          </div>
          <div className="kpi-glass kpi-purple">
            <div className="kpi-label">PR-AUC</div>
            <div className="kpi-value">{result.metrics.pr_auc}</div>
          </div>
          <div className="kpi-glass kpi-teal">
            <div className="kpi-label">Model Type</div>
            <div className="kpi-value" style={{ fontSize: '1rem' }}>LightGBM</div>
          </div>
          <div className="kpi-glass kpi-rose">
            <div className="kpi-label">Features</div>
            <div className="kpi-value">{result.metrics.n_features}</div>
          </div>
        </div>
      )}

      {/* Input form */}
      <div className="glass">
        <div className="form-grid-3">
          {/* Financial */}
          <div>
            <div className="form-section-title">Financial</div>
            <Field label="Annual Income (₹)">
              <input className="form-input" type="number" value={form.amt_income}
                onChange={e => set('amt_income', +e.target.value)} />
            </Field>
            <Field label="Loan Amount (₹)">
              <input className="form-input" type="number" value={form.amt_credit}
                onChange={e => set('amt_credit', +e.target.value)} />
            </Field>
            <Field label="Annual Repayment (₹)">
              <input className="form-input" type="number" value={form.amt_annuity}
                onChange={e => set('amt_annuity', +e.target.value)} />
            </Field>
            <Field label="Goods Price (₹)">
              <input className="form-input" type="number" value={form.amt_goods}
                onChange={e => set('amt_goods', +e.target.value)} />
            </Field>
          </div>

          {/* Personal */}
          <div>
            <div className="form-section-title">Personal</div>
            <Field label={`Age: ${form.age}`}>
              <input className="form-range" type="range" min={20} max={70} value={form.age}
                onChange={e => set('age', +e.target.value)} />
            </Field>
            <Field label={`Employment (years): ${form.employment_years}`}>
              <input className="form-range" type="range" min={0} max={40} value={form.employment_years}
                onChange={e => set('employment_years', +e.target.value)} />
            </Field>
            <Field label="No. of Children">
              <select className="form-select" value={form.cnt_children}
                onChange={e => set('cnt_children', +e.target.value)}>
                {[...Array(11)].map((_, i) => <option key={i} value={i}>{i}</option>)}
              </select>
            </Field>
            <Field label="Family Size">
              <select className="form-select" value={form.cnt_fam}
                onChange={e => set('cnt_fam', +e.target.value)}>
                {[...Array(10)].map((_, i) => <option key={i+1} value={i+1}>{i+1}</option>)}
              </select>
            </Field>
          </div>

          {/* Profile */}
          <div>
            <div className="form-section-title">Profile</div>
            <Field label="Gender">
              <select className="form-select" value={form.gender} onChange={e => set('gender', e.target.value)}>
                <option value="F">Female</option>
                <option value="M">Male</option>
              </select>
            </Field>
            <Field label="Education Level">
              <select className="form-select" value={form.education} onChange={e => set('education', e.target.value)}>
                {EDUCATIONS.map(e => <option key={e} value={e}>{e}</option>)}
              </select>
            </Field>
            <Field label="Income Type">
              <select className="form-select" value={form.income_type} onChange={e => set('income_type', e.target.value)}>
                {INCOME_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </Field>
            <Field label="Owns a Vehicle?">
              <select className="form-select" value={form.own_car} onChange={e => set('own_car', e.target.value)}>
                <option value="N">No</option>
                <option value="Y">Yes</option>
              </select>
            </Field>
            <Field label="Owns Property?">
              <select className="form-select" value={form.own_realty} onChange={e => set('own_realty', e.target.value)}>
                <option value="Y">Yes</option>
                <option value="N">No</option>
              </select>
            </Field>
            <Field label="Region Risk Rating">
              <select className="form-select" value={form.region} onChange={e => set('region', +e.target.value)}>
                {[1, 2, 3].map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </Field>
          </div>
        </div>
      </div>

      {/* Credit Scores */}
      <div className="glass">
        <div className="form-section-title">🏦 External Credit Bureau Scores</div>
        <p style={{ color: '#64748b', fontSize: '0.8rem', marginBottom: '1rem' }}>
          Strongest predictors. Scale 0 (worst) → 1 (best). Leave at 0.5 if unknown.
        </p>
        <div className="scores-row">
          {[['ext1', 'EXT_SOURCE_1 (Credit Score 1)'], ['ext2', 'EXT_SOURCE_2 (Credit Score 2)'], ['ext3', 'EXT_SOURCE_3 (Credit Score 3)']].map(([key, label]) => (
            <div key={key}>
              <label className="form-label">{label}: <span style={{ color: '#63b3ed', fontFamily: 'DM Mono,monospace' }}>{form[key]}</span></label>
              <input className="form-range" type="range" min={0} max={1} step={0.01}
                value={form[key]} onChange={e => set(key, +e.target.value)} />
            </div>
          ))}
        </div>
      </div>

      <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
        {loading ? <><span className="spinner" />Assessing risk...</> : '⚡ Assess Risk Now'}
      </button>

      {error && <div className="alert alert-error" style={{ marginTop: '1rem' }}>{error}</div>}

      {/* Results */}
      {result && (
        <>
          <hr />
          <div className="charts-grid-2">
            {/* Gauge */}
            <div className="glass">
              <div className="gauge-container">
                <div className="gauge-number" style={{ color: bandColor }}>{result.score}%</div>
                <div className="gauge-label">Default Probability</div>
                <div style={{ marginTop: '1rem' }}>
                  <GaugeBar value={result.score} color={bandColor} />
                </div>
              </div>
            </div>

            {/* Decision */}
            <div className="glass">
              <span className={`risk-pill ${bandClass}`}>⬤ &nbsp;{result.band} Risk</span>
              <div className="mini-metrics">
                <div>
                  <div className="mini-metric-label">Default Prob</div>
                  <div className="mini-metric-value">{result.score}%</div>
                </div>
                <div>
                  <div className="mini-metric-label">Credit / Income</div>
                  <div className="mini-metric-value">{result.credit_to_income}×</div>
                </div>
                <div>
                  <div className="mini-metric-label">Repayment / Inc</div>
                  <div className="mini-metric-value">{result.repayment_to_income}%</div>
                </div>
              </div>
              {result.band === 'Low'    && <div className="alert alert-success">✅ APPROVE — Profile appears stable. Standard loan terms recommended.</div>}
              {result.band === 'Medium' && <div className="alert alert-warning">⚠️ MANUAL REVIEW — Moderate risk. Request additional documents or collateral.</div>}
              {result.band === 'High'   && <div className="alert alert-error">❌ HIGH RISK — Likely to default. Decline or apply stricter conditions.</div>}
            </div>
          </div>

          {/* Model metrics */}
          {result.metrics && (
            <>
              <hr />
              <div className="section-title">📊 Model Performance Details</div>
              <div className="kpi-grid">
                <div className="kpi-glass kpi-teal">
                  <div className="kpi-label">F1 (Default Class)</div>
                  <div className="kpi-value">{typeof result.metrics.f1 === 'number' ? result.metrics.f1.toFixed(4) : result.metrics.f1}</div>
                </div>
                <div className="kpi-glass kpi-blue">
                  <div className="kpi-label">Precision</div>
                  <div className="kpi-value">{typeof result.metrics.precision === 'number' ? result.metrics.precision.toFixed(4) : result.metrics.precision}</div>
                </div>
                <div className="kpi-glass kpi-purple">
                  <div className="kpi-label">Recall</div>
                  <div className="kpi-value">{typeof result.metrics.recall === 'number' ? result.metrics.recall.toFixed(4) : result.metrics.recall}</div>
                </div>
                <div className="kpi-glass kpi-rose">
                  <div className="kpi-label">Accuracy</div>
                  <div className="kpi-value">{typeof result.metrics.accuracy === 'number' ? result.metrics.accuracy.toFixed(4) : result.metrics.accuracy}</div>
                </div>
              </div>

              {result.metrics.confusion_matrix && (
                <div className="glass" style={{ marginTop: '1rem' }}>
                  <div className="section-title">Confusion Matrix</div>
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th></th>
                        <th>Pred: Repaid</th>
                        <th>Pred: Default</th>
                      </tr>
                    </thead>
                    <tbody>
                      {['Actual: Repaid', 'Actual: Default'].map((row, i) => (
                        <tr key={i}>
                          <td style={{ color: '#63b3ed' }}>{row}</td>
                          {result.metrics.confusion_matrix[i].map((v, j) => (
                            <td key={j} style={{ fontFamily: 'DM Mono,monospace' }}>{v?.toLocaleString()}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          )}

          {/* SHAP waterfall */}
          {result.shap && (
            <>
              <hr />
              <div className="section-title">Why this score? — SHAP Explanation</div>
              <div className="glass">
                <ShapWaterfall shap={result.shap} />
              </div>
              <p style={{ color: '#475569', fontSize: '0.78rem', marginTop: '0.5rem' }}>
                Red bars push risk UP · Blue bars push risk DOWN · f(x) = final predicted probability
              </p>
            </>
          )}
        </>
      )}
    </div>
  );
}

function GaugeBar({ value, color }) {
  return (
    <div style={{ position: 'relative', height: '12px', borderRadius: '6px', background: 'rgba(255,255,255,0.06)', overflow: 'hidden' }}>
      <div style={{
        width: `${value}%`, height: '100%', borderRadius: '6px',
        background: `linear-gradient(90deg, rgba(20,184,166,0.6), ${color})`,
        transition: 'width 0.6s ease',
      }} />
    </div>
  );
}

function ShapWaterfall({ shap }) {
  const maxAbs = Math.max(...shap.features.map(f => Math.abs(f.value)), 0.001);

  return (
    <div>
      <div style={{ marginBottom: '6px', fontSize: '0.75rem', color: '#475569' }}>
        Base value: {shap.base_value.toFixed(4)}
      </div>
      {shap.features.map((f, i) => {
        const pct = (Math.abs(f.value) / maxAbs) * 100;
        const pos = f.value > 0;
        return (
          <div className="shap-bar-row" key={i}>
            <div className="shap-feature">{f.feature}</div>
            <div className="shap-bar-track">
              <div className={`shap-bar-fill ${pos ? 'shap-bar-pos' : 'shap-bar-neg'}`}
                style={{ width: `${pct}%` }} />
            </div>
            <div className="shap-val" style={{ color: pos ? '#f87171' : '#60a5fa' }}>
              {f.value > 0 ? '+' : ''}{f.value.toFixed(4)}
            </div>
          </div>
        );
      })}
    </div>
  );
}
