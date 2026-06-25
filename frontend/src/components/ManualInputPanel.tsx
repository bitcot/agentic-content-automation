"use client";

import React, { useState, useEffect } from 'react';
import { useVoiceRecognition } from '../hooks/useVoiceRecognition';

const tones = [
  { value: "thought_leader", label: "Thought Leader" },
  { value: "founder_voice",  label: "Founder Voice" },
  { value: "educational",    label: "Educational" },
  { value: "contrarian",     label: "Contrarian" },
];

const platforms = ["LinkedIn", "X Thread", "Blog", "Newsletter"];

export default function ManualInputPanel({
  onGenerate,
  isLoading,
  agentLogs = [],
  onStop,
}: {
  onGenerate: (data: any) => void;
  isLoading: boolean;
  agentLogs?: any[];
  onStop?: () => void;
}) {
  const [topic, setTopic]       = useState("");
  const [angle, setAngle]       = useState("");
  const [imageIdea, setImageIdea] = useState("");
  const [enhanceDirection, setEnhanceDirection] = useState("");
  const [tone, setTone]         = useState("thought_leader");
  const [targetPersona, setTargetPersona] = useState("");
  const [authorVoice, setAuthorVoice] = useState("bitcot");
  const [useWebSearch, setUseWebSearch] = useState(false);
  const [requireApproval, setRequireApproval] = useState(true);
  const [imageSource, setImageSource] = useState("ai");
  const [activePlatforms, setActivePlatforms] = useState(
    new Set(["LinkedIn", "X Thread", "Blog"])
  );

  const togglePlatform = (p: string) => {
    setActivePlatforms(prev => {
      const next = new Set(prev);
      next.has(p) ? next.delete(p) : next.add(p);
      return next;
    });
  };

  const [isEnhancing, setIsEnhancing] = useState(false);
  const [trends, setTrends] = useState<any[]>([]);
  const [isDiscovering, setIsDiscovering] = useState(false);
  
  const [customVoices, setCustomVoices] = useState<string[]>([]);
  const [showVoiceModal, setShowVoiceModal] = useState(false);
  const [newVoiceName, setNewVoiceName] = useState("");
  const [newVoiceSample, setNewVoiceSample] = useState("");
  const [isCloning, setIsCloning] = useState(false);

  useEffect(() => {
    const fetchVoices = async () => {
      try {
        const backendUrl = `http://${window.location.hostname}:8000`;
        const res = await fetch(`${backendUrl}/voices`);
        const data = await res.json();
        if (data.status === 'success') {
          setCustomVoices(data.voices);
        }
      } catch (err) {
        console.error("Failed to fetch voices:", err);
      }
    };
    fetchVoices();
  }, []);

  const handleCloneVoice = async () => {
    if (!newVoiceName || !newVoiceSample) return;
    setIsCloning(true);
    try {
      const backendUrl = `http://${window.location.hostname}:8000`;
      const res = await fetch(`${backendUrl}/clone-voice`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sample_text: newVoiceSample,
          persona_name: newVoiceName
        })
      });
      const data = await res.json();
      if (data.status === 'success') {
        setCustomVoices(prev => [...prev, data.persona]);
        setAuthorVoice(data.persona);
        setShowVoiceModal(false);
        setNewVoiceName("");
        setNewVoiceSample("");
      }
    } catch (err) {
      console.error("Failed to clone voice:", err);
    } finally {
      setIsCloning(false);
    }
  };

  const { isListening, activeField, startListening, hasSupport } = useVoiceRecognition();

  const handleVoiceInput = (fieldId: string, setter: (val: string | ((prev: string) => string)) => void) => {
    startListening(fieldId, (text) => {
      setter((prev: string) => prev ? prev + " " + text : text);
    });
  };

  const renderMicBtn = (fieldId: string, setter: any, isTextArea: boolean = false) => {
    if (!hasSupport) return null;
    const active = isListening && activeField === fieldId;
    return (
      <button 
        type="button"
        onClick={() => handleVoiceInput(fieldId, setter)}
        style={{
          position: 'absolute',
          right: 12,
          top: isTextArea ? 12 : '50%',
          transform: isTextArea ? 'none' : 'translateY(-50%)',
          background: 'transparent',
          border: 'none',
          color: active ? 'var(--accent)' : 'var(--muted)',
          cursor: 'pointer',
          padding: 4,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          opacity: active ? 1 : 0.5,
          transition: 'all 0.2s',
          animation: active ? 'pulse 1.5s infinite' : 'none'
        }}
        title="Dictate with microphone"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
          <line x1="12" y1="19" x2="12" y2="22"></line>
        </svg>
      </button>
    );
  };

  const handleDiscover = async () => {
    setIsDiscovering(true);
    try {
      const backendUrl = `http://${window.location.hostname}:8000`;
      const res = await fetch(`${backendUrl}/discover-trends`);
      const data = await res.json();
      setTrends(data.trends || []);
    } catch (err) {
      console.error(err);
    } finally {
      setIsDiscovering(false);
    }
  };

  const handleEnhance = async () => {
    if (!topic.trim()) return;
    setIsEnhancing(true);
    try {
      const backendUrl = `http://${window.location.hostname}:8000`;
      const res = await fetch(`${backendUrl}/enhance-topic`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, angle, target_persona: targetPersona, direction: enhanceDirection, image_idea: imageIdea })
      });
      const data = await res.json();
      if (data.status === "success") {
        setTopic(data.enhanced_topic);
        setAngle(data.enhanced_angle);
        if (data.enhanced_image_idea) {
          setImageIdea(data.enhanced_image_idea);
        }
      }
    } catch (e) {
      console.error("Failed to enhance topic:", e);
    } finally {
      setIsEnhancing(false);
    }
  };

  return (
    <div style={{ maxWidth: 680, margin: '60px auto 0', animation: 'fadeUp 0.4s ease' }}>

      {/* Big editorial headline */}
      <div style={{ marginBottom: 40 }}>
        <p style={{ fontSize: 10, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--muted)', marginBottom: 10 }}>
          Mode B — Daily Generation
        </p>
        <h2 style={{
          fontFamily: 'var(--font-display)',
          fontSize: 'clamp(32px, 5vw, 52px)',
          fontWeight: 700,
          lineHeight: 1.05,
          letterSpacing: '-0.03em',
          color: 'var(--paper)',
        }}>
          What should<br />
          <em style={{ fontStyle: 'italic', color: 'var(--accent)' }}>the world read</em><br />
          today?
        </h2>
      </div>

      <div style={{ marginBottom: 40, borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: 24 }}>
        <button 
          onClick={handleDiscover} 
          disabled={isDiscovering}
          className="btn" 
          style={{ width: '100%', background: 'rgba(200,255,0,0.05)', borderColor: 'rgba(200,255,0,0.3)', color: 'var(--accent)' }}
        >
          {isDiscovering ? 'Scraping HackerNews & Web...' : '✨ Discover Trending Topics (Mode A)'}
        </button>

        {trends.length > 0 && (
          <div style={{ marginTop: 20, display: 'flex', flexDirection: 'column', gap: 12 }}>
            <span style={{ fontSize: 9, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--muted)' }}>Top Matches for ICP</span>
            {trends.map((t, idx) => (
              <div 
                key={idx} 
                onClick={() => { setTopic(t.topic); setAngle(t.reasoning); setTrends([]); }}
                style={{ 
                  padding: 16, 
                  background: 'rgba(200,255,0,0.05)', 
                  border: '1px solid rgba(200,255,0,0.2)', 
                  cursor: 'pointer',
                  borderRadius: 4,
                  transition: 'background 0.2s'
                }}
                onMouseOver={(e) => e.currentTarget.style.background = 'rgba(200,255,0,0.1)'}
                onMouseOut={(e) => e.currentTarget.style.background = 'rgba(200,255,0,0.05)'}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, gap: 16 }}>
                  <strong style={{ color: 'var(--paper)', fontSize: 13, lineHeight: 1.4 }}>{t.topic}</strong>
                  <span style={{ color: 'var(--accent)', fontFamily: 'var(--font-mono)', fontSize: 11, whiteSpace: 'nowrap' }}>
                    Score: {t.score}
                  </span>
                </div>
                <p style={{ color: 'var(--muted)', fontSize: 11, margin: 0, lineHeight: 1.5 }}>{t.reasoning}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Form fields */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 28 }}>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 6 }}>
            <label className="field-label" style={{ marginBottom: 0 }}>
              Topic / Keyword
            </label>
            <button 
              onClick={handleEnhance} 
              disabled={isEnhancing || !topic.trim()}
              style={{
                background: 'transparent',
                border: '1px solid rgba(200,255,0,0.3)',
                color: 'var(--accent)',
                fontSize: 10,
                padding: '4px 8px',
                borderRadius: 4,
                cursor: 'pointer',
                fontFamily: 'var(--font-mono)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                transition: 'all 0.2s'
              }}
            >
              {isEnhancing ? 'Enhancing...' : 'Enhance ✨'}
            </button>
          </div>
          <div style={{ position: 'relative' }}>
            <input
              type="text"
              value={topic}
              onChange={e => setTopic(e.target.value)}
              placeholder="Enterprise AI Adoption"
              style={{ paddingRight: 40 }}
            />
            {renderMicBtn('topic', setTopic)}
          </div>
        </div>

        <div>
          <label className="field-label">
            Enhancement Direction (Optional)
          </label>
          <div style={{ position: 'relative' }}>
            <input
              type="text"
              value={enhanceDirection}
              onChange={e => setEnhanceDirection(e.target.value)}
              placeholder="e.g. Make it more aggressive, focus on cost savings"
              style={{ paddingRight: 40 }}
            />
            {renderMicBtn('enhanceDirection', setEnhanceDirection)}
          </div>
        </div>

        <div>
          <label className="field-label">
            Your Angle or Opinion
          </label>
          <div style={{ position: 'relative' }}>
            <textarea
              value={angle}
              onChange={e => setAngle(e.target.value)}
              placeholder="What's your contrarian take? What do you know that others don't?"
              rows={4}
              style={{ paddingRight: 40 }}
            />
            {renderMicBtn('angle', setAngle, true)}
          </div>
        </div>

        <div>
          <label className="field-label">
            Image Idea
          </label>
          <div style={{ position: 'relative', marginBottom: 12 }}>
            <input
              type="text"
              value={imageIdea}
              onChange={e => setImageIdea(e.target.value)}
              placeholder="e.g. Minimalist chart showing 3x adoption curve"
              style={{ paddingRight: 40, marginBottom: 0 }}
            />
            {renderMicBtn('imageIdea', setImageIdea)}
          </div>
          <div className="platform-toggle-group">
            <div className="platform-toggle">
              <input
                type="radio"
                id="img-src-ai"
                name="imageSource"
                checked={imageSource === "ai"}
                onChange={() => setImageSource("ai")}
              />
              <label htmlFor="img-src-ai">AI Generated</label>
            </div>
            <div className="platform-toggle">
              <input
                type="radio"
                id="img-src-web"
                name="imageSource"
                checked={imageSource === "web"}
                onChange={() => setImageSource("web")}
              />
              <label htmlFor="img-src-web">Web Image</label>
            </div>
          </div>
        </div>

        <div>
          <label className="field-label">
            Target Persona (Who is this for?)
          </label>
          <div style={{ position: 'relative' }}>
            <input
              type="text"
              value={targetPersona}
              onChange={e => setTargetPersona(e.target.value)}
              placeholder="e.g. CTOs concerned about cloud costs, or CEOs looking for ROI"
              list="persona-suggestions"
              style={{ paddingRight: 40 }}
            />
            {renderMicBtn('targetPersona', setTargetPersona)}
          </div>
          <datalist id="persona-suggestions">
            <option value="CTO / VP Engineering (Technical & Architecture focus)" />
            <option value="CEO / Founder (Business outcomes, ROI & Strategy)" />
            <option value="Product Manager (User adoption & Time-to-market)" />
          </datalist>
        </div>

        {/* Tone row */}
        <div>
          <label className="field-label">Tone</label>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 0 }}>
            {tones.map(t => (
              <button
                key={t.value}
                onClick={() => setTone(t.value)}
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: 11,
                  letterSpacing: '0.04em',
                  padding: '9px 8px',
                  border: '1px solid rgba(242, 237, 228, 0.15)',
                  marginLeft: '-1px',
                  cursor: 'pointer',
                  transition: 'all 0.15s',
                  background: tone === t.value ? 'var(--accent-dim)' : 'transparent',
                  color: tone === t.value ? 'var(--accent)' : 'var(--muted)',
                  borderColor: tone === t.value ? 'rgba(200,255,0,0.35)' : 'rgba(242,237,228,0.15)',
                  zIndex: tone === t.value ? 1 : 0,
                  position: 'relative',
                }}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>

        {/* Author Voice row */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 6 }}>
            <label className="field-label" style={{ marginBottom: 0 }}>Author Voice</label>
            <button 
              onClick={() => setShowVoiceModal(true)} 
              style={{
                background: 'transparent',
                border: '1px solid rgba(200,255,0,0.3)',
                color: 'var(--accent)',
                fontSize: 10,
                padding: '4px 8px',
                borderRadius: 4,
                cursor: 'pointer',
                fontFamily: 'var(--font-mono)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                transition: 'all 0.2s'
              }}
            >
              + Clone Voice
            </button>
          </div>
          <div className="platform-toggle-group">
            <div className="platform-toggle">
              <input
                type="radio"
                id="voice-bitcot"
                name="authorVoice"
                checked={authorVoice === "bitcot"}
                onChange={() => setAuthorVoice("bitcot")}
              />
              <label htmlFor="voice-bitcot">Bitcot Brand</label>
            </div>
            {customVoices.map(voice => (
              <div className="platform-toggle" key={voice}>
                <input
                  type="radio"
                  id={`voice-${voice}`}
                  name="authorVoice"
                  checked={authorVoice === voice}
                  onChange={() => setAuthorVoice(voice)}
                />
                <label htmlFor={`voice-${voice}`}>{voice}</label>
              </div>
            ))}
          </div>
        </div>

        {/* Web Search Toggle */}
        <div>
          <label className="field-label">Research & Approval</label>
          <div className="platform-toggle-group">
            <div className="platform-toggle">
              <input
                type="checkbox"
                id="use-web-search"
                checked={useWebSearch}
                onChange={(e) => setUseWebSearch(e.target.checked)}
              />
              <label htmlFor="use-web-search" style={{ color: useWebSearch ? 'var(--accent)' : 'inherit' }}>
                Enable Web Search (Fetch recent facts)
              </label>
            </div>
            <div className="platform-toggle">
              <input
                type="checkbox"
                id="require-approval"
                checked={requireApproval}
                onChange={(e) => setRequireApproval(e.target.checked)}
              />
              <label htmlFor="require-approval" style={{ color: requireApproval ? 'var(--accent)' : 'inherit' }}>
                Require Research Approval Mid-Flight
              </label>
            </div>
          </div>
        </div>

        {/* Platform toggles */}
        <div>
          <label className="field-label">Publish To</label>
          <div className="platform-toggle-group">
            {platforms.map(p => (
              <div className="platform-toggle" key={p}>
                <input
                  type="checkbox"
                  id={`plat-${p}`}
                  checked={activePlatforms.has(p)}
                  onChange={() => togglePlatform(p)}
                />
                <label htmlFor={`plat-${p}`}>{p}</label>
              </div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div style={{ paddingTop: 8, display: 'flex', alignItems: 'center', gap: 20 }}>
          {!isLoading ? (
            <button
              className="btn btn-primary"
              onClick={() => onGenerate({ topic, angle, imageIdea, targetPersona, tone, authorVoice, useWebSearch, requireApproval, imageSource, platforms: [...activePlatforms] })}
              disabled={!topic.trim()}
              style={{ padding: '12px 32px', fontSize: 12 }}
            >
              Generate All Formats →
            </button>
          ) : (
            <button
              className="btn"
              onClick={onStop}
              style={{ padding: '12px 32px', fontSize: 12, background: 'rgba(255, 65, 54, 0.1)', color: 'var(--danger)', border: '1px solid var(--danger)' }}
            >
              Stop Generation ⏹
            </button>
          )}
          {isLoading && (
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 10 }}>
              <div>
                <div className="loading-bar" />
                <p style={{ fontSize: 10, color: 'var(--muted)', marginTop: 6, letterSpacing: '0.1em', textTransform: 'uppercase' }}>
                  Pipeline Active
                </p>
              </div>
              <div style={{
                background: '#0a0a0a',
                border: '1px solid rgba(200,255,0,0.2)',
                borderRadius: 4,
                padding: 12,
                height: 120,
                overflowY: 'auto',
                fontFamily: 'var(--font-mono)',
                fontSize: 11,
                color: 'var(--paper)',
                display: 'flex',
                flexDirection: 'column',
                gap: 6
              }}>
                {(!agentLogs || agentLogs.length === 0) ? (
                  <div style={{ color: 'var(--muted)', fontStyle: 'italic' }}>Waiting for agent logs...</div>
                ) : (
                  agentLogs.map((log, i) => (
                    <div key={i} style={{ display: 'flex', gap: 8 }}>
                      <span style={{ color: 'var(--accent)', opacity: 0.7 }}>[{log.agent}]</span>
                      <span>{log.message}</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
        </div>
      </div>

      {showVoiceModal && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          backdropFilter: 'blur(5px)'
        }}>
          <div style={{
            background: 'var(--surface)',
            border: '1px solid var(--border)',
            padding: 30,
            borderRadius: 8,
            width: 500,
            display: 'flex',
            flexDirection: 'column',
            gap: 20
          }}>
            <h3 style={{ margin: 0, color: 'var(--accent)' }}>Clone Voice Persona</h3>
            <div>
              <label className="field-label">Persona Name</label>
              <input 
                type="text" 
                placeholder="e.g. Raj Sanghvi" 
                value={newVoiceName}
                onChange={e => setNewVoiceName(e.target.value)}
              />
            </div>
            <div>
              <label className="field-label">Writing Sample (Paste past LinkedIn posts or articles)</label>
              <textarea 
                style={{ height: 150 }}
                placeholder="Paste at least 150 words of their best writing..."
                value={newVoiceSample}
                onChange={e => setNewVoiceSample(e.target.value)}
              />
            </div>
            <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
              <button 
                className="secondary-btn" 
                onClick={() => setShowVoiceModal(false)}
                disabled={isCloning}
              >
                Cancel
              </button>
              <button 
                className="action-btn" 
                onClick={handleCloneVoice}
                disabled={isCloning || !newVoiceName || !newVoiceSample}
              >
                {isCloning ? 'Cloning...' : 'Extract Voice DNA ✨'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
