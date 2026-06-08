import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp, API_BASE } from '../App';
import { Check, Compass, AlertCircle, Sparkles, Shield, Cpu, RefreshCw, Terminal, Layers, Plus, Clock, Briefcase, Code, FileText, Star, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';
import './ProfileAnalysis.css';

export default function ProfileAnalysis() {
  const { sessionId, updateSession, updateSessionStatus } = useApp();
  const [pipelineStep, setPipelineStep] = useState(0); // 0 to 8
  const [statusText, setStatusText] = useState('Initializing AI Career Compass pipeline...');
  const [analysisResults, setAnalysisResults] = useState(null);
  const [confirmedSkills, setConfirmedSkills] = useState(new Set());
  const [detectedSkills, setDetectedSkills] = useState([]);
  const [customSkill, setCustomSkill] = useState('');
  const [loading, setLoading] = useState(true);
  const [onboardingData, setOnboardingData] = useState(null);
  const navigate = useNavigate();

  const pipeline = [
    { name: 'Resume Parsing', desc: 'Extracting text structure and qualifications from PDF...' },
    { name: 'Skills Extraction', desc: 'Matching skills against standard SDE placement syllabus...' },
    { name: 'GitHub Analysis', desc: 'Analyzing repository commits, counts, and languages...' },
    { name: 'Career Matching', desc: 'Aligning career stage to industry sectors and tiers...' },
    { name: 'Peer Matching', desc: 'Calculating cosine similarity matches against employee profiles...' },
    { name: 'Readiness Calculation', desc: 'Determining gap weights and corporate readiness rating...' },
    { name: 'Roadmap Generation', desc: 'Generating learning stages and hands-on SDE projects...' },
    { name: 'Career Report Generation', desc: 'Compiling circular progress metrics and placement forecasts...' }
  ];

  useEffect(() => {
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
    // Step 0: Resume Parsing
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
      await new Promise(resolve => setTimeout(resolve, 100));
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
    try {
      const response = await fetch(`${API_BASE}/api/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reqBody)
      });
      if (response.ok) {
        responseData = await response.json();
      }
    } catch (err) {
      console.warn("Backend recommendation call offline. Generating mock recommendations:", err);
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
    navigate('/dashboard');
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="analysis-page-container"
    >
      {/* 8-step Pipeline visualization */}
      {loading ? (
        <div className="pipeline-screen glass-panel">
          <div className="pipeline-spinner-wrapper">
            <div className="pipeline-spinner-outer"></div>
            <div className="pipeline-spinner-inner"></div>
          </div>
          <h2 className="pipeline-screen-title">Analyzing Candidate SDE Profile</h2>
          <div className="pipeline-screen-desc">{statusText}</div>

          <div className="pipeline-visual-timeline">
            {pipeline.map((step, idx) => {
              const active = idx === pipelineStep;
              const completed = idx < pipelineStep;
              const statusClass = active ? 'active' : completed ? 'completed' : 'waiting';
              
              return (
                <div key={step.name} className={`pipeline-step-node ${statusClass}`}>
                  <div className="node-indicator">
                    {completed ? <Check size={12} /> : active ? <Cpu size={12} className="animate-pulse" /> : <Clock size={12} />}
                  </div>
                  <div className="node-label">
                    <span className="node-number">0{idx + 1}.</span>
                    <span className="node-name">{step.name}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="results-container-view animate-fade-in">
          <div className="results-header-view">
            <h1>SDE Profile Extraction Complete</h1>
            <p>We've successfully parsed your professional presence. Review details and select your matched placement skills below.</p>
          </div>

          {/* Profile matching grids */}
          <div className="profile-matching-grid">
            {/* LinkedIn Card */}
            <div className="profile-data-card glass-panel">
              <h3 className="data-card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Briefcase size={16} />
                <span>LinkedIn Profile</span>
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
                    <div className="data-row"><span className="lbl">Extracted Skills:</span><span className="val skills-color">{(analysisResults.linkedin_parsed.skills_raw || []).join(', ')}</span></div>
                  </div>
                )
              ) : (
                <div className="no-data-msg">No LinkedIn URL provided.</div>
              )}
            </div>

            {/* GitHub Card */}
            <div className="profile-data-card glass-panel">
              <h3 className="data-card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Code size={16} />
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
                    <div className="data-row"><span className="lbl">Total Stars:</span><span className="val"><Star size={12} style={{ display: 'inline-block', marginRight: '0.25rem', verticalAlign: 'middle' }} /> {analysisResults.github_parsed.stars || 0}</span></div>
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
            </div>

            {/* Resume Card */}
            <div className="profile-data-card glass-panel">
              <h3 className="data-card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <FileText size={16} />
                <span>Resume Details</span>
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
            </div>
          </div>

          {/* Verification section */}
          <div className="verification-card glass-panel">
            <h2>Verify Placement Skills</h2>
            <p className="verification-desc">Toggle the checkboxes to confirm which skills you want to include in your placement readiness calculation. You can also add custom tags.</p>

            <div className="skills-checklist-grid">
              {detectedSkills.map(skill => {
                const isSelected = confirmedSkills.has(skill.name);
                return (
                  <button 
                    key={skill.name}
                    onClick={() => handleToggleSkill(skill.name)}
                    className={`skills-checklist-badge ${isSelected ? 'selected' : 'unselected'}`}
                  >
                    <div className="badge-header-row">
                      <div className="badge-header-left">
                        <div className="checklist-check">
                          {isSelected && <Check size={10} />}
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
                  </button>
                );
              })}
              {detectedSkills.length === 0 && (
                <div className="no-data-msg" style={{ width: '100%', gridColumn: '1 / -1' }}>
                  No skills detected. Add custom skills below.
                </div>
              )}
            </div>

            {/* Add Custom Skill */}
            <div className="add-skill-form">
              <input 
                type="text" 
                placeholder="e.g. NextJS, Redis, SRE..." 
                className="form-input custom-skill-input"
                value={customSkill}
                onChange={e => setCustomSkill(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleAddCustomSkill()}
              />
              <button onClick={handleAddCustomSkill} className="btn-secondary add-skill-btn">
                <Plus size={16} />
                <span>Add Skill</span>
              </button>
            </div>

            <div className="verification-actions">
              <button className="btn-secondary" onClick={() => navigate('/student-form')}>
                Back to Form
              </button>
              <button className="btn-primary" onClick={handleGenerateGuidancePlan}>
                <span>Confirm & Generate SDE Plan</span>
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
}
