import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp, API_BASE } from '../App';
import { 
  Sun, 
  Moon, 
  Sparkles, 
  Compass, 
  TrendingUp, 
  ArrowRight,
  Shield,
  Activity,
  CheckCircle,
  Circle,
  Play,
  Flame,
  Target,
  FileText
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './Welcome.css';

// Hook to count up readiness score
function useAnimatedCounter(target, duration = 400) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    if (!target || target <= 0) return;
    let start = 0;
    const startTime = performance.now();
    function step(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setCount(Math.round(eased * target));
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }, [target, duration]);
  return count;
}

export default function Welcome() {
  const { theme, sessionId, sessionStatus, careerPlan, setCareerPlan, updateSession, updateSessionStatus, toggleTheme, logout } = useApp();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [workspaceReady, setWorkspaceReady] = useState(false);
  const [readinessScore, setReadinessScore] = useState(0);
  const [targetCompany, setTargetCompany] = useState('');
  const [targetRole, setTargetRole] = useState('');
  const [timeline, setTimeline] = useState('');
  const [currentStage, setCurrentStage] = useState('');
  
  // Weekly goals states
  const [goals, setGoals] = useState([
    { id: 1, text: "Review active microservices blueprints", completed: false },
    { id: 2, text: "Close priority missing backend index gaps", completed: false },
    { id: 3, text: "Complete Sandbox coding challenge", completed: false }
  ]);

  const animatedScore = useAnimatedCounter(readinessScore);

  useEffect(() => {
    async function loadWorkspace() {
      if (!sessionId) {
        setLoading(false);
        setWorkspaceReady(false);
        return;
      }

      try {
        const skipLlm = localStorage.getItem('skip_llm') === 'true' ? '?skip_llm=true' : '';
        const response = await fetch(`${API_BASE}/api/readiness/${sessionId}${skipLlm}`);
        if (response.ok) {
          const apiData = await response.json();
          setCareerPlan(apiData);
          localStorage.setItem('career_plan', JSON.stringify(apiData));
          
          setReadinessScore(apiData.readiness_score || 35);
          setTargetCompany(apiData.dream_company || 'Blinkit');
          setTargetRole(apiData.target_role || 'Software Development Engineer');
          
          const stages = apiData.timeline?.stages || [];
          const currentStageIdx = parseInt(localStorage.getItem('roadmap_current_stage') || '0');
          const activeStage = stages[currentStageIdx]?.title || 'Core Alignment';
          setCurrentStage(activeStage);
          
          setTimeline(`${apiData.timeline?.months_remaining || 18} Months remaining`);
          setWorkspaceReady(true);
        } else {
          // fallback
          loadFallback();
        }
      } catch (err) {
        console.warn("Workspace API error. Using local caching.", err);
        loadFallback();
      } finally {
        setLoading(false);
      }
    }

    function loadFallback() {
      const cached = localStorage.getItem('career_plan');
      if (cached) {
        try {
          const apiData = JSON.parse(cached);
          setReadinessScore(apiData.readiness_score || 35);
          setTargetCompany(apiData.dream_company || 'Blinkit');
          setTargetRole(apiData.target_role || 'Software Development Engineer');
          
          const stages = apiData.timeline?.stages || [];
          const currentStageIdx = parseInt(localStorage.getItem('roadmap_current_stage') || '0');
          const activeStage = stages[currentStageIdx]?.title || 'Core Alignment';
          setCurrentStage(activeStage);
          
          setTimeline(`${apiData.timeline?.months_remaining || 18} Months remaining`);
          setWorkspaceReady(true);
        } catch (e) {
          setWorkspaceReady(false);
        }
      } else {
        setWorkspaceReady(false);
      }
    }

    loadWorkspace();
  }, [sessionId, setCareerPlan]);

  const handleStartNew = () => {
    const loggedInUser = localStorage.getItem('logged_in_user');
    const users = localStorage.getItem('registered_users');
    const activeTheme = localStorage.getItem('theme');
    localStorage.clear();

    if (loggedInUser) localStorage.setItem('logged_in_user', loggedInUser);
    if (users) localStorage.setItem('registered_users', users);
    if (activeTheme) localStorage.setItem('theme', activeTheme);

    navigate('/student-form');
  };

  const handleContinue = () => {
    const status = sessionStatus;
    if (status === 'registered') {
      navigate('/student-form');
    } else if (status === 'analyzed') {
      navigate('/profile-analysis');
    } else {
      navigate('/dashboard');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const toggleGoal = (id) => {
    setGoals(prev => prev.map(g => g.id === id ? { ...g, completed: !g.completed } : g));
  };

  // Get Next Action based on session status
  const getNextActionDetails = () => {
    const status = sessionStatus;
    if (status === 'registered') {
      return {
        tag: "Intake Form",
        title: "Setup Career Targets",
        desc: "Define your dream role and target SDE companies to formulate your workspace profile.",
        actionLabel: "Configure Goals",
        path: "/student-form"
      };
    } else if (status === 'analyzed') {
      return {
        tag: "Skill Mapping",
        title: "Verify Matched Skills",
        desc: "Review your parsed GitHub, resume, and LinkedIn skills to establish a baseline.",
        actionLabel: "Verify Skills",
        path: "/profile-analysis"
      };
    } else if (status === 'skills_confirmed' || status === 'dashboard_unlocked') {
      return {
        tag: "Blueprint Analysis",
        title: "Unlock Recommended Blueprints",
        desc: "Your skill gaps have been identified. Review your tailored SDE code projects.",
        actionLabel: "View Blueprints",
        path: "/dashboard" // Dashboard redirects appropriately
      };
    } else if (status === 'recommendations_completed') {
      return {
        tag: "Interview Prep",
        title: "Explore Selective Problems",
        desc: "Master specific questions targeted towards SDE placement rounds at " + targetCompany + ".",
        actionLabel: "Start Practicing",
        path: "/interview-plan"
      };
    } else if (status === 'interview_completed') {
      return {
        tag: "Curriculum Progression",
        title: "Execute Roadmap Milestone",
        desc: "Begin your customized interactive training stages (Overview, Sandbox, Assessments).",
        actionLabel: "Open Roadmap",
        path: "/roadmap"
      };
    } else {
      return {
        tag: "Portfolio Generation",
        title: "personalize ATS Profile",
        desc: "Generate quantitative SDE bullets, summaries, and GitHub readmes via Google Gemini.",
        actionLabel: "Build Portfolio",
        path: "/profile-builder"
      };
    }
  };

  const nextAction = getNextActionDetails();

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100vh', gap: '1rem', background: 'var(--bg-main)' }}>
        <div className="loader-spinner animate-spin" style={{ width: '36px', height: '36px', borderWidth: '3px' }}></div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', fontFamily: 'var(--font-title)', fontWeight: 650 }}>Synchronizing AI Career Operating System...</p>
      </div>
    );
  }

  return (
    <div className="welcome-container">
      <motion.button 
        onClick={toggleTheme} 
        className="theme-toggle-welcome" 
        aria-label="Toggle Theme"
        whileHover={{ scale: 1.1, rotate: 10 }}
        whileTap={{ scale: 0.95 }}
      >
        {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
      </motion.button>

      <motion.button 
        onClick={handleLogout} 
        className="logout-welcome-btn"
        whileHover={{ scale: 1.03 }}
        whileTap={{ scale: 0.97 }}
      >
        Sign Out
      </motion.button>

      {workspaceReady ? (
        /* Workspace Command Center view */
        <motion.div 
          className="workspace-wrapper animate-fade-in"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.2 }}
        >
          {/* Header row */}
          <div className="workspace-greeting">
            <motion.h1 
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05, type: 'spring', stiffness: 350, damping: 25 }}
            >
              My SDE Workspace
            </motion.h1>
            <p>Your AI Career Operating System command center.</p>
          </div>

          {/* Top Cards Row */}
          <div className="workspace-grid-3">
            {/* Target Profile Card */}
            <motion.div 
              className="glass-card target-info-card"
              whileHover={{ y: -3 }}
            >
              <div>
                <div className="target-lbl">Target Target</div>
                <div className="target-company">{targetCompany}</div>
                <div className="target-role-badge">{targetRole}</div>
              </div>
              <div className="target-timeline">{timeline} • Stage: {currentStage}</div>
            </motion.div>

            {/* Score Ring Card */}
            <motion.div 
              className="glass-card score-dial-card"
              whileHover={{ y: -3 }}
            >
              <div className="dial-container">
                <div className="dial-svg-box">
                  <svg width="110" height="110" viewBox="0 0 150 150">
                    <circle cx="75" cy="75" r="60" className="dial-bg-circle" />
                    <circle 
                      cx="75" 
                      cy="75" 
                      r="60" 
                      className="dial-active-circle" 
                      style={{ strokeDasharray: 377, strokeDashoffset: 377 - (377 * readinessScore) / 100 }}
                    />
                  </svg>
                  <div className="dial-value-text">{animatedScore}%</div>
                </div>
                <div className="dial-info-text">
                  <h3>Readiness Rating</h3>
                  <p>Matching index computed against target hiring bar criteria.</p>
                </div>
              </div>
            </motion.div>

            {/* Mission Card (Next Best Action) */}
            <motion.div 
              className="glass-card mission-card"
              whileHover={{ y: -3 }}
            >
              <div className="mission-header">
                <span className="mission-tag">{nextAction.tag}</span>
                <Flame size={18} style={{ color: 'var(--amber)' }} />
              </div>
              <div>
                <h4 className="mission-title">{nextAction.title}</h4>
                <p className="mission-desc">{nextAction.desc}</p>
              </div>
              <div className="mission-action-row">
                <button 
                  className="btn-primary btn-continue-workspace"
                  onClick={() => navigate(nextAction.path)}
                >
                  <span>{nextAction.actionLabel}</span>
                  <ArrowRight size={16} />
                </button>
              </div>
            </motion.div>
          </div>

          {/* Details Row */}
          <div className="workspace-row-split-2">
            {/* Weekly Tasks list */}
            <div className="glass-card workspace-list-card">
              <h3 className="card-heading-title weekly">
                <Target size={18} style={{ color: 'var(--accent-primary)' }} />
                <span>Active Missions Checklist</span>
              </h3>
              <div className="goals-list">
                {goals.map(g => (
                  <div 
                    key={g.id} 
                    className="goal-item-row"
                    onClick={() => toggleGoal(g.id)}
                  >
                    <span className={`goal-checkbox ${g.completed ? 'completed' : ''}`}>
                      {g.completed ? <CheckCircle size={18} /> : <Circle size={18} />}
                    </span>
                    <span className={`goal-text ${g.completed ? 'completed' : ''}`}>{g.text}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* AI Advisor Recommendations */}
            <div className="glass-card workspace-list-card">
              <h3 className="card-heading-title ai-rec">
                <Sparkles size={18} style={{ color: 'var(--accent-secondary)' }} />
                <span>AI Mentor Recommendations</span>
              </h3>
              <div className="rec-items-list">
                {careerPlan?.projects && careerPlan.projects.slice(0, 2).map((p, idx) => (
                  <div key={idx} className="rec-item-pill" onClick={() => navigate('/roadmap')}>
                    <span className="rec-item-title">{p.name || p.title}</span>
                    <span className="rec-item-desc">{p.details?.substring(0, 100)}...</span>
                  </div>
                ))}
                {(!careerPlan?.projects || careerPlan.projects.length === 0) && (
                  <div className="rec-item-pill">
                    <span className="rec-item-title">Setup Career Roadmap</span>
                    <span className="rec-item-desc">Confirm your skills checklist to load specialized code blueprint recommendations.</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Action Footer */}
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
            <button className="btn-secondary" onClick={handleStartNew}>Reset Workspace Session</button>
            <button className="btn-primary" onClick={handleContinue}>Resume Training Flow</button>
          </div>

        </motion.div>
      ) : (
        /* Original Splash page style modified to look ultra-premium */
        <motion.div 
          className="welcome-card glass-panel"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
        >
          <div className="welcome-brand">
            <Compass className="welcome-logo-icon animate-pulse-glow" />
            <span>CareerCompass AI</span>
          </div>
          
          <p className="welcome-tagline">
            SDE Career Guidance Operating System. Formulate targeted learning roadmaps, optimize technical portfolios, and simulate ATS evaluation systems.
          </p>

          <div className="welcome-grid">
            <button 
              onClick={handleStartNew} 
              className="welcome-btn-card"
            >
              <div className="welcome-btn-title start-new">
                <Sparkles size={18} />
                <span>Launch Workspace</span>
              </div>
              <div className="welcome-btn-desc">
                Initiate onboarding sequence, upload PDF resume, and evaluate target selective bar alignments.
              </div>
            </button>

            <button 
              onClick={handleContinue} 
              className="welcome-btn-card"
            >
              <div className="welcome-btn-title continue">
                <Compass size={18} />
                <span>Resume Session</span>
              </div>
              <div className="welcome-btn-desc">
                Restore existing candidate profile workspace parameters and return to your active learning stage.
              </div>
            </button>

            <button 
              onClick={() => navigate('/analytics')} 
              className="welcome-btn-card"
            >
              <div className="welcome-btn-title analytics">
                <TrendingUp size={18} />
                <span>Macro Analytics</span>
              </div>
              <div className="welcome-btn-desc">
                Evaluate industry-wide developer placements data, salary structures, and tech taxonomy maps.
              </div>
            </button>
          </div>
        </motion.div>
      )}
    </div>
  );
}
