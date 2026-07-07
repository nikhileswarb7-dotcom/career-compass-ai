import React, { useState, useEffect, useRef } from 'react';
import { useApp, API_BASE } from '../App';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, 
  Send, 
  Bot, 
  User, 
  Target, 
  Compass, 
  Flame, 
  Cpu,
  AlertCircle,
  TrendingUp,
  Award
} from 'lucide-react';
import './AIMentor.css';

// Simple Markdown to HTML parser utility to render tables, lists, bold, and code blocks
function parseMarkdown(text) {
  if (!text) return '';
  
  let html = text;

  // Code blocks: ```code```
  html = html.replace(/```(\w*)\n([\s\S]+?)\n```/g, (match, lang, code) => {
    return `<pre><code class="language-${lang}">${code.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre>`;
  });

  // Inline code: `code`
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  // Bold: **text**
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

  // Tables
  html = html.replace(/\|(.+)\|/g, (match, rowContent) => {
    const cols = rowContent.split('|').map(c => c.trim());
    if (rowContent.includes('---')) {
      return ''; // ignore separator lines
    }
    const isHeader = html.indexOf(match) === html.indexOf('|'); // very basic heuristic for th
    const cellTag = isHeader ? 'th' : 'td';
    const cellsHtml = cols.filter(c => c !== '').map(c => `<${cellTag}>${c}</${cellTag}>`).join('');
    return `<tr>${cellsHtml}</tr>`;
  });

  // Wrap Table rows in <table>
  html = html.replace(/(<tr>[\s\S]+?<\/tr>)/g, '<table>$1</table>');
  // De-duplicate table tags if multiple rows
  html = html.replace(/<\/table>\s*<table>/g, '');

  // Bullet items: - item
  html = html.replace(/^\s*[-*]\s+(.+)$/gm, '<li>$1</li>');
  
  // Wrap list items
  html = html.replace(/(<li>[\s\S]+?<\/li>)/g, '<ul>$1</ul>');
  html = html.replace(/<\/ul>\s*<ul>/g, '');

  // Line breaks to <br/> (excluding within table or pre blocks)
  const lines = html.split('\n');
  let inPre = false;
  let inTable = false;
  const processedLines = lines.map(line => {
    if (line.includes('<pre>')) inPre = true;
    if (line.includes('</pre>')) inPre = false;
    if (line.includes('<table>')) inTable = true;
    if (line.includes('</table>')) inTable = false;

    if (!inPre && !inTable && line.trim() !== '') {
      return line + '<br/>';
    }
    return line;
  });
  html = processedLines.join('\n');

  return html;
}

