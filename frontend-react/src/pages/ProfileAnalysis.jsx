import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp, API_BASE } from '../App';
import { Check, Compass, AlertCircle, Sparkles, Shield, Cpu, RefreshCw, Terminal, Layers, Plus, Clock, Briefcase, Code, FileText, Star, ArrowRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './ProfileAnalysis.css';

export default function ProfileAnalysis() {
  const { sessionId, updateSession, updateSessionStatus } = useApp();
  const [pipelineStep, setPipelineStep] = useState(0); // 0 to 8
  const [statusText, setStatusText] = useState('Initializing AI Career Operating System...');
  const [analysisResults, setAnalysisResults] = useState(null);
  const [confirmedSkills, setConfirmedSkills] = useState(new Set());
  const [detectedSkills, setDetectedSkills] = useState([]);
  const [customSkill, setCustomSkill] = useState('');
  const [loading, setLoading] = useState(true);
  const [onboardingData, setOnboardingData] = useState(null);
  const navigate = useNavigate();
  const hasCalledAnalyze = useRef(false);

  const pipeline = [
    { name: 'Resume Verification', desc: 'Extracting text vectors and qualifications...' },
    { name: 'Taxonomy Matcher', desc: 'Cross-referencing skills against standard SDE database...' },
    { name: 'GitHub Sync', desc: 'Scanning repository insights, commits, and languages...' },
    { name: 'Sector Alignment', desc: 'Evaluating corporate sectors and dream company bar...' },
    { name: 'Career Twin Resolution', desc: 'Calculating cosine similarity twin paths in DB...' },
    { name: 'Readiness Scoring', desc: 'Determining placement preparedness score...' },
    { name: 'Roadmap Generation', desc: 'Compiling curriculum checklist stages...' },
    { name: 'Report Formulation', desc: 'Personalizing placement outcome forecast reports...' }
  ];

  useEffect(() => {
    if (hasCalledAnalyze.current) return;
    hasCalledAnalyze.current = true;

    const dataStr = localStorage.getItem('pending_onboarding');
    if (!dataStr) {
      navigate('/student-form');
      return;
    }
    const parsedData = JSON.parse(dataStr);
    setOnboardingData(parsedData);
    runPipeline(parsedData);
  }, []);

  const runPipeline = async (onboarding) => {
    // Step 0
    setPipelineStep(0);
    setStatusText('Accessing PDF reader bytes stream...');

    let backendResults = null;
    try {
      const response = await fetch(`${API_BASE}/api/student/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(onboarding)
      });
      if (response.ok) {
        backendResults = await response.json();
      }
    } catch (err) {
      console.warn("Backend student analyze error:", err);
    }

    if (!backendResults) {
      alert("Backend analysis failed. Please ensure the FastAPI server and PostgreSQL database are running.");
      navigate('/student-form');
      return;
    }

    // Sequentially step through the 8-step pipeline quickly for user feedback
    for (let i = 0; i < 8; i++) {
      setPipelineStep(i);
      setStatusText(pipeline[i].desc);
      await new Promise(resolve => setTimeout(resolve, 150));
    }

    // Finalize
    setPipelineStep(8);
    setStatusText('Profile successfully parsed and matched!');
    setAnalysisResults(backendResults);
    if (backendResults.session_id) localStorage.setItem('session_id', backendResults.session_id);
    if (backendResults.student_id) localStorage.setItem('student_id', backendResults.student_id);

    const skillsList = backendResults.extracted_skills || [];
    setDetectedSkills(skillsList);
    setConfirmedSkills(new Set(skillsList.map(s => s.name)));
    setLoading(false);
  };

  const handleToggleSkill = (skill) => {
    const updated = new Set(confirmedSkills);
    if (updated.has(skill)) {
      updated.delete(skill);
    } else {
      updated.add(skill);
    }
    setConfirmedSkills(updated);
  };

  const handleAddCustomSkill = () => {
    const skill = customSkill.trim();
    if (skill) {
      const existing = detectedSkills.find(s => s.name.toLowerCase() === skill.toLowerCase());
      if (existing) {
        if (!confirmedSkills.has(existing.name)) {
          const updated = new Set(confirmedSkills);
          updated.add(existing.name);
          setConfirmedSkills(updated);
        }
      } else {
        const newSkillObj = {
          name: skill,
          confidence: 'High',
          confidence_score: 100,
          sources: ['Manual'],
          github_frequency: 0
        };
        setDetectedSkills(prev => [...prev, newSkillObj]);
        const updated = new Set(confirmedSkills);
        updated.add(skill);
        setConfirmedSkills(updated);
      }
      setCustomSkill('');
    }
  };

  const handleGenerateGuidancePlan = async () => {
    const finalSkills = Array.from(confirmedSkills);
    if (finalSkills.length === 0) {
      alert("Please select at least one skill to generate your SDE career roadmap.");
      return;
    }

    setLoading(true);
    setStatusText('Assembling SDE corporate roadmap timeline...');

    const reqBody = {
      name: onboardingData.name,
      qualification: onboardingData.qualification,
      branch: onboardingData.branch,
      cgpa: onboardingData.cgpa,
      dream_company: onboardingData.dream_company,
      dream_sector: onboardingData.dream_sector,
      fresh_passout: onboardingData.fresh_passout,
      target_role: onboardingData.target_role,
      known_skills: finalSkills,
      linkedin_url: onboardingData.linkedin_url,
      github_username: onboardingData.github_username,
      resume_text: onboardingData.resume_text,
      student_id: localStorage.getItem('student_id') ? parseInt(localStorage.getItem('student_id')) : null,
      session_id: localStorage.getItem('session_id') || null
    };

    let responseData = null;
    let fallbackMode = false;
    try {
      const response = await fetch(`${API_BASE}/api/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reqBody)
      });
      if (response.ok) {
        responseData = await response.json();
        localStorage.setItem('skip_llm', 'false');
      } else {
        fallbackMode = true;
      }
    } catch (err) {
      console.warn("Backend recommendation call error. Retrying in offline mode...", err);
      fallbackMode = true;
    }

    if (fallbackMode) {
      try {
        const mockResponse = await fetch(`${API_BASE}/api/recommend`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ...reqBody, skip_llm: true })
        });
        if (mockResponse.ok) {
          responseData = await mockResponse.json();
          localStorage.setItem('skip_llm', 'true');
        }
      } catch (mockErr) {
        console.error("Offline simulated recommendations failed:", mockErr);
      }
    }

    if (!responseData) {
      alert("Failed to generate career guidance plan. Please check backend server and database logs.");
      setLoading(false);
      return;
    }

    // Progress session to 'skills_confirmed' status
    try {
      await fetch(`${API_BASE}/api/session/${responseData.session_id}/progress`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'skills_confirmed' })
      });
    } catch (e) {
      console.warn("Failed to set session progress status:", e);
    }
    
    // Save final details and update context AFTER backend confirmation
    updateSession(responseData.session_id, responseData.student_id, responseData);
    updateSessionStatus('skills_confirmed');
    localStorage.removeItem('pending_onboarding');
    navigate('/');
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.15 }}
      className="analysis-page-container"
    >
      {/* Timeline Steps Pipeline Loader */}
      {loading ? (
        <div className="pipeline-screen glass-panel">
          <div className="pipeline-spinner-wrapper">
            <div className="pipeline-spinner-outer"></div>
            <div className="pipeline-spinner-inner"></div>
          </div>
          <h2 className="pipeline-screen-title">Analyzing SDE Profile</h2>
          <div className="pipeline-screen-desc">{statusText}</div>

          <div className="pipeline-visual-timeline">
            {pipeline.map((step, idx) => {
              const active = idx === pipelineStep;
              const completed = idx < pipelineStep;
              const statusClass = active ? 'active' : completed ? 'completed' : 'waiting';
              
              return (
                <motion.div 
                  key={step.name} 
                  className={`pipeline-step-node ${statusClass}`}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.02, type: 'spring', stiffness: 350 }}
                >
                  <div className="node-indicator">
                    {completed ? <Check size={14} style={{ color: 'var(--success)' }} /> : active ? <Cpu size={14} className="animate-pulse" style={{ color: 'var(--primary)' }} /> : <Clock size={14} />}
                  </div>
                  <div className="node-label">
                    <span className="node-number">0{idx + 1}.</span>
                    <span className="node-name">{step.name}</span>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      ) : (
        /* Results completed verification view */
        <div className="results-container-view animate-fade-in">
          <div className="results-header-view">
            <h1>SDE Workspace Formulated</h1>
            <p>Profile metrics resolved successfully. Verify matched skills to compile your career roadmap plan.</p>
          </div>

          {/* Profile metadata grids */}
          <div className="profile-matching-grid">
            {/* LinkedIn Card */}
            <motion.div 
              className="profile-data-card glass-panel"
              whileHover={{ y: -3 }}
            >
              <h3 className="data-card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Briefcase size={16} style={{ color: 'var(--primary)' }} />
                <span>LinkedIn Credentials</span>
              </h3>
              {analysisResults?.linkedin_parsed && Object.keys(analysisResults.linkedin_parsed).length > 0 ? (
                analysisResults.linkedin_parsed.error ? (
                  <div className="error-card-msg">
                    <AlertCircle size={16} className="error-icon" />
                    <span>{analysisResults.linkedin_parsed.error}</span>
                  </div>
                ) : (
                  <div className="data-card-body">
                    <div className="data-row"><span className="lbl">Headline:</span><span className="val">{analysisResults.linkedin_parsed.headline || 'Aspiring Engineer'}</span></div>
                    <div className="data-row"><span className="lbl">Connections:</span><span className="val">{analysisResults.linkedin_parsed.connections || '100+'}</span></div>
                    <div className="data-row"><span className="lbl">Extracted:</span><span className="val skills-color">{(analysisResults.linkedin_parsed.skills_raw || []).join(', ')}</span></div>
                  </div>
                )
              ) : (
                <div className="no-data-msg">No LinkedIn URL provided.</div>
              )}
            </motion.div>

            {/* GitHub Card */}
            <motion.div 
              className="profile-data-card glass-panel"
              whileHover={{ y: -3 }}
            >
              <h3 className="data-card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Code size={16} style={{ color: 'var(--primary)' }} />
                <span>GitHub Analytics</span>
              </h3>
              {analysisResults?.github_parsed && Object.keys(analysisResults.github_parsed).length > 0 ? (
                analysisResults.github_parsed.error ? (
                  <div className="error-card-msg">
                    <AlertCircle size={16} className="error-icon" />
                    <span>{analysisResults.github_parsed.error}</span>
                  </div>
                ) : (
                  <div className="data-card-body">
                    <div className="data-row"><span className="lbl">Username:</span><span className="val">@{analysisResults.github_parsed.username}</span></div>
                    <div className="data-row"><span className="lbl">Repositories:</span><span className="val">{analysisResults.github_parsed.public_repos !== undefined ? analysisResults.github_parsed.public_repos : (analysisResults.github_parsed.repositories || 0)}</span></div>
                    <div className="data-row"><span className="lbl">Total Stars:</span><span className="val"><Star size={12} style={{ display: 'inline-block', marginRight: '0.25rem', verticalAlign: 'middle', color: 'var(--warning)' }} /> {analysisResults.github_parsed.stars || 0}</span></div>
                    {analysisResults.github_parsed.languages && Object.keys(analysisResults.github_parsed.languages).length > 0 && (
                      <div className="github-lang-breakdown">
                        {Object.entries(analysisResults.github_parsed.languages).map(([lang, pct]) => (
                          <div key={lang} className="lang-bar-container">
                            <div className="lang-bar-info"><span>{lang}</span><span>{pct}%</span></div>
                            <div className="lang-bar-outer"><div className="lang-bar-inner" style={{ width: `${pct}%` }}></div></div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )
              ) : (
                <div className="no-data-msg">No GitHub username provided.</div>
              )}
            </motion.div>

            {/* Resume Card */}
            <motion.div 
              className="profile-data-card glass-panel"
              whileHover={{ y: -3 }}
            >
              <h3 className="data-card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <FileText size={16} style={{ color: 'var(--primary)' }} />
                <span>Resume Extraction</span>
              </h3>
              {analysisResults?.resume_parsed && Object.keys(analysisResults.resume_parsed).length > 0 ? (
                analysisResults.resume_parsed.error ? (
                  <div className="error-card-msg">
                    <AlertCircle size={16} className="error-icon" />
                    <span>{analysisResults.resume_parsed.error}</span>
                  </div>
                ) : (
                  <div className="data-card-body">
                    <div className="data-row"><span className="lbl">Degree:</span><span className="val">{analysisResults.resume_parsed.education || 'B.Tech'}</span></div>
                    <div className="data-row"><span className="lbl">Branch:</span><span className="val">{analysisResults.resume_parsed.branch || 'Computer Science'}</span></div>
                    <div className="data-row"><span className="lbl">CGPA:</span><span className="val">{analysisResults.resume_parsed.cgpa || '8.0'}</span></div>
                    <div className="data-row"><span className="lbl">Keywords Found:</span><span className="val keyword-color">{(analysisResults.resume_parsed.skills_raw || []).join(', ')}</span></div>
                  </div>
                )
              ) : (
                <div className="no-data-msg">No resume uploaded.</div>
              )}
            </motion.div>
          </div>

          {/* Verification checklists */}
          <div className="verification-card glass-panel">
            <h2>Verify Matched Skills</h2>
            <p className="verification-desc">Toggle the cards to include/exclude parsed tags from SDE readiness indexes. You can also append custom skills.</p>

            <div className="skills-checklist-grid">
              {detectedSkills.map((skill, idx) => {
                const isSelected = confirmedSkills.has(skill.name);
                return (
                  <motion.button 
                    key={skill.name}
                    onClick={() => handleToggleSkill(skill.name)}
                    className={`skills-checklist-badge ${isSelected ? 'selected' : 'unselected'}`}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: idx * 0.015, type: 'spring' }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className="badge-header-row">
                      <div className="badge-header-left">
                        <div className="checklist-check">
                          {isSelected && <Check size={12} />}
                        </div>
                        <span className="skill-name">{skill.name}</span>
                      </div>
                      <span className={`confidence-tag ${skill.confidence ? skill.confidence.toLowerCase() : 'high'}`}>
                        {skill.confidence || 'High'}
                      </span>
                    </div>
                    <div className="badge-details-row">
                      <span className="sources-label">
                        Sources: <span className="sources-val">{(skill.sources || []).join(' + ')}</span>
                      </span>
                    </div>
                  </motion.button>
                );
              })}
              {detectedSkills.length === 0 && (
                <div className="no-data-msg" style={{ width: '100%', gridColumn: '1 / -1' }}>
                  No skills matched. Append custom skills below.
                </div>
              )}
            </div>

            {/* Custom skill adder */}
            <div className="add-skill-form">
              <input 
                type="text" 
                className="form-input custom-skill-input" 
                placeholder="Add custom skill (e.g. gRPC, Spark)..."
                value={customSkill}
                onChange={e => setCustomSkill(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleAddCustomSkill()}
              />
              <button type="button" className="btn-secondary add-skill-btn" onClick={handleAddCustomSkill}>
                <Plus size={16} />
                <span>Add Skill</span>
              </button>
            </div>

            {/* Actions row */}
            <div className="verification-actions">
              <button className="btn-secondary" onClick={() => navigate('/student-form')}>
                Back to intake form
              </button>
              <button className="btn-primary" onClick={handleGenerateGuidancePlan}>
                <span>Assemble SDE Operating System</span>
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
}
