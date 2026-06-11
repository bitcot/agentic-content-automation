"use client";

import React, { useState } from 'react';

import { marked } from 'marked';
import DOMPurify from 'dompurify';

function renderMarkdown(text: string) {
  if (!text) return { __html: '' };
  let processedText = text.replace(/(\[NEEDS HUMAN CHECK:[^\]]+\])/g, '<mark class="needs-check">$1</mark>');
  const rawHtml = marked.parse(processedText, { async: false }) as string;
  
  if (typeof window !== 'undefined') {
    return { 
      __html: DOMPurify.sanitize(rawHtml, { 
        ADD_ATTR: ['class', 'style', 'target'], 
        ADD_TAGS: ['mark'] 
      }) 
    };
  }
  return { __html: rawHtml };
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
  onRegenerate,
}: {
  draftData: any;
  onReject: () => void;
  onApprove: () => void;
  onRegenerate?: (target_part: string, feedback: string) => void;
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
  const [showRegen, setShowRegen] = useState(false);
  const [regenTarget, setRegenTarget] = useState('all');
  const [regenFeedback, setRegenFeedback] = useState('');

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
                  {draftData.token_usage.estimated_cost_usd !== undefined && (
                    <>
                      <span style={{ color: 'var(--muted)' }}>|</span>
                      <span>Cost: ${draftData.token_usage.estimated_cost_usd.toFixed(4)}</span>
                    </>
                  )}
                </div>
              </div>
            </>
          )}
        </div>

        <div style={{ display: 'flex', gap: 0 }}>
          <button className="btn btn-danger" onClick={onReject} style={{ fontSize: 11 }}>Reject</button>
          <button className="btn" onClick={() => setShowRegen(true)} style={{ fontSize: 11, marginLeft: -1 }}>Regenerate</button>
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
        {activeTab === 'blog' && (
          <button 
            className="btn btn-primary"
            onClick={async () => {
              const element = document.getElementById('blog-pdf-content');
              if (!element) return;
              
              const images = element.querySelectorAll('img');
              const originalSrcs = new Map();
              const loadPromises: Promise<void>[] = [];
              
              images.forEach(img => {
                if (img.src && !img.src.startsWith('data:') && !img.src.includes('proxy-image')) {
                  originalSrcs.set(img, img.src);
                  const p = new Promise<void>(resolve => {
                    img.onload = () => resolve();
                    img.onerror = () => resolve();
                  });
                  loadPromises.push(p);
                  img.src = `http://localhost:8000/proxy-image?url=${encodeURIComponent(img.src)}`;
                }
              });

              if (loadPromises.length > 0) {
                await Promise.all(loadPromises);
              }

              // Inject global print styles to prevent page breaks inside elements
              const style = document.createElement('style');
              style.innerHTML = `
                #blog-pdf-content img, #blog-pdf-content p, #blog-pdf-content h1, #blog-pdf-content h2, #blog-pdf-content h3, #blog-pdf-content li, #blog-pdf-content .key-takeaways {
                  page-break-inside: avoid !important;
                  break-inside: avoid !important;
                }
              `;
              document.head.appendChild(style);

              const html2pdf = (await import('html2pdf.js')).default;
              html2pdf().set({
                margin: 0.4,
                filename: `${blog?.url_slug || 'blog'}.pdf`,
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 2, useCORS: true, backgroundColor: '#0a0a0a' },
                jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' },
                pagebreak: { mode: ['css', 'legacy'], avoid: ['img', 'h1', 'h2', 'h3', 'p', 'li', '.key-takeaways'] }
              }).from(element).save().then(() => {
                document.head.removeChild(style);
                images.forEach(img => {
                  if (originalSrcs.has(img)) img.src = originalSrcs.get(img);
                });
              });
            }}
            style={{ 
              marginLeft: 16, 
              fontSize: 11, 
              padding: '6px 14px', 
              display: 'flex', 
              alignItems: 'center', 
              gap: 6,
              boxShadow: '0 0 12px rgba(200,255,0,0.2)',
              border: '1px solid rgba(200,255,0,0.5)'
            }}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            Export PDF
          </button>
        )}
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
            {blog.title_tag && (
              <p style={{ fontSize: 11, color: 'var(--muted)', fontFamily: 'var(--font-mono)', marginBottom: 8, padding: '8px 12px', background: 'rgba(242,237,228,0.03)', border: 'var(--rule)' }}>
                <span style={{ color: 'var(--muted)', marginRight: 8 }}>TITLE TAG:</span>{blog.title_tag}
              </p>
            )}
            {blog.meta_description && (
              <p style={{ fontSize: 11, color: 'var(--muted)', fontFamily: 'var(--font-mono)', marginBottom: 8, padding: '8px 12px', background: 'rgba(242,237,228,0.03)', border: 'var(--rule)' }}>
                <span style={{ color: 'var(--muted)', marginRight: 8 }}>META DESC:</span>{blog.meta_description}
              </p>
            )}
            {blog.url_slug && (
              <p style={{ fontSize: 11, color: 'var(--muted)', fontFamily: 'var(--font-mono)', marginBottom: 18, padding: '8px 12px', background: 'rgba(242,237,228,0.03)', border: 'var(--rule)' }}>
                <span style={{ color: 'var(--muted)', marginRight: 8 }}>URL SLUG:</span>/{blog.url_slug}
              </p>
            )}
            
            {blog.image_url && (
              <div style={{ marginBottom: 20, padding: '12px 16px', background: 'rgba(242,237,228,0.03)', border: 'var(--rule)' }}>
                <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start', marginBottom: 12 }}>
                  <div style={{ color: 'var(--accent)', marginTop: 2 }}>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                      <circle cx="8.5" cy="8.5" r="1.5"></circle>
                      <polyline points="21 15 16 10 5 21"></polyline>
                    </svg>
                  </div>
                  <div>
                    <span style={{ fontSize: 9, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--muted)', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                      Generated Header Image (16:9)
                    </span>
                    {blog.image_prompt && <p style={{ fontSize: 11, color: 'var(--paper)', margin: 0, fontStyle: 'italic', lineHeight: 1.5 }}>{blog.image_prompt}</p>}
                    {blog.image_alt_text && <p style={{ fontSize: 10, color: 'var(--accent)', marginTop: 8, fontFamily: 'var(--font-mono)' }}>ALT TEXT: {blog.image_alt_text}</p>}
                  </div>
                </div>
              </div>
            )}
            
            <div id="blog-pdf-content" style={{ padding: '24px', background: '#0a0a0a', color: '#e6e6e6', borderRadius: 8, border: '1px solid rgba(255,255,255,0.05)' }}>
              {blog.image_url && (
                <a href={blog.image_url} target="_blank" rel="noopener noreferrer">
                  <img src={blog.image_url} alt={blog.image_alt_text || "Generated Header"} crossOrigin="anonymous" style={{ width: '100%', maxHeight: '300px', objectFit: 'cover', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.1)', marginBottom: 24 }} />
                </a>
              )}
              {blog.h1_title && <h1 style={{ fontSize: 28, marginBottom: 24, color: '#fff', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: 16 }}>{blog.h1_title}</h1>}
              <div 
                className="draft-area rendered-markdown" 
                dangerouslySetInnerHTML={renderMarkdown(blog.body || '—')} 
                style={{ minHeight: 340 }} 
              />
            </div>
            {blog.internal_links?.length > 0 && (
              <div style={{ marginTop: 16, display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
                <span style={{ fontSize: 9, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--muted)' }}>SEO Internal Links:</span>
                {blog.internal_links.map((link: string, i: number) => (
                  <span key={i} style={{ fontSize: 10, color: 'var(--accent)', fontFamily: 'var(--font-mono)', padding: '2px 6px', border: '1px solid rgba(200,255,0,0.2)' }}>{link}</span>
                ))}
              </div>
            )}
            
            {blog.json_ld_schema && (
              <div style={{ marginTop: 20, padding: '12px 16px', background: '#0a0a0a', border: '1px solid #333', borderRadius: 4 }}>
                <span style={{ fontSize: 9, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--muted)' }}>JSON-LD Schema (Rich Snippets)</span>
                <pre style={{ fontSize: 10, color: '#A3B3CC', fontFamily: 'var(--font-mono)', whiteSpace: 'pre-wrap', marginTop: 8, overflowX: 'auto' }}>
                  {typeof blog.json_ld_schema === 'string' ? blog.json_ld_schema : JSON.stringify(blog.json_ld_schema, null, 2)}
                </pre>
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

            {linkedin.image_url && (
              <div style={{ marginBottom: 20, padding: '12px 16px', background: 'rgba(242,237,228,0.03)', border: 'var(--rule)' }}>
                <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start', marginBottom: 12 }}>
                  <div style={{ color: 'var(--accent)', marginTop: 2 }}>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                      <circle cx="8.5" cy="8.5" r="1.5"></circle>
                      <polyline points="21 15 16 10 5 21"></polyline>
                    </svg>
                  </div>
                  <div>
                    <span style={{ fontSize: 9, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--muted)', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                      Generated Post Graphic (1:1)
                    </span>
                    {linkedin.image_prompt && <p style={{ fontSize: 11, color: 'var(--paper)', margin: 0, fontStyle: 'italic', lineHeight: 1.5 }}>{linkedin.image_prompt}</p>}
                  </div>
                </div>
                <a href={linkedin.image_url} target="_blank" rel="noopener noreferrer">
                  <img src={linkedin.image_url} alt="Generated LinkedIn Graphic" style={{ width: '100%', maxWidth: '300px', objectFit: 'cover', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.1)' }} />
                </a>
              </div>
            )}
            <div 
              className="draft-area rendered-markdown" 
              dangerouslySetInnerHTML={renderMarkdown(linkedin.post || '—')} 
              style={{ minHeight: 200, padding: 24 }} 
            />
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
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', borderTop: 'var(--rule)' }}>
        <div style={{ padding: '24px 32px' }}>
          <p className="panel-label" style={{ margin: 0, marginBottom: 14, paddingBottom: 10, borderBottom: 'var(--rule)' }}>Schedule</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14, maxWidth: '600px' }}>
            {['LinkedIn', 'Blog Post', 'X Thread'].map(p => (
              <div key={p}>
                <label className="field-label">{p} Publication Time</label>
                <input type="datetime-local" />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Regenerate Modal */}
      {showRegen && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.8)', zIndex: 100,
          display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
          <div style={{
            background: 'var(--ink)', border: 'var(--rule-strong)', padding: '32px',
            width: 440, maxWidth: '90%', boxShadow: '0 24px 48px rgba(0,0,0,0.5)',
            position: 'relative'
          }}>
            <h3 style={{ margin: 0, marginBottom: 20, fontFamily: 'var(--font-display)', fontSize: 20, color: 'var(--paper)' }}>Regenerate Content</h3>
            
            <label className="field-label" style={{ marginBottom: 8, color: 'var(--accent)' }}>What to regenerate?</label>
            <select className="input-field" value={regenTarget} onChange={e => setRegenTarget(e.target.value)} style={{ marginBottom: 20, width: '100%', background: 'rgba(255,255,255,0.05)', color: '#fff' }}>
              <option value="all">Everything</option>
              <option value="blog">Blog Post</option>
              <option value="linkedin">LinkedIn Post</option>
              <option value="x_thread">X Thread</option>
              <option value="blog_image">Blog Image</option>
              <option value="linkedin_image">LinkedIn Image</option>
            </select>

            <label className="field-label" style={{ marginBottom: 8, color: 'var(--accent)' }}>Feedback / Issue</label>
            <textarea 
              className="input-field" 
              rows={4} 
              value={regenFeedback}
              onChange={e => setRegenFeedback(e.target.value)}
              placeholder="E.g., The hook is too generic, make it more controversial..."
              style={{ marginBottom: 28, resize: 'none', width: '100%', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
            />

            <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
              <button className="btn" onClick={() => setShowRegen(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={() => {
                setShowRegen(false);
                onRegenerate?.(regenTarget, regenFeedback);
              }}>Submit</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