export default function AIMentor() {
  const { sessionId, sessionStatus, careerPlan, setCareerPlan } = useApp();
  const plan = careerPlan || {};
  
  // Chat state
  const [messages, setMessages] = useState([
    { sender: 'coach', text: "Hello! I am your SDE Placement Mentor. I've analyzed your vector profile indices and I am ready to guide you on system design architectures, high-performance database patterns, or target interview preparation strategies. Ask me anything!" }
  ]);
  const [input, setInput] = useState('');
  const [typing, setTyping] = useState(false);

  // Mock Interview Mode States
  const [chatMode, setChatMode] = useState('guidance'); // 'guidance' or 'interview'
  const [jds, setJds] = useState([]);
  const [selectedJdId, setSelectedJdId] = useState('');
  const [interviewStarted, setInterviewStarted] = useState(false);
  const [loadingJds, setLoadingJds] = useState(false);

  const messagesEndRef = useRef(null);

  // Sync scroll on message length updates
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, typing]);

  // Load chat history or sync details on mount
  useEffect(() => {
    const storedHistory = localStorage.getItem('mentor_chat_history');
    if (storedHistory) {
      try {
        setMessages(JSON.parse(storedHistory));
      } catch (e) {
        console.error("Failed to load chat history", e);
      }
    }

    if (sessionId && !careerPlan) {
      async function loadProfile() {
        try {
          const skipLlm = localStorage.getItem('skip_llm') === 'true' ? '?skip_llm=true' : '';
          const res = await fetch(`${API_BASE}/api/readiness/${sessionId}${skipLlm}`);
          if (res.ok) {
            const data = await res.json();
            setCareerPlan(data);
          }
        } catch (e) {
          console.warn("Failed to load profile details in AI Mentor side panel", e);
        }
      }
      loadProfile();
    }
  }, [sessionId, careerPlan, setCareerPlan]);

  // Fetch job descriptions from database on mount
  useEffect(() => {
    async function loadJds() {
      setLoadingJds(true);
      try {
        const response = await fetch(`${API_BASE}/api/job-descriptions`);
        if (response.ok) {
          const data = await response.json();
          setJds(data);
          if (data.length > 0) {
            setSelectedJdId(data[0].jd_id.toString());
          }
        }
      } catch (err) {
        console.error("Failed to load JDs:", err);
      } finally {
        setLoadingJds(false);
      }
    }
    loadJds();
  }, []);

  const handleStartInterview = async () => {
    if (!selectedJdId) return;
    setTyping(true);
    setInterviewStarted(true);
    setMessages([]);

    try {
      const response = await fetch(`${API_BASE}/api/chat/interview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId || 'dummy-session',
          jd_id: parseInt(selectedJdId),
          message: '/start'
        })
      });
      if (response.ok) {
        const data = await response.json();
        setMessages([{ sender: 'coach', text: data.reply }]);
      }
    } catch (err) {
      console.error("Failed to start mock interview", err);
      setMessages([{ sender: 'coach', text: "Failed to initialize mock interview session. Please try again." }]);
    } finally {
      setTyping(false);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    const query = input.trim();
    if (!query) return;

    const newMessages = [...messages, { sender: 'user', text: query }];
    setMessages(newMessages);
    setInput('');
    setTyping(true);

    if (chatMode === 'guidance') {
      localStorage.setItem('mentor_chat_history', JSON.stringify(newMessages));

      const payload = {
        message: query,
        stage_title: plan.timeline?.stages?.[parseInt(localStorage.getItem('roadmap_current_stage') || '0')]?.title || 'active stage',
        dream_company: plan.dream_company || 'Blinkit',
        dream_sector: plan.dream_sector || 'Quick-Commerce',
        qualification: plan.qualification || 'Candidate',
        session_id: sessionId || ''
      };

      try {
        const response = await fetch(`${API_BASE}/api/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (response.ok) {
          const data = await response.json();
          const updated = [...newMessages, { sender: 'coach', text: data.reply || "I didn't capture that. Could you clarify your technical query?" }];
          setMessages(updated);
          localStorage.setItem('mentor_chat_history', JSON.stringify(updated));
        } else {
          throw new Error("Chat api failed");
        }
      } catch (err) {
        console.warn("Chat API error. Loading offline response template.", err);
        const offlineReply = `I am currently operating in offline SDE advice mode. For your query "${query}", I recommend focusing on closing your high-priority missing skill gaps in ${plan.gaps?.high_priority_missing?.join(', ') || 'distributed systems'} and practicing the Sandbox database assessments on your timeline roadmap.`;
        const updated = [...newMessages, { sender: 'coach', text: offlineReply }];
        setMessages(updated);
        localStorage.setItem('mentor_chat_history', JSON.stringify(updated));
      } finally {
        setTyping(false);
      }
    } else {
      // Mock Interview Mode
      try {
        const response = await fetch(`${API_BASE}/api/chat/interview`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: sessionId || 'dummy-session',
            jd_id: parseInt(selectedJdId),
            message: query
          })
        });

        if (response.ok) {
          const data = await response.json();
          setMessages([...newMessages, { sender: 'coach', text: data.reply }]);
        } else {
          throw new Error("Interview chat api failed");
        }
      } catch (err) {
        console.error("Interview API error", err);
        setMessages([...newMessages, { sender: 'coach', text: "Connection error. Failed to retrieve interviewer response." }]);
      } finally {
        setTyping(false);
      }
    }
  };

  const handleClearHistory = () => {
    if (chatMode === 'interview') {
      if (window.confirm("Do you want to reset and start a new mock interview session?")) {
        setInterviewStarted(false);
        setMessages([]);
      }
      return;
    }

    if (window.confirm("Do you want to reset your conversation history with your AI Mentor?")) {
      const initial = [{ sender: 'coach', text: "Hello! I am your SDE Placement Mentor. I've analyzed your vector profile indices and I am ready to guide you on system design architectures, high-performance database patterns, or target interview preparation strategies. Ask me anything!" }];
      setMessages(initial);
      localStorage.removeItem('mentor_chat_history');
    }
  };

  const gaps = Array.from(new Set([
    ...(plan.gaps?.high_priority_missing || []),
    ...(plan.gaps?.medium_priority_missing || [])
  ]));

  const currentSelectedJd = selectedJdId ? jds.find(j => j.jd_id === parseInt(selectedJdId)) : null;

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.15 }}
      className="ai-mentor-page"
    >
      {/* Chat Section */}
      <div className="mentor-chat-panel">
        {/* Chat Mode Switcher Tabs */}
        <div style={{ display: 'flex', borderBottom: '1px solid var(--border-glass)', background: 'var(--bg-card)', padding: '0.5rem 1.5rem', gap: '1rem', alignItems: 'center' }}>
          <button 
            type="button"
            onClick={() => { setChatMode('guidance'); setInterviewStarted(false); }}
            style={{ 
              background: chatMode === 'guidance' ? 'var(--primary-glow)' : 'transparent',
              color: chatMode === 'guidance' ? 'var(--accent-primary)' : 'var(--text-muted)',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              fontWeight: 650,
              cursor: 'pointer',
              fontSize: '0.85rem'
            }}
          >
            General Q&A Coach
          </button>
          <button 
            type="button"
            onClick={() => setChatMode('interview')}
            style={{ 
              background: chatMode === 'interview' ? 'var(--primary-glow)' : 'transparent',
              color: chatMode === 'interview' ? 'var(--accent-primary)' : 'var(--text-muted)',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              fontWeight: 650,
              cursor: 'pointer',
              fontSize: '0.85rem'
            }}
          >
            Job Description Interview
          </button>
        </div>

        <div className="chat-conversation-area">
          {chatMode === 'interview' && !interviewStarted ? (
            <div className="interview-selection-wrapper" style={{ padding: '2rem 1.5rem', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1.25rem', margin: 'auto' }}>
              <Award size={48} style={{ color: 'var(--accent-primary)', marginBottom: '0.25rem' }} />
              <h2 style={{ fontFamily: 'var(--font-title)', fontSize: '1.4rem', fontWeight: 800 }}>Simulated Mock Interview</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', maxWidth: '480px', lineHeight: '1.5' }}>
                Select a target SDE Job Description from Swiggy, Flipkart, Uber, Zomato, or Microsoft. The coach will interview you dynamically based on the target requirements.
              </p>
              
              <div style={{ width: '100%', maxWidth: '380px', display: 'flex', flexDirection: 'column', gap: '0.4rem', textAlign: 'left' }}>
                <label style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-secondary)' }}>Target Job Description</label>
                <select 
                  className="form-input" 
                  value={selectedJdId} 
                  onChange={e => setSelectedJdId(e.target.value)}
                  style={{ width: '100%', padding: '0.65rem', borderRadius: '8px', background: 'var(--bg-secondary)', color: 'var(--text-main)', border: '1px solid var(--border-glass)' }}
                >
                  {jds.map(jd => (
                    <option key={jd.jd_id} value={jd.jd_id}>
                      {jd.company_name} - {jd.role_name} ({jd.experience_required_years} Yrs)
                    </option>
                  ))}
                </select>
              </div>

              {currentSelectedJd && (
                <div className="glass-card" style={{ padding: '1rem', width: '100%', maxWidth: '480px', textAlign: 'left', fontSize: '0.82rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  <div><strong>Role Overview:</strong> {currentSelectedJd.description}</div>
                  <div>
                    <strong>Core Requirements:</strong>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem', marginTop: '0.25rem' }}>
                      {currentSelectedJd.requirements.map(req => (
                        <span key={req} className="dashboard-gap-badge success" style={{ fontSize: '0.7rem', padding: '0.15rem 0.4rem' }}>{req}</span>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              <button type="button" className="btn-primary" onClick={handleStartInterview} style={{ padding: '0.65rem 1.5rem', borderRadius: '8px' }}>
                <span>Start Mock Interview</span>
              </button>
            </div>
          ) : (
            <>
              {messages.map((msg, index) => {
                const isCoach = msg.sender === 'coach';
                return (
                  <div key={index} className={`message-bubble ${isCoach ? 'coach' : 'user'}`}>
                    <div className="avatar-icon-box">
                      {isCoach ? <Bot size={16} /> : <User size={16} />}
                    </div>
                    <div className="message-content">
                      <div 
                        className="markdown-body"
                        dangerouslySetInnerHTML={{ __html: parseMarkdown(msg.text) }}
                      />
                    </div>
                  </div>
                );
              })}
              
              {typing && (
                <div className="message-bubble coach">
                  <div className="avatar-icon-box">
                    <Bot size={16} />
                  </div>
                  <div className="message-content">
                    <div style={{ display: 'flex', gap: '0.25rem', alignItems: 'center', padding: '0.25rem 0' }}>
                      <div className="skeleton" style={{ width: '8px', height: '8px', borderRadius: '50%' }} />
                      <div className="skeleton" style={{ width: '8px', height: '8px', borderRadius: '50%', animationDelay: '0.2s' }} />
                      <div className="skeleton" style={{ width: '8px', height: '8px', borderRadius: '50%', animationDelay: '0.4s' }} />
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSend} className="chat-input-container">
          <button 
            type="button" 
            className="btn-secondary" 
            onClick={handleClearHistory}
            style={{ padding: '0.7rem' }}
            title={chatMode === 'interview' ? "Reset Interview" : "Reset history"}
          >
            {chatMode === 'interview' ? 'Reset' : 'Clear'}
          </button>
          <input 
            type="text" 
            className="form-input chat-text-input"
            placeholder={chatMode === 'interview' ? "Type your response to the interviewer's question..." : "Ask your AI Mentor about system design, code patterns, or resumes..."}
            value={input}
            onChange={e => setInput(e.target.value)}
            disabled={typing || (chatMode === 'interview' && !interviewStarted)}
          />
          <button 
            type="submit" 
            className="btn-primary btn-send-message" 
            disabled={!input.trim() || typing || (chatMode === 'interview' && !interviewStarted)}
          >
            <Send size={16} />
          </button>
        </form>
      </div>

      {/* Side Context Panel */}
      <aside className="mentor-context-aside">
        {/* Goal Card */}
        <div className="glass-card aside-context-card">
          <h4 className="aside-card-title">
            <Target size={14} style={{ color: 'var(--accent-primary)' }} />
            <span>Target Goal</span>
          </h4>
          <div className="context-lbl">Dream SDE Company</div>
          <div className="context-val dream">{plan.dream_company || 'Blinkit'}</div>
          
          <div className="context-lbl" style={{ marginTop: '0.75rem' }}>Role alignment</div>
          <div className="context-val">{plan.target_role || 'Software Development Engineer'}</div>

          <div className="context-lbl" style={{ marginTop: '0.75rem' }}>Hiring bar readiness</div>
          <div className="context-val" style={{ color: 'var(--success)' }}>{plan.readiness_score || 35}% readiness score</div>
        </div>

        {/* Weak skills gaps card */}
        <div className="glass-card aside-context-card">
          <h4 className="aside-card-title">
            <Cpu size={14} style={{ color: 'var(--accent-secondary)' }} />
            <span>Core missing skills</span>
          </h4>
          <div className="context-gaps-list">
            {gaps.map((gap, i) => (
              <span key={i} className="context-gap-badge">{gap}</span>
            ))}
            {gaps.length === 0 && (
              <span className="context-gap-badge" style={{ borderColor: 'var(--success)', color: 'var(--success)' }}>
                No missing skill gaps identified!
              </span>
            )}
          </div>
        </div>

        {/* Active Stage & tasks card */}
        <div className="glass-card aside-context-card">
          <h4 className="aside-card-title">
            <Compass size={14} style={{ color: 'var(--warning)' }} />
            <span>Upcoming stages</span>
          </h4>
          <div className="upcoming-tasks-list">
            {(plan.timeline?.stages || []).slice(0, 4).map((stage, i) => (
              <div key={i} className="task-item-row">
                <span className="task-dot" />
                <span>{stage.title}</span>
              </div>
            ))}
          </div>
        </div>
      </aside>
    </motion.div>
  );
}
