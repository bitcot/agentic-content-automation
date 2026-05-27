"use client";

import React, { useEffect, useState } from 'react';

const BASELINE = {
  linkedin_engagement_rate: 1.82,
  form_conversion_rate: 0.26,
  x_bookmark_rate: 2.0,
};

export default function AnalyticsDashboard() {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/analytics')
      .then(r => r.json())
      .then(setMetrics)
      .finally(() => setLoading(false));
  }, []);

  const data = metrics || BASELINE;

  return (
    <div style={{ animation: 'fadeUp 0.4s ease' }}>
      {/* Section header */}
      <div style={{ padding: '32px 40px 24px', borderBottom: 'var(--rule)' }}>
        <p style={{ fontSize: 9, letterSpacing: '0.2em', textTransform: 'uppercase', color: 'var(--muted)', marginBottom: 8 }}>
          Weekly Performance Overview — May 2026
        </p>
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(26px, 3vw, 38px)', fontWeight: 700, letterSpacing: '-0.02em' }}>
          What&apos;s Working.<br />
          <span style={{ color: 'var(--muted)' }}>What Needs Fixing.</span>
        </h2>
      </div>

      {/* Metric cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', borderBottom: 'var(--rule)' }}>
        {[
          { label: 'LinkedIn Avg Engagement', value: data.linkedin_engagement_rate, unit: '%', baseline: 1.82, target: 2.5 },
          { label: 'X Thread Bookmark Rate', value: data.x_bookmark_rate, unit: '%', baseline: 2.0, target: 2.5 },
          { label: 'Form Conversion Rate', value: data.form_conversion_rate, unit: '%', baseline: 0.26, target: 0.5 },
        ].map((m, i) => {
          const delta = ((m.value - m.baseline) / m.baseline * 100).toFixed(0);
          const positive = m.value >= m.baseline;
          return (
            <div key={m.label} className="metric-card" style={{ borderRight: i < 2 ? 'var(--rule)' : undefined, borderTop: 'none', borderLeft: 'none', borderBottom: 'none' }}>
              <p className="metric-label">{m.label}</p>
              <p className="metric-value">
                {m.value.toFixed(2)}
                <span className="metric-unit">{m.unit}</span>
              </p>
              <div style={{ marginTop: 14, display: 'flex', gap: 10, alignItems: 'center' }}>
                <span className={`status-pill ${positive ? 'success' : 'danger'}`}>
                  {positive ? '▲' : '▼'} {Math.abs(Number(delta))}% vs baseline
                </span>
                <span style={{ fontSize: 9, color: 'var(--muted)', letterSpacing: '0.1em' }}>
                  Target: {m.target}{m.unit}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Top performers / Underperformers */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', borderBottom: 'var(--rule)' }}>
        {/* Top */}
        <div style={{ padding: '28px 32px', borderRight: 'var(--rule)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20, paddingBottom: 12, borderBottom: 'var(--rule)' }}>
            <span style={{ fontSize: 9, letterSpacing: '0.2em', textTransform: 'uppercase', color: 'var(--muted)' }}>Top Performers</span>
            <span className="status-pill success">High Engagement + Conversion</span>
          </div>
          {(data.top_performers || []).map((p: any) => (
            <div key={p.id} style={{ marginBottom: 18, paddingBottom: 18, borderBottom: 'var(--rule)' }}>
              <p style={{ fontFamily: 'var(--font-display)', fontSize: 16, fontWeight: 700, marginBottom: 6, color: 'var(--paper)' }}>
                {p.topic}
              </p>
              <div style={{ display: 'flex', gap: 16, fontSize: 11, color: 'var(--muted-warm)' }}>
                <span>Engagement <strong style={{ color: 'var(--success)' }}>{p.engagement}%</strong></span>
                <span>Conversion <strong style={{ color: 'var(--success)' }}>{p.conversion}%</strong></span>
              </div>
            </div>
          ))}
        </div>

        {/* Underperformers */}
        <div style={{ padding: '28px 32px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20, paddingBottom: 12, borderBottom: 'var(--rule)' }}>
            <span style={{ fontSize: 9, letterSpacing: '0.2em', textTransform: 'uppercase', color: 'var(--muted)' }}>Underperformers</span>
            <span className="status-pill danger">Below Threshold</span>
          </div>
          {(data.under_performers || []).map((p: any) => (
            <div key={p.id} style={{ marginBottom: 18, paddingBottom: 18, borderBottom: 'var(--rule)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <p style={{ fontFamily: 'var(--font-display)', fontSize: 16, fontWeight: 700, marginBottom: 6 }}>{p.topic}</p>
                <div style={{ display: 'flex', gap: 16, fontSize: 11, color: 'var(--muted-warm)' }}>
                  <span>Engagement <strong style={{ color: 'var(--danger)' }}>{p.engagement}%</strong></span>
                  <span>Conversion <strong style={{ color: 'var(--danger)' }}>{p.conversion}%</strong></span>
                </div>
              </div>
              <button className="btn" style={{ fontSize: 10, padding: '6px 12px' }}>Optimise →</button>
            </div>
          ))}
        </div>
      </div>

      {/* Baseline table */}
      <div style={{ padding: '24px 40px' }}>
        <p style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--muted)', marginBottom: 16 }}>
          Baseline Benchmarks (May 2026) — from Bitcot&apos;s actual analytics
        </p>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
          <thead>
            <tr>
              {['Metric', 'Current', 'Source', 'Action if below'].map(h => (
                <th key={h} style={{ textAlign: 'left', padding: '8px 0', borderBottom: '1px solid rgba(242,237,228,0.15)', fontSize: 9, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--muted)', fontWeight: 500 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {[
              { metric: 'LinkedIn engagement rate', value: '1.82%', source: 'LinkedIn analytics', action: 'Regenerate hook' },
              { metric: 'LinkedIn CTR', value: '0.8%', source: 'LinkedIn analytics', action: 'Check URL not in body' },
              { metric: 'Blog organic CTR', value: '1.5%', source: 'GSC', action: 'Rewrite title tag' },
              { metric: 'Form conversion rate', value: '0.26% → 0.5%', source: 'GA4', action: 'Flag form UX issue' },
              { metric: 'X thread bookmark rate', value: '2%', source: 'X analytics', action: 'Improve thread structure' },
            ].map(r => (
              <tr key={r.metric}>
                {[r.metric, r.value, r.source, r.action].map((val, i) => (
                  <td key={i} style={{ padding: '10px 0', borderBottom: 'var(--rule)', color: i === 0 ? 'var(--paper)' : 'var(--muted-warm)', paddingRight: 24 }}>{val}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
