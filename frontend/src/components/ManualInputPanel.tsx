"use client";

import React, { useState } from 'react';

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
}: {
  onGenerate: (data: any) => void;
  isLoading: boolean;
}) {
  const [topic, setTopic]       = useState("");
  const [angle, setAngle]       = useState("");
  const [imageIdea, setImageIdea] = useState("");
  const [tone, setTone]         = useState("thought_leader");
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

  const handleEnhance = async () => {
    if (!topic.trim()) return;
    setIsEnhancing(true);
    try {
      const res = await fetch("http://localhost:8000/enhance-topic", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic })
      });
      const data = await res.json();
      if (data.status === "success") {
        setTopic(data.enhanced_topic);
        setAngle(data.enhanced_angle);
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

      {/* Form fields */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 28 }}>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 6 }}>
            <label className="field-label" style={{ marginBottom: 0 }}>Topic / Keyword</label>
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
          <input
            type="text"
            value={topic}
            onChange={e => setTopic(e.target.value)}
            placeholder="Enterprise AI Adoption"
          />
        </div>

        <div>
          <label className="field-label">Your Angle or Opinion</label>
          <textarea
            value={angle}
            onChange={e => setAngle(e.target.value)}
            placeholder="What's your contrarian take? What do you know that others don't?"
            rows={4}
          />
        </div>

        <div>
          <label className="field-label">Image Idea</label>
          <input
            type="text"
            value={imageIdea}
            onChange={e => setImageIdea(e.target.value)}
            placeholder="e.g. Minimalist chart showing 3x adoption curve"
          />
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
          <button
            className="btn btn-primary"
            onClick={() => onGenerate({ topic, angle, imageIdea, tone, platforms: [...activePlatforms] })}
            disabled={isLoading || !topic.trim()}
            style={{ padding: '12px 32px', fontSize: 12 }}
          >
            {isLoading ? 'Generating…' : 'Generate All Formats →'}
          </button>
          {isLoading && (
            <div style={{ flex: 1 }}>
              <div className="loading-bar" />
              <p style={{ fontSize: 10, color: 'var(--muted)', marginTop: 6, letterSpacing: '0.1em', textTransform: 'uppercase' }}>
                ICP scoring → SEO analysis → Writing drafts
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
