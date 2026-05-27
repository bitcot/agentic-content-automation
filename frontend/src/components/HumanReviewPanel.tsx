"use client";

import React, { useState } from 'react';

function formatText(text: string) {
  if (!text) return null;
  return text.split(/(\[NEEDS HUMAN CHECK:[^\]]+\])/g).map((part, i) =>
    part.startsWith('[NEEDS HUMAN CHECK:')
      ? <mark key={i} className="needs-check">{part}</mark>
      : <span key={i}>{part}</span>
  );
}

function TweetList({ tweets }: { tweets: string[] }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {tweets.map((t, i) => (
        <div key={i} style={{
          padding: '10px 12px',
          background: 'rgba(242,237,228,0.03)',
          border: 'var(--rule)',
          fontSize: 12,
          lineHeight: 1.6,
          color: 'var(--paper)',
        }}>
          <span style={{ color: 'var(--accent)', fontFamily: 'var(--font-mono)', fontSize: 9, marginRight: 8 }}>{i + 1}</span>
          {t}
        </div>
      ))}
    </div>
  );
}

export default function HumanReviewPanel({
  draftData,
  onReject,
  onApprove,
}: {
  draftData: any;
  onReject: () => void;
  onApprove: () => void;
}) {
  // New API shape: icp, blog, linkedin, x_thread, check_flags on root
  const icp        = draftData?.icp;
  const blog       = draftData?.blog || {};
  const linkedin   = draftData?.linkedin || {};
  const xThread    = draftData?.x_thread || {};
  const checkFlags = draftData?.check_flags || [];
  const needsCheck = draftData?.needs_human_check;

  const score    = icp?.score ?? 0;
  const icpPct   = (score * 100).toFixed(0);
  const approved = score >= 0.65;

  const [activeTab, setActiveTab] = useState<'blog' | 'linkedin' | 'x'>('blog');

  return (
    <div style={{ animation: 'fadeUp 0.35s ease' }}>

      {/* Status bar */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr auto',
        alignItems: 'center',
        padding: '18px 40px',
        borderBottom: 'var(--rule)',
        gap: 20,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 24, flexWrap: 'wrap' }}>
          <div>
            <span style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--muted)' }}>ICP Score</span>
            <p style={{
              fontFamily: 'var(--font-display)', fontSize: 26, fontWeight: 700,
              color: approved ? 'var(--accent)' : 'var(--danger)', lineHeight: 1, marginTop: 2,
            }}>
              {icpPct}<span style={{ fontSize: 14, fontFamily: 'var(--font-mono)' }}>%</span>
            </p>
          </div>

          <div style={{ width: 1, height: 36, background: 'var(--rule-strong)' }} />

          <div>
            <span style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--muted)' }}>Target Persona</span>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--accent)', marginTop: 4 }}>
              {icp?.persona_match || '—'}
            </p>
          </div>

          <div style={{ width: 1, height: 36, background: 'var(--rule-strong)' }} />

          <div>
            <span style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--muted)' }}>ICP Verdict</span>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--muted-warm)', marginTop: 4, maxWidth: 340 }}>
              {icp?.reasoning}
            </p>
          </div>

          {blog.title && (
            <>
              <div style={{ width: 1, height: 36, background: 'var(--rule-strong)' }} />
              <div>
                <span style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--muted)' }}>Blog Title</span>
                <p style={{ fontFamily: 'var(--font-display)', fontSize: 13, fontWeight: 600, color: 'var(--paper)', marginTop: 4, maxWidth: 360 }}>
                  {blog.title}
                </p>
              </div>
            </>
          )}

          {draftData?.token_usage?.total_tokens && (
            <>
              <div style={{ width: 1, height: 36, background: 'var(--rule-strong)' }} />
              <div>
                <span style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--muted)' }}>Tokens Used</span>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--accent)', marginTop: 4, display: 'flex', gap: 8 }}>
                  <span>In: {draftData.token_usage.input_tokens}</span>
                  <span style={{ color: 'var(--muted)' }}>|</span>
                  <span>Out: {draftData.token_usage.output_tokens}</span>
                </div>
              </div>
            </>
          )}
        </div>

        <div style={{ display: 'flex', gap: 0 }}>
          <button className="btn btn-danger" onClick={onReject} style={{ fontSize: 11 }}>Reject</button>
          <button className="btn" style={{ fontSize: 11, marginLeft: -1 }}>Regenerate</button>
          <button className="btn btn-primary" onClick={onApprove} style={{ fontSize: 11, marginLeft: -1 }}>
            Approve & Schedule
          </button>
        </div>
      </div>

      {/* Human check warning */}
      {needsCheck && checkFlags.length > 0 && (
        <div style={{
          padding: '12px 40px',
          background: 'var(--amber-dim)',
          borderBottom: '1px solid rgba(255,184,0,0.2)',
          display: 'flex', alignItems: 'flex-start', gap: 12,
        }}>
          <span style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--amber)', whiteSpace: 'nowrap', marginTop: 2 }}>
            ⚠ {checkFlags.length} Flag{checkFlags.length > 1 ? 's' : ''} — Verify Before Publishing
          </span>
          <p style={{ fontSize: 12, color: 'var(--amber)', lineHeight: 1.6 }}>
            {checkFlags.join(' · ')}
          </p>
        </div>
      )}

      {/* Platform tab selector */}
      <div style={{ padding: '0 40px', borderBottom: 'var(--rule)', display: 'flex', gap: 0, alignItems: 'center' }}>
        {([
          { id: 'blog', label: 'Blog Post' },
          { id: 'linkedin', label: 'LinkedIn' },
          { id: 'x', label: 'X Thread' },
        ] as const).map(t => (
          <button
            key={t.id}
            className={`btn ${activeTab === t.id ? 'active' : ''}`}
            onClick={() => setActiveTab(t.id)}
            style={{ fontSize: 11, marginRight: -1, padding: '14px 16px' }}
          >
            {t.label}
          </button>
        ))}
        {linkedin.hook_pattern_used && (
          <span style={{ marginLeft: 'auto', fontSize: 9, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--muted)', paddingRight: 4 }}>
            Hook: Pattern {linkedin.hook_pattern_used}
          </span>
        )}
      </div>

      {/* Content panels */}
      <div style={{ padding: '28px 40px', minHeight: 380 }}>

        {activeTab === 'blog' && (
          <div>
            {blog.meta_description && (
              <p style={{ fontSize: 11, color: 'var(--muted)', fontFamily: 'var(--font-mono)', marginBottom: 18, padding: '8px 12px', background: 'rgba(242,237,228,0.03)', border: 'var(--rule)' }}>
                <span style={{ color: 'var(--muted)', marginRight: 8 }}>META:</span>{blog.meta_description}
              </p>
            )}
            <div className="draft-area" contentEditable suppressContentEditableWarning spellCheck={false} style={{ minHeight: 340 }}>
              {formatText(blog.body || '—')}
            </div>
            {blog.internal_links?.length > 0 && (
              <div style={{ marginTop: 16, display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
                <span style={{ fontSize: 9, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--muted)' }}>SEO Internal Links:</span>
                {blog.internal_links.map((link: string, i: number) => (
                  <span key={i} style={{ fontSize: 10, color: 'var(--accent)', fontFamily: 'var(--font-mono)', padding: '2px 6px', border: '1px solid rgba(200,255,0,0.2)' }}>{link}</span>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'linkedin' && (
          <div>
            <div style={{ display: 'flex', gap: 8, marginBottom: 14, flexWrap: 'wrap' }}>
              {linkedin.hashtags?.map((h: string, i: number) => (
                <span key={i} style={{ fontSize: 10, color: 'var(--accent)', fontFamily: 'var(--font-mono)', padding: '3px 8px', border: '1px solid rgba(200,255,0,0.2)', background: 'var(--accent-dim)' }}>{h}</span>
              ))}
            </div>
            <div className="draft-area" contentEditable suppressContentEditableWarning spellCheck={false} style={{ minHeight: 200 }}>
              {formatText(linkedin.post || '—')}
            </div>
            {linkedin.first_comment && (
              <div style={{ marginTop: 16, padding: '10px 14px', border: '1px solid rgba(255,184,0,0.2)', background: 'var(--amber-dim)' }}>
                <span style={{ fontSize: 9, color: 'var(--amber)', textTransform: 'uppercase', letterSpacing: '0.12em' }}>First comment (paste after posting): </span>
                <p style={{ fontSize: 12, color: 'var(--paper)', marginTop: 6, fontFamily: 'var(--font-mono)' }}>{linkedin.first_comment}</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'x' && (
          <div>
            {xThread.tweets?.length > 0
              ? <TweetList tweets={xThread.tweets} />
              : <p style={{ color: 'var(--muted)', fontSize: 13, fontStyle: 'italic' }}>No X thread generated.</p>
            }
            {xThread.dm_keyword && (
              <div style={{ marginTop: 16, padding: '10px 14px', border: '1px solid rgba(200,255,0,0.2)', background: 'var(--accent-dim)', display: 'flex', alignItems: 'center', gap: 12 }}>
                <span style={{ fontSize: 9, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.12em' }}>DM Hook Keyword:</span>
                <span style={{ fontSize: 16, color: 'var(--accent)', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>{xThread.dm_keyword}</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Schedule row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', borderTop: 'var(--rule)' }}>
        <div style={{ padding: '24px 32px', borderRight: 'var(--rule)' }}>
          <p className="panel-label" style={{ margin: 0, marginBottom: 14, paddingBottom: 10, borderBottom: 'var(--rule)' }}>Image Brief</p>
          <p style={{ color: 'var(--muted-warm)', fontSize: 12, lineHeight: 1.7, marginBottom: 14 }}>
            Minimalist infographic visualising the hook stat or contrarian reframe. High contrast, no stock photos. Bold headline overlay.
          </p>
          <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', fontSize: 12, color: 'var(--paper)' }}>
            <input type="checkbox" style={{ width: 'auto', accentColor: 'var(--accent)' }} />
            Approve image brief
          </label>
        </div>

        <div style={{ padding: '24px 32px' }}>
          <p className="panel-label" style={{ margin: 0, marginBottom: 14, paddingBottom: 10, borderBottom: 'var(--rule)' }}>Schedule</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {['LinkedIn', 'Blog Post', 'X Thread'].map(p => (
              <div key={p}>
                <label className="field-label">{p} Publication Time</label>
                <input type="datetime-local" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
