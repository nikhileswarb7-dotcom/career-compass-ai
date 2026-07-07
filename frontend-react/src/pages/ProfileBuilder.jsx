import React, { useState, useEffect } from 'react';
import { useApp, API_BASE } from '../App';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, 
  FileText, 
  Copy, 
  Check, 
  AlertCircle, 
  Cpu, 
  RefreshCw, 
  ChevronRight, 
  Eye, 
  Code as CodeIcon,
  Plus
} from 'lucide-react';
import './ProfileBuilder.css';

// Custom inline SVG components for LinkedIn and GitHub
const Linkedin = ({ size = 16, ...props }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    {...props}
  >
    <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z" />
    <rect width="4" height="12" x="2" y="9" />
    <circle cx="4" cy="4" r="2" />
  </svg>
);

const Github = ({ size = 16, ...props }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    {...props}
  >
    <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4" />
    <path d="M9 18c-4.51 2-5-2-7-2" />
  </svg>
);

export default function ProfileBuilder() {
  const { sessionId, careerPlan } = useApp();
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [error, setError] = useState(null);
  
  // Intake fields
  const [name, setName] = useState('');
  const [dreamCompany, setDreamCompany] = useState('Blinkit');
  const [targetRole, setTargetRole] = useState('Software Development Engineer');
  const [projectName, setProjectName] = useState('');
  const [skills, setSkills] = useState([]);
  const [newSkill, setNewSkill] = useState('');
  
  // Tabs: 'resume' | 'linkedin' | 'github'
  const [activeTab, setActiveTab] = useState('linkedin');
  const [githubMode, setGithubMode] = useState('preview');

  // Outputs
  const [generatedData, setGeneratedData] = useState(null);
  const [copiedStates, setCopiedStates] = useState({});

  // Loading steps text
  const loadingSteps = [
    "Establishing connection with Google Gemini...",
    "Synthesizing quantitative SDE resume bullets...",
    "Composing LinkedIn summary...",
    "Compiling GitHub README structure..."
  ];

  useEffect(() => {
    if (loading) {
      const interval = setInterval(() => {
        setLoadingStep(prev => (prev < loadingSteps.length - 1 ? prev + 1 : prev));
      }, 1200);
      return () => clearInterval(interval);
    }
  }, [loading]);

  useEffect(() => {
    if (!sessionId) return;

    async function fetchOnboardingDetails() {
      try {
        const res = await fetch(`${API_BASE}/api/readiness/${sessionId}`);
        if (res.ok) {
          const data = await res.json();
          setName(data.name || '');
          setDreamCompany(data.dream_company || 'Blinkit');
          setTargetRole(data.target_role || 'Software Development Engineer');
          setSkills(data.known_skills || []);
          
          if (data.projects && data.projects.length > 0) {
            const firstProj = data.projects[0];
            setProjectName(firstProj.name || firstProj.title || 'High-Concurrency Geo-Dispatch Engine');
          } else {
            setProjectName('High-Concurrency Order Dispatching Engine');
          }
        }
      } catch (err) {
        console.error("Failed to fetch profile builder prefill details:", err);
        if (careerPlan) {
          setName(careerPlan.name || '');
          setDreamCompany(careerPlan.dream_company || 'Blinkit');
          setTargetRole(careerPlan.target_role || 'Software Development Engineer');
          setSkills(careerPlan.known_skills || []);
        }
      }
    }

    fetchOnboardingDetails();
  }, [sessionId, careerPlan]);

  const handleAddSkill = (e) => {
    e.preventDefault();
    const skill = newSkill.trim();
    if (skill && !skills.includes(skill)) {
      setSkills([...skills, skill]);
      setNewSkill('');
    }
  };

  const handleRemoveSkill = (skillToRemove) => {
    setSkills(skills.filter(s => s !== skillToRemove));
  };

  const handleGenerate = async () => {
    if (!name.trim()) {
      alert("Please enter your name.");
      return;
    }
    if (!projectName.trim()) {
      alert("Please enter a project name.");
      return;
    }

    setLoading(true);
    setLoadingStep(0);
    setError(null);
    setGeneratedData(null);

    const isSkipLlmEnabled = localStorage.getItem('skip_llm') === 'true';

    const payload = {
      name,
      dream_company: dreamCompany,
      target_role: targetRole,
      project_name: projectName,
      skills: skills,
      skip_llm: isSkipLlmEnabled
    };

    try {
      const response = await fetch(`${API_BASE}/api/profile/optimize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const resData = await response.json();
        setGeneratedData(resData);
      } else {
        const errText = await response.text();
        if (errText.includes("429") || errText.includes("quota") || errText.includes("LimitExceeded") || errText.includes("Quota exceeded") || response.status === 500) {
          const runMock = window.confirm("Google Gemini AI API Rate Limit/Quota Exceeded (HTTP 429/500).\n\nWould you like to run in Offline/Simulated AI Mode?");
          if (runMock) {
            const mockResponse = await fetch(`${API_BASE}/api/profile/optimize`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ ...payload, skip_llm: true })
            });
            if (mockResponse.ok) {
              const resData = await mockResponse.json();
              setGeneratedData(resData);
              localStorage.setItem('skip_llm', 'true');
            } else {
              throw new Error("Simulated fallback failed.");
            }
          } else {
            throw new Error("API rate limit exceeded.");
          }
        } else {
          throw new Error("Generation failed.");
        }
      }
    } catch (err) {
      console.error("Profile builder generation error:", err);
      setError(err.message || "Failed to generate optimized SDE profiles. Verify backend server environment configuration.");
    } finally {
      setLoading(false);
    }
  };

  const triggerCopy = (text, key) => {
    navigator.clipboard.writeText(text);
    setCopiedStates(prev => ({ ...prev, [key]: true }));
    setTimeout(() => {
      setCopiedStates(prev => ({ ...prev, [key]: false }));
    }, 2000);
  };

  // Compute simulated ATS score based on skills counts
  const calculateATSScore = () => {
    const base = 55;
    const additional = Math.min(35, skills.length * 4);
    return base + additional;
  };

  const atsScore = calculateATSScore();

  return (
    <div className="profile-builder-page">
      <div className="profile-builder-header">
        <h1>Portfolio Optimizer</h1>
        <p className="subtitle">
          Optimize SDE resume bullet points, professional LinkedIn headlines, and repository README parameters using Google Gemini AI.
        </p>
      </div>

      <div className="profile-builder-layout">
        
        {/* Left Form: Config Panel */}
        <div className="builder-form-card glass-panel">
          <div className="card-header">
            <Cpu size={16} className="header-icon animate-pulse" />
            <h2>AI Optimization Config</h2>
          </div>

          <div className="builder-fields">
            <div className="form-group">
              <label htmlFor="builder-name">Candidate Name</label>
              <input 
                id="builder-name"
                type="text" 
                value={name} 
                onChange={(e) => setName(e.target.value)} 
                placeholder="Rahul Sharma"
              />
            </div>

            <div className="form-row-2">
              <div className="form-group">
                <label htmlFor="builder-company">Target Company</label>
                <input 
                  id="builder-company"
                  type="text" 
                  value={dreamCompany} 
                  onChange={(e) => setDreamCompany(e.target.value)} 
                  placeholder="e.g. Blinkit"
                />
              </div>

              <div className="form-group">
                <label htmlFor="builder-role">Target Role</label>
                <input 
                  id="builder-role"
                  type="text" 
                  value={targetRole} 
                  onChange={(e) => setTargetRole(e.target.value)} 
                  placeholder="e.g. SDE"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="builder-project">Project Showcase</label>
              <input 
                id="builder-project"
                type="text" 
                value={projectName} 
                onChange={(e) => setProjectName(e.target.value)} 
                placeholder="e.g. Geo-caching system"
              />
            </div>

            {/* Skills Tag Input */}
            <div className="form-group">
              <label>Technical Skills taxonomy</label>
              <form onSubmit={handleAddSkill} className="skill-input-row">
                <input 
                  type="text" 
                  value={newSkill} 
                  onChange={(e) => setNewSkill(e.target.value)} 
                  placeholder="Add skill (e.g. Kafka)"
                />
                <button type="submit" className="add-skill-btn">
                  <Plus size={16} />
                </button>
              </form>
              
              <div className="skills-badge-container">
                {skills.length === 0 ? (
                  <p className="no-skills-msg">No SDE skills configured.</p>
                ) : (
                  skills.map((skill, index) => (
                    <span key={index} className="skill-badge">
                      {skill}
                      <button type="button" onClick={() => handleRemoveSkill(skill)} className="remove-badge-btn" style={{ marginLeft: '0.2rem' }}>
                        &times;
                      </button>
                    </span>
                  ))
                )}
              </div>
            </div>

            {/* Simulated ATS Score Gauge */}
            <div className="ats-gauge-container">
              <span className="ats-title">Simulated ATS Match Rate</span>
              <div className="ats-value-row">
                <span className="ats-val">{atsScore}%</span>
                <span className="ats-max">/100</span>
              </div>
              <div className="ats-bar-outer">
                <div className="ats-bar-fill" style={{ width: `${atsScore}%` }} />
              </div>
              <span className="ats-status-msg">
                {atsScore < 70 ? 'Incomplete: Add more core technology keywords to clear corporate SDE scans.' : 'Optimal: Keyword count is highly aligned with selective parameters.'}
              </span>
            </div>

            <button 
              onClick={handleGenerate} 
              disabled={loading}
              className="generate-profiles-btn"
            >
              {loading ? (
                <>
                  <RefreshCw size={16} className="animate-spin" />
                  <span>Synthesizing...</span>
                </>
              ) : (
                <>
                  <Sparkles size={16} />
                  <span>Invoke Gemini Personalizer</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Output Panel */}
        <div className="builder-output-card glass-panel">
          
          {loading && (
            <div className="output-loading-container">
              <div className="pulse-loader">
                <div className="pulse-circle"></div>
                <Sparkles size={24} className="sparkle-icon animate-pulse" />
              </div>
              <div className="loader-step-text">
                <h3>Formulating AI Blueprints</h3>
                <p className="active-step-desc">{loadingSteps[loadingStep]}</p>
              </div>
              <div className="loading-progress-bar">
                <div className="progress-fill" style={{ width: `${((loadingStep + 1) / loadingSteps.length) * 100}%`, transition: 'width 0.5s' }} />
              </div>
            </div>
          )}

          {error && !loading && (
            <div className="output-error-container">
              <AlertCircle size={32} className="error-icon" />
              <h3>AI Generation Blocked</h3>
              <p>{error}</p>
            </div>
          )}

          {!loading && !error && !generatedData && (
            <div className="output-empty-container">
              <Sparkles size={40} className="empty-sparkle-icon" />
              <h3>Awaiting Optimization</h3>
              <p>Configure SDE parameters on the left and invoke the personalizer to generate ATS bullets and summaries.</p>
              <button onClick={handleGenerate} className="empty-state-generate-btn">
                <span>Start Workspace Generation</span>
                <ChevronRight size={14} />
              </button>
            </div>
          )}

          {generatedData && !loading && !error && (
            <div className="output-content-container">
              
              <div className="output-tab-bar">
                <button 
                  className={`tab-btn ${activeTab === 'linkedin' ? 'active' : ''}`}
                  onClick={() => setActiveTab('linkedin')}
                >
                  <Linkedin size={14} />
                  <span>LinkedIn Showcase</span>
                </button>
                <button 
                  className={`tab-btn ${activeTab === 'github' ? 'active' : ''}`}
                  onClick={() => setActiveTab('github')}
                >
                  <Github size={14} />
                  <span>GitHub README</span>
                </button>
                <button 
                  className={`tab-btn ${activeTab === 'resume' ? 'active' : ''}`}
                  onClick={() => setActiveTab('resume')}
                >
                  <FileText size={14} />
                  <span>ATS Resume Bullets</span>
                </button>
              </div>

              <div className="tab-pane-content">
                
                {activeTab === 'linkedin' && (
                  <div className="linkedin-mockup-pane">
                    <div className="linkedin-header-card">
                      <div className="banner-bg"></div>
                      <div className="profile-metadata-row">
                        <div className="mock-avatar">
                          {name ? name.split(' ').map(n=>n[0]).join('').toUpperCase() : 'SDE'}
                        </div>
                        <div className="mock-name-role">
                          <h3 className="mock-name">{name || "Candidate"}</h3>
                          <p className="mock-headline">
                            Aspiring {targetRole} | Specialized in {skills.slice(0, 3).join(', ') || 'Backend engineering'}
                          </p>
                          <p className="mock-subinfo">{dreamCompany} SDE Target &bull; India</p>
                        </div>
                        <button 
                          className={`copy-btn-floating ${copiedStates['li_headline'] ? 'success' : ''}`}
                          onClick={() => triggerCopy(`Aspiring ${targetRole} | Specialized in ${skills.slice(0, 3).join(', ') || 'Backend engineering'}`, 'li_headline')}
                        >
                          {copiedStates['li_headline'] ? <Check size={12} /> : <Copy size={12} />}
                          <span>{copiedStates['li_headline'] ? 'Copied' : 'Copy Headline'}</span>
                        </button>
                      </div>
                    </div>

                    <div className="linkedin-about-card">
                      <div className="about-header">
                        <h4>About Summary</h4>
                        <button 
                          className={`copy-btn-floating ${copiedStates['li_summary'] ? 'success' : ''}`}
                          onClick={() => triggerCopy(generatedData.linkedin_summary, 'li_summary')}
                        >
                          {copiedStates['li_summary'] ? <Check size={12} /> : <Copy size={12} />}
                          <span>{copiedStates['li_summary'] ? 'Copied' : 'Copy Summary'}</span>
                        </button>
                      </div>
                      <p className="about-text">{generatedData.linkedin_summary}</p>
                    </div>
                  </div>
                )}

                {activeTab === 'github' && (
                  <div className="github-readme-pane">
                    <div className="github-sub-actions">
                      <div className="sub-tab-toggles">
                        <button 
                          className={`sub-toggle-btn ${githubMode === 'preview' ? 'active' : ''}`}
                          onClick={() => setGithubMode('preview')}
                        >
                          <Eye size={12} />
                          <span>Preview</span>
                        </button>
                        <button 
                          className={`sub-toggle-btn ${githubMode === 'raw' ? 'active' : ''}`}
                          onClick={() => setGithubMode('raw')}
                        >
                          <CodeIcon size={12} />
                          <span>Raw</span>
                        </button>
                      </div>

                      <button 
                        className={`copy-btn-floating ${copiedStates['gh_readme'] ? 'success' : ''}`}
                        onClick={() => triggerCopy(generatedData.github_readme, 'gh_readme')}
                      >
                        {copiedStates['gh_readme'] ? <Check size={12} /> : <Copy size={12} />}
                        <span>{copiedStates['gh_readme'] ? 'Copied' : 'Copy README'}</span>
                      </button>
                    </div>

                    <div className="github-content-wrapper">
                      {githubMode === 'preview' ? (
                        <div className="readme-markdown-preview">
                          <div className="mock-readme-header">
                            <Github size={14} />
                            <span>README.md</span>
                          </div>
                          <div className="preview-markdown-body">
                            {generatedData.github_readme.split('\n').map((line, idx) => {
                              if (line.startsWith('# ')) {
                                return <h1 key={idx}>{line.substring(2)}</h1>;
                              } else if (line.startsWith('## ')) {
                                return <h2 key={idx}>{line.substring(3)}</h2>;
                              } else if (line.startsWith('### ')) {
                                return <h3 key={idx}>{line.substring(4)}</h3>;
                              } else if (line.startsWith('- ') || line.startsWith('* ')) {
                                return <li key={idx} className="md-bullet">{line.substring(2)}</li>;
                              } else if (line.trim() === '') {
                                return <div key={idx} style={{ height: '0.5rem' }}></div>;
                              } else {
                                return <p key={idx} className="md-para">{line}</p>;
                              }
                            })}
                          </div>
                        </div>
                      ) : (
                        <pre className="readme-raw-code">
                          <code>{generatedData.github_readme}</code>
                        </pre>
                      )}
                    </div>
                  </div>
                )}

                {activeTab === 'resume' && (
                  <div className="resume-bullets-pane">
                    <div className="resume-section-card">
                      <div className="resume-section-header">
                        <div className="resume-headline-title">
                          <h4>SDE Bullet Checklist</h4>
                          <p style={{ color: 'var(--text-muted)', fontSize: '0.78rem', marginTop: '0.15rem' }}>Optimized for ATS scans</p>
                        </div>
                        <button 
                          className={`copy-btn-floating ${copiedStates['resume_bullets'] ? 'success' : ''}`}
                          onClick={() => triggerCopy(generatedData.resume_bullets.join('\n'), 'resume_bullets')}
                        >
                          {copiedStates['resume_bullets'] ? <Check size={12} /> : <Copy size={12} />}
                          <span>{copiedStates['resume_bullets'] ? 'Copied' : 'Copy All'}</span>
                        </button>
                      </div>

                      <div className="resume-bullets-list">
                        {generatedData.resume_bullets.map((bullet, idx) => (
                          <div key={idx} className="resume-bullet-row">
                            <span className="bullet-dot">&bull;</span>
                            <span>{bullet}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

              </div>

            </div>
          )}

        </div>

      </div>
    </div>
  );
}
