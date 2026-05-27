"use client";

import React, { useEffect, useState } from 'react';

type LogItem = {
  id: number;
  topic: string;
  icp_score: number;
  platform: string;
  status: string;
  needs_human_check: boolean;
  created_at: string;
  published_at: string | null;
};

const STATUS_COLORS: Record<string, string> = {
  pending_review: 'var(--amber)',
  published: 'var(--success)',
  rejected: 'var(--danger)',
  draft: 'var(--muted)',
};

function timeAgo(iso: string) {
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

export default function ContentHistory() {
  const [items, setItems] = useState<LogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  const fetchHistory = () => {
    const url = filter === 'all'
      ? 'http://localhost:8000/history?limit=50'
      : `http://localhost:8000/history?limit=50&status=${filter}`;

    fetch(url)
      .then(r => r.json())
      .then(d => setItems(d.items || []))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    setLoading(true);
    fetchHistory();
  }, [filter]);

  const statusCounts = items.reduce((acc, item) => {
    acc[item.status] = (acc[item.status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div style={{ animation: 'fadeUp 0.4s ease' }}>
      {/* Header */}
      <div style={{ padding: '32px 40px 24px', borderBottom: 'var(--rule)' }}>
        <p style={{ fontSize: 9, letterSpacing: '0.2em', textTransform: 'uppercase', color: 'var(--muted)', marginBottom: 8 }}>
          Memory Layer — Content Log
        </p>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: 16 }}>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(26px, 3vw, 38px)', fontWeight: 700, letterSpacing: '-0.02em', lineHeight: 1.1 }}>
            All Generated<br />
            <span style={{ color: 'var(--muted)' }}>Content.</span>
          </h2>
          {/* Status filter */}
          <div style={{ display: 'flex', gap: 0 }}>
            {['all', 'pending_review', 'published', 'rejected'].map(s => (
              <button
                key={s}
                className={`btn ${filter === s ? 'active' : ''}`}
                onClick={() => setFilter(s)}
                style={{ fontSize: 10, padding: '7px 14px', textTransform: 'capitalize', marginLeft: '-1px' }}
              >
                {s.replace('_', ' ')}
                {s !== 'all' && statusCounts[s] ? ` (${statusCounts[s]})` : ''}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Table */}
      {loading ? (
        <div style={{ padding: '60px 40px', textAlign: 'center', color: 'var(--muted)', fontSize: 12 }}>
          <div className="loading-bar" style={{ marginBottom: 12 }} />
          Loading content history…
        </div>
      ) : items.length === 0 ? (
        <div style={{ padding: '80px 40px', textAlign: 'center' }}>
          <p style={{ fontFamily: 'var(--font-display)', fontSize: 22, color: 'var(--muted)', fontStyle: 'italic' }}>
            No content generated yet.
          </p>
          <p style={{ fontSize: 12, color: 'var(--muted)', marginTop: 8 }}>
            Generate your first piece from the Content Generator tab.
          </p>
        </div>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: 'var(--rule)' }}>
              {['ID', 'Topic', 'ICP Score', 'Platform', 'Status', 'Flags', 'Created'].map(h => (
                <th key={h} style={{
                  textAlign: 'left',
                  padding: '10px 16px',
                  fontSize: 9,
                  letterSpacing: '0.15em',
                  textTransform: 'uppercase',
                  color: 'var(--muted)',
                  fontFamily: 'var(--font-mono)',
                  fontWeight: 500,
                  background: 'rgba(242,237,228,0.02)',
                }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {items.map((item, i) => (
              <tr
                key={item.id}
                style={{
                  borderBottom: 'var(--rule)',
                  transition: 'background 0.1s',
                  background: i % 2 === 0 ? 'transparent' : 'rgba(242,237,228,0.01)',
                }}
                onMouseEnter={e => (e.currentTarget.style.background = 'rgba(200,255,0,0.03)')}
                onMouseLeave={e => (e.currentTarget.style.background = i % 2 === 0 ? 'transparent' : 'rgba(242,237,228,0.01)')}
              >
                <td style={{ padding: '12px 16px', color: 'var(--muted)', fontSize: 11, fontFamily: 'var(--font-mono)' }}>
                  #{item.id}
                </td>
                <td style={{ padding: '12px 16px', fontFamily: 'var(--font-display)', fontSize: 14, fontWeight: 600, maxWidth: 280 }}>
                  {item.topic}
                </td>
                <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: 12 }}>
                  <span style={{ color: item.icp_score >= 0.65 ? 'var(--success)' : 'var(--danger)', fontWeight: 600 }}>
                    {item.icp_score ? (item.icp_score * 100).toFixed(0) + '%' : '—'}
                  </span>
                </td>
                <td style={{ padding: '12px 16px', fontSize: 11, color: 'var(--muted-warm)', textTransform: 'capitalize' }}>
                  {item.platform}
                </td>
                <td style={{ padding: '12px 16px' }}>
                  <span style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: 10,
                    letterSpacing: '0.08em',
                    textTransform: 'uppercase',
                    color: STATUS_COLORS[item.status] || 'var(--muted)',
                    padding: '3px 8px',
                    border: `1px solid ${STATUS_COLORS[item.status] || 'var(--muted)'}33`,
                    background: `${STATUS_COLORS[item.status] || 'var(--muted)'}11`,
                  }}>
                    {item.status.replace('_', ' ')}
                  </span>
                </td>
                <td style={{ padding: '12px 16px', fontSize: 11, color: item.needs_human_check ? 'var(--amber)' : 'var(--muted)' }}>
                  {item.needs_human_check ? '⚠ Verify' : '✓ Clean'}
                </td>
                <td style={{ padding: '12px 16px', fontSize: 11, color: 'var(--muted)', fontFamily: 'var(--font-mono)' }}>
                  {item.created_at ? timeAgo(item.created_at) : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
