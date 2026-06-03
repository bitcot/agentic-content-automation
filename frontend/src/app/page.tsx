"use client";

import React, { useState } from 'react';
import ManualInputPanel from '@/components/ManualInputPanel';
import HumanReviewPanel from '@/components/HumanReviewPanel';
import AnalyticsDashboard from '@/components/AnalyticsDashboard';
import ContentHistory from '@/components/ContentHistory';

type Tab = 'generate' | 'history' | 'analytics';

export default function Home() {
  const [tab, setTab]           = useState<Tab>('generate');
  const [draftData, setDraftData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError]       = useState<string | null>(null);

  const handleGenerate = async (data: any) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch('http://localhost:8000/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          topic: data.topic, 
          angle: data.angle, 
          target_persona: data.targetPersona,
          tone: data.tone,
          author_voice: data.authorVoice,
          image_idea: data.imageIdea,
          use_web_search: data.useWebSearch,
          image_source: data.imageSource
        }),
      });
      const result = await res.json();
      if (!res.ok) throw new Error(result.detail || 'Generation failed');
      setDraftData(result);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleViewHistory = async (id: number) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(`http://localhost:8000/history/${id}`);
      const result = await res.json();
      if (!res.ok) throw new Error(result.detail || 'Failed to fetch content');
      setDraftData(result);
      setTab('generate');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!draftData?.content_id) {
       alert("No content ID found");
       return;
    }
    setIsLoading(true);
    setError(null);
    try {
       const res = await fetch('http://localhost:8000/schedule', {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify({
            content_id: draftData.content_id,
            platform: 'all',
            schedule_time: new Date().toISOString()
         })
       });
       const result = await res.json();
       if (!res.ok) throw new Error(result.detail || 'Scheduling failed');
       alert('Content approved and queued for publishing!'); 
       setDraftData(null);
    } catch (err: any) {
       setError(err.message);
    } finally {
       setIsLoading(false);
    }
  };

  const handleRegenerate = async (target_part: string, feedback: string) => {
    if (!draftData?.content_id) {
       alert("No content ID found");
       return;
    }
    setIsLoading(true);
    setError(null);
    try {
       const res = await fetch('http://localhost:8000/regenerate', {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify({
            content_id: draftData.content_id,
            target_part,
            feedback
         })
       });
       const result = await res.json();
       if (!res.ok) throw new Error(result.detail || 'Regeneration failed');
       setDraftData(result);
    } catch (err: any) {
       setError(err.message);
    } finally {
       setIsLoading(false);
    }
  };

  return (
    <>
      {/* ── Masthead ──────────────────────────────────────────────── */}
      <header className="masthead">
        <div>
          <h1 className="masthead-title">
            Bitcot <span>Content OS</span>
          </h1>
          <p className="masthead-sub">Autonomous Content Generation System · v1.0</p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 10 }}>
          {/* Mode badges */}
          <div style={{ display: 'flex', gap: 8 }}>
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 9,
              letterSpacing: '0.12em',
              textTransform: 'uppercase',
              padding: '4px 10px',
              background: 'var(--accent-dim)',
              color: 'var(--accent)',
              border: '1px solid rgba(200,255,0,0.3)',
            }}>
              ● Mode B — Active
            </span>
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 9,
              letterSpacing: '0.12em',
              textTransform: 'uppercase',
              padding: '4px 10px',
              background: 'rgba(255,255,255,0.03)',
              color: 'var(--muted)',
              border: 'var(--rule)',
            }}>
              ○ Mode A — Not Built Yet
            </span>
          </div>

          {/* Nav tabs */}
          <nav className="masthead-nav">
            <button
              className={`btn ${tab === 'generate' ? 'active' : ''}`}
              onClick={() => { setTab('generate'); setDraftData(null); }}
              style={{ fontSize: 11 }}
            >
              Generate
            </button>
            <button
              className={`btn ${tab === 'history' ? 'active' : ''}`}
              onClick={() => setTab('history')}
              style={{ fontSize: 11, marginLeft: -1 }}
            >
              History
            </button>
            <button
              className={`btn ${tab === 'analytics' ? 'active' : ''}`}
              onClick={() => setTab('analytics')}
              style={{ fontSize: 11, marginLeft: -1 }}
            >
              Analytics
            </button>
          </nav>
        </div>
      </header>

      {/* ── Error banner ─────────────────────────────────────────── */}
      {error && (
        <div style={{
          padding: '14px 40px',
          background: 'var(--danger-dim)',
          borderBottom: '1px solid rgba(255,65,54,0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 20,
        }}>
          <div>
            <span style={{ fontSize: 9, letterSpacing: '0.15em', textTransform: 'uppercase', color: 'var(--danger)' }}>
              Pipeline Error
            </span>
            <p style={{ fontSize: 12, color: 'var(--paper)', marginTop: 2 }}>{error}</p>
          </div>
          <button
            className="btn btn-danger"
            onClick={() => setError(null)}
            style={{ fontSize: 10, padding: '6px 14px', whiteSpace: 'nowrap' }}
          >
            Dismiss
          </button>
        </div>
      )}

      {/* ── Main content ─────────────────────────────────────────── */}
      <main>
        {tab === 'generate' ? (
          !draftData ? (
            <ManualInputPanel onGenerate={handleGenerate} isLoading={isLoading} />
          ) : (
            <HumanReviewPanel
              draftData={draftData}
              onReject={() => setDraftData(null)}
              onApprove={handleApprove}
              onRegenerate={handleRegenerate}
            />
          )
        ) : tab === 'history' ? (
          <ContentHistory onViewContent={handleViewHistory} />
        ) : (
          <AnalyticsDashboard />
        )}
      </main>
    </>
  );
}
