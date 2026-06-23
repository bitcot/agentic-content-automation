"use client";

import React, { useState, useEffect, useRef } from 'react';
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
  const [agentLogs, setAgentLogs] = useState<any[]>([]);
  const [researchPlan, setResearchPlan] = useState<any>(null);
  const [showResearchModal, setShowResearchModal] = useState(false);
  const [currentRequestData, setCurrentRequestData] = useState<any>(null);
  const [selectedSources, setSelectedSources] = useState<number[]>([]);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    let ws: WebSocket;
    let reconnectTimeout: NodeJS.Timeout;

    const connectWS = () => {
      const wsUrl = `ws://${window.location.hostname}:8000/ws`;
      ws = new WebSocket(wsUrl);
      
      ws.onopen = () => console.log("Connected to WS:", wsUrl);
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "AGENT_LOG") {
            setAgentLogs(prev => [...prev, data]);
          }
        } catch (err) {
          console.error("WS Parse error", err);
        }
      };

      ws.onclose = () => {
        console.log("WS Closed, reconnecting in 2s...");
        reconnectTimeout = setTimeout(connectWS, 2000);
      };

      ws.onerror = (e) => {
        // Suppressed console.error to prevent Next.js error overlay during backend reloads
        ws.close(); // Trigger onclose to reconnect
      };
    };

    connectWS();
    
    return () => {
      clearTimeout(reconnectTimeout);
      if (ws) {
        ws.onclose = null; // Prevent reconnect loop
        ws.close();
      }
    };
  }, []);

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsLoading(false);
      setAgentLogs(prev => [...prev, { agent: "System", message: "Generation stopped by user." }]);
    }
  };

  const handleGenerate = async (data: any) => {
    setIsLoading(true);
    setError(null);
    setAgentLogs([]);
    setCurrentRequestData(data);
    
    abortControllerRef.current = new AbortController();
    
    try {
      const backendUrl = `http://${window.location.hostname}:8000`;
      
      // STEP 1: Research Plan
      const res = await fetch(`${backendUrl}/research-plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: abortControllerRef.current.signal,
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
      if (!res.ok) throw new Error(result.detail || 'Research phase failed');
      
      if (data.requireApproval) {
        setResearchPlan(result);
        if (result.research_context && result.research_context.sources) {
          setSelectedSources(result.research_context.sources.map((_: any, i: number) => i));
        } else {
          setSelectedSources([]);
        }
        setShowResearchModal(true);
        setIsLoading(false); // Pause loading while waiting for approval
      } else {
        // Auto-approve and continue
        let autoContextStr = "";
        if (typeof result.research_context === 'object' && result.research_context.sources) {
           autoContextStr = result.research_context.header || "";
           result.research_context.sources.forEach((src: any, i: number) => {
               autoContextStr += `Result ${i + 1}:\nTitle: ${src.title}\nBody/Snippet: ${src.body}\nSource URL: ${src.url}\n\n`;
           });
        } else {
           autoContextStr = result.research_context || "";
        }
        await executeWriteContent(data, result.icp_result, autoContextStr);
      }
    } catch (err: any) {
      if (err.name === 'AbortError') {
        console.log("Generation aborted");
      } else {
        setError(err.message);
      }
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  const executeWriteContent = async (data: any, icp_result: any, research_context: string) => {
    setIsLoading(true);
    try {
      const backendUrl = `http://${window.location.hostname}:8000`;
      const res = await fetch(`${backendUrl}/write-content`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: abortControllerRef.current?.signal,
        body: JSON.stringify({ 
          topic: data.topic, 
          angle: data.angle, 
          target_persona: data.targetPersona,
          tone: data.tone,
          author_voice: data.authorVoice,
          image_idea: data.imageIdea,
          use_web_search: data.useWebSearch,
          image_source: data.imageSource,
          icp_result: icp_result,
          research_context: research_context
        }),
      });
      const result = await res.json();
      if (!res.ok) throw new Error(result.detail || 'Generation failed');
      setDraftData(result.draft);
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        setError(err.message);
      }
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  const handleApproveResearch = () => {
    setShowResearchModal(false);
    if (currentRequestData && researchPlan) {
      let finalContextStr = "";
      if (typeof researchPlan.research_context === 'object' && researchPlan.research_context.sources) {
         finalContextStr = researchPlan.research_context.header || "";
         researchPlan.research_context.sources.forEach((src: any, i: number) => {
            if (selectedSources.includes(i)) {
                finalContextStr += `Result ${i + 1}:\nTitle: ${src.title}\nBody/Snippet: ${src.body}\nSource URL: ${src.url}\n\n`;
            }
         });
      } else {
         finalContextStr = researchPlan.research_context || "";
      }
      executeWriteContent(currentRequestData, researchPlan.icp_result, finalContextStr);
    }
  };

  const toggleSource = (index: number) => {
    setSelectedSources(prev => 
      prev.includes(index) ? prev.filter(i => i !== index) : [...prev, index]
    );
  };

  const handleViewHistory = async (id: number) => {
    setIsLoading(true);
    setError(null);
    try {
      const backendUrl = `http://${window.location.hostname}:8000`;
      const res = await fetch(`${backendUrl}/history/${id}`);
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
       const backendUrl = `http://${window.location.hostname}:8000`;
       const res = await fetch(`${backendUrl}/schedule`, {
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
       const backendUrl = `http://${window.location.hostname}:8000`;
       const res = await fetch(`${backendUrl}/regenerate`, {
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
              color: 'var(--accent)',
              border: '1px solid rgba(200,255,0,0.3)',
            }}>
              ● Mode A — Trend Detection
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

      {/* Main content */}
      <main>
        {tab === 'generate' ? (
          !draftData ? (
            <ManualInputPanel onGenerate={handleGenerate} isLoading={isLoading} agentLogs={agentLogs} onStop={handleStop} />
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

      {/* Research Approval Modal */}
      {showResearchModal && researchPlan && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.85)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 9999, backdropFilter: 'blur(4px)', padding: 20
        }}>
          <div style={{
            background: 'var(--bg)', border: '1px solid var(--border)',
            padding: '30px', maxWidth: 600, width: '100%',
            boxShadow: '0 20px 40px rgba(0,0,0,0.5)'
          }}>
            <h2 style={{ fontSize: 16, marginBottom: 10, color: 'var(--accent)' }}>Mid-Flight Research Approval Required</h2>
            <p style={{ fontSize: 13, color: 'var(--muted)', marginBottom: 20 }}>
              The agent proposes the following topic and data. Do you approve this direction?
            </p>
            
            <div style={{
              background: '#0a0a0a', padding: 15, border: '1px solid rgba(255,255,255,0.1)',
              fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--paper)',
              maxHeight: 400, overflowY: 'auto', marginBottom: 20
            }}>
              {researchPlan.research_context && typeof researchPlan.research_context === 'object' && researchPlan.research_context.sources ? (
                 <div>
                   <p style={{ whiteSpace: 'pre-wrap', marginBottom: 16 }}>{researchPlan.research_context.header}</p>
                   {researchPlan.research_context.sources.length > 0 ? researchPlan.research_context.sources.map((src: any, i: number) => (
                      <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 12, marginBottom: 16, borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: 16 }}>
                         <input 
                           type="checkbox" 
                           checked={selectedSources.includes(i)} 
                           onChange={() => toggleSource(i)} 
                           style={{ marginTop: 2, accentColor: 'var(--accent)' }}
                         />
                         <div style={{ flex: 1 }}>
                            <p style={{ margin: 0, fontWeight: 'bold', color: 'var(--paper)', fontSize: 12 }}>{src.title}</p>
                            <a href={src.url} target="_blank" style={{ color: 'var(--accent)', textDecoration: 'none', display: 'block', marginBottom: 6, fontSize: 10, wordBreak: 'break-all' }}>{src.url}</a>
                            <p style={{ margin: 0, color: 'var(--muted)', lineHeight: 1.5 }}>{src.body}</p>
                         </div>
                      </div>
                   )) : <p style={{ color: 'var(--muted)' }}>No web search data fetched. Continuing with internal knowledge.</p>}
                 </div>
              ) : (
                 <div style={{ whiteSpace: 'pre-wrap' }}>
                   {researchPlan.research_context || "No web search data fetched. Continuing with internal knowledge."}
                 </div>
              )}
            </div>

            <div style={{ display: 'flex', gap: 15, justifyContent: 'flex-end' }}>
              <button className="btn" onClick={() => setShowResearchModal(false)} style={{ fontSize: 12 }}>
                Reject & Cancel
              </button>
              <button className="btn btn-primary" onClick={handleApproveResearch} style={{ fontSize: 12 }}>
                Approve & Write Content
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
