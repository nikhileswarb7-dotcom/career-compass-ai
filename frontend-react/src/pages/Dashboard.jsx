import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp, API_BASE } from '../App';
import { BarChart3, Users, Award, Shield, BookOpen, AlertCircle, Compass, CheckCircle, User, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';
import './Dashboard.css';

// Animated counter hook for readiness score
function useAnimatedCounter(target, duration = 400) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    if (target <= 0) return;
    let start = 0;
    const startTime = performance.now();
    function step(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setCount(Math.round(eased * target));
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }, [target, duration]);
  return count;
}

export default function Dashboard() {
  const { sessionId, careerPlan, setCareerPlan, updateSessionStatus } = useApp();
  const plan = careerPlan || {};
  const score = plan.readiness_score || 35;
  const animatedScore = useAnimatedCounter(score);
  const [loading, setLoading] = useState(true);
  const [statsData, setStatsData] = useState(null);
  const [error, setError] = useState(null);
  const [loaderSteps, setLoaderSteps] = useState([
    { label: 'Loading candidate profile indices', status: 'active' },
    { label: 'Computing target readiness rating', status: 'pending' },
    { label: 'Matching successful career twins', status: 'pending' },
    { label: 'Formulating command dashboard', status: 'pending' }
  ]);
  const navigate = useNavigate();

  const updateStep = (index, status) => {
    setLoaderSteps(prev => prev.map((step, idx) => {
      if (idx === index) return { ...step, status };
      if (status === 'active' && idx < index) return { ...step, status: 'completed' };
      if (status === 'completed' && idx <= index) return { ...step, status: 'completed' };
      return step;
    }));
  };

  useEffect(() => {
    if (!sessionId) return;

    async function loadDashboardData() {
      if (careerPlan && statsData) {
        setLoading(false);
      } else {
        setLoading(true);
      }
      setError(null);

      updateStep(0, 'active');
      updateStep(1, 'active');

      try {
        const skipLlm = localStorage.getItem('skip_llm') === 'true' ? '?skip_llm=true' : '';
        const [readinessRes, statsRes] = await Promise.all([
          fetch(`${API_BASE}/api/readiness/${sessionId}${skipLlm}`).then(res => res.ok ? res.json() : null),
          fetch(`${API_BASE}/api/dashboard/stats`).then(res => res.ok ? res.json() : null)
        ]);

        updateStep(0, 'completed');
        updateStep(1, 'completed');
        updateStep(2, 'active');

        let planData = readinessRes;
        if (planData) {
          setCareerPlan(planData);
          localStorage.setItem('career_plan', JSON.stringify(planData));
        }

        if (!planData && !careerPlan) {
          const cached = localStorage.getItem('career_plan');
          if (cached) {
            planData = JSON.parse(cached);
            setCareerPlan(planData);
          } else {
            setError("No active career workspace found. Please configure targets first.");
            setLoading(false);
            return;
          }
        }

        updateStep(2, 'completed');
        updateStep(3, 'active');

        let stats = statsRes;
        if (!stats) {
          stats = {
            source: "Local Database Fallback",
            colleges: [
              { college: "IIT Kharagpur", count: 86 },
              { college: "IIIT Allahabad", count: 72 },
              { college: "NIT Trichy", count: 54 },
              { college: "VIT Vellore", count: 48 },
              { college: "PES University", count: 42 }
            ],
            skills: [
              { skill_name: "Go", frequency: 890 },
              { skill_name: "Java", frequency: 780 },
              { skill_name: "Kafka", frequency: 650 },
              { skill_name: "Redis", frequency: 580 },
              { skill_name: "System Design", frequency: 520 },
              { skill_name: "PostgreSQL", frequency: 490 },
              { skill_name: "Docker", frequency: 420 }
            ]
          };
        }

        setStatsData(stats);
        updateStep(3, 'completed');

        try {
          await fetch(`${API_BASE}/api/session/${sessionId}/progress`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: 'dashboard_unlocked' })
          });
          updateSessionStatus('dashboard_unlocked');
        } catch (e) {
          console.warn("Failed to set dashboard unlocked status:", e);
          updateSessionStatus('dashboard_unlocked');
        }
      } catch (err) {
        console.error("Dashboard fetching error:", err);
        setError("Error loading dashboard data. Server might be offline.");
      } finally {
        setLoading(false);
      }
    }

    loadDashboardData();
  }, [sessionId]);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '70vh' }}>
        <div className="informative-loader-container glass-panel animate-fade-in">
          <div className="loader-header">
            <div className="loader-spinner"></div>
            <h3>Formulating OS Dashboard</h3>
          </div>
          <div className="loader-steps">
            {loaderSteps.map((step, idx) => (
              <div key={idx} className={`loader-step-item ${step.status}`}>
                <span className="step-icon" style={{ marginRight: '0.5rem' }}>
                  {step.status === 'completed' ? '✓' : step.status === 'active' ? '●' : '○'}
                </span>
                <span>{step.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', margin: '2rem auto', maxWidth: '600px' }}>
        <AlertCircle size={40} style={{ color: 'var(--rose)', marginBottom: '1rem' }} />
        <h3 style={{ fontFamily: 'var(--font-title)', fontSize: '1.25rem', marginBottom: '0.5rem' }}>Access Denied</h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>{error}</p>
      </div>
    );
  }

  const gaps = Array.from(new Set([
    ...(plan.gaps?.high_priority_missing || []),
    ...(plan.gaps?.medium_priority_missing || [])
  ]));

  const getCoachSummary = () => {
    const name = plan.name || "Candidate";
    const company = plan.dream_company || "Blinkit";
    const role = plan.target_role || "Software Development Engineer";
    const g = plan.gaps?.high_priority_missing || [];

    if (score < 40) {
      return `Welcome, ${name}! Your profile aligns at ${score}% readiness for ${company}'s SDE criteria. The similarity matching engine indicates strong gaps in critical high-concurrency skills, specifically ${g.join(', ') || 'distributed systems and message brokers'}. Your immediate focus should be finishing Stage 1 (Core Alignment) and executing the SDE learning blueprints.`;
    } else if (score < 70) {
      return `Excellent progress, ${name}! You have achieved ${score}% readiness rating. The database matcher shows you have aligned SDE core layers, but you need to refine low-latency data structures and distributed databases to lock down your target at ${company}. Keep practicing real company experiences inside your practice plan.`;
    } else {
      return `Outstanding, ${name}! You are in the top tier with ${score}% placement probability for ${company}'s hiring bar. Review the latest SDE blueprints to maintain alignment.`;
    }
  };

  const peersList = plan.similar_engineers || [];
  const careerTwin = peersList.length > 0 ? peersList[0] : null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.15 }}
      className="dashboard-wrapper"
    >
      <div className="welcome-banner-row">
        <h1>Workspace Command Center</h1>
        <p>Real-time candidate profile alignment indexes and corporate SDE readiness analytics.</p>
      </div>

      {/* Row 1: Timeline Parameters */}
      <div className="dashboard-metrics-grid">
        <div className="glass-card metric-item">
          <div className="metric-lbl">Target Role & Company</div>
          <div className="metric-val">{plan.dream_company || 'Blinkit'}</div>
          <div className="metric-sub" style={{ color: 'var(--accent-primary)' }}>{plan.target_role || 'Software Development Engineer'}</div>
        </div>

        <div className="glass-card metric-item">
          <div className="metric-lbl">Roadmap Duration</div>
          <div className="metric-val">{plan.timeline?.months_remaining || 18} Months</div>
          <div className="metric-sub">Recommended: {plan.timeline?.weekly_hours_recommended || 25} weekly study hours</div>
        </div>

        <div className="glass-card metric-item">
          <div className="metric-lbl">Sector & Cut-off Target</div>
          <div className="metric-val">{plan.dream_sector || 'Quick-Commerce'}</div>
          <div className="metric-sub">CGPA Threshold: 8.00</div>
        </div>
      </div>

      {/* Row 2: Readiness score & advice */}
      <div className="dashboard-row-split-2">
        <div className="glass-card score-dial-card">
          <div className="dial-container">
            <div className="dial-svg-box">
              <svg width="150" height="150" viewBox="0 0 150 150">
                <circle cx="75" cy="75" r="60" className="dial-bg-circle" />
                <circle
                  cx="75"
                  cy="75"
                  r="60"
                  className="dial-active-circle"
                  style={{ strokeDasharray: 377, strokeDashoffset: 377 - (377 * score) / 100 }}
                />
              </svg>
              <div className="dial-value-text">{animatedScore}%</div>
            </div>
            <div className="dial-info-text">
              <h3>Readiness Score</h3>
              <p>Placement match index computed against hiring bar criteria.</p>
            </div>
          </div>
        </div>

        <div className="glass-card ai-coach-summary-card">
          <div className="ai-summary-header">
            <Shield className="ai-icon" />
            <h3>Placement Advisor Insights</h3>
          </div>
          <p className="ai-summary-text">{getCoachSummary()}</p>
        </div>
      </div>

      {/* Expandable ML Specialization Affinity (Experimental) */}
      {plan.ml_affinity && plan.ml_affinity.supported && (
        <div className="glass-card ml-affinity-card" style={{ marginBottom: '24px', padding: '16px' }}>
          <details style={{ width: '100%' }}>
            <summary style={{ cursor: 'pointer', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-primary)' }}>
              <Shield size={16} style={{ color: 'var(--accent-primary)' }} />
              <span>Data-Driven Profile Signals (Experimental ML)</span>
            </summary>
            <div style={{ marginTop: '16px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              <div className="affinity-item" style={{ padding: '12px', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>General Software Engineering Foundation</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 'bold', marginTop: '4px', color: plan.ml_affinity.general_engineering_score > 0.7 ? '#4caf50' : (plan.ml_affinity.general_engineering_score > 0.4 ? '#ff9800' : '#f44336') }}>
                  {plan.ml_affinity.general_engineering_score > 0.7 ? 'Strong' : (plan.ml_affinity.general_engineering_score > 0.4 ? 'Moderate' : 'Low')}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>Score: {plan.ml_affinity.general_engineering_score.toFixed(4)}</div>
              </div>
              <div className="affinity-item" style={{ padding: '12px', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Backend Specialization Affinity</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 'bold', marginTop: '4px', color: plan.ml_affinity.backend_affinity_score > 0.6 ? '#4caf50' : (plan.ml_affinity.backend_affinity_score > 0.3 ? '#ff9800' : '#f44336') }}>
                  {plan.ml_affinity.backend_affinity_score > 0.6 ? 'High' : (plan.ml_affinity.backend_affinity_score > 0.3 ? 'Moderate' : 'Low')}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>Score: {plan.ml_affinity.backend_affinity_score.toFixed(4)}</div>
              </div>
              <div className="affinity-item" style={{ padding: '12px', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Frontend Specialization Affinity</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 'bold', marginTop: '4px', color: plan.ml_affinity.frontend_affinity_score > 0.6 ? '#4caf50' : (plan.ml_affinity.frontend_affinity_score > 0.3 ? '#ff9800' : '#f44336') }}>
                  {plan.ml_affinity.frontend_affinity_score > 0.6 ? 'High' : (plan.ml_affinity.frontend_affinity_score > 0.3 ? 'Moderate' : 'Low')}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>Score: {plan.ml_affinity.frontend_affinity_score.toFixed(4)}</div>
              </div>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '12px', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '8px' }}>
              Based on patterns learned from versioned professional-profile data (Model: {plan.ml_affinity.model_version}, Dataset Hash: {plan.ml_affinity.dataset_version}).
              Used as experimental supporting evidence alongside skill gaps, hiring evidence, career similarity, and year-aware planning.
            </div>
          </details>
        </div>
      )}

      {/* Row 3: Career twins & weak skills */}
      <div className="dashboard-row-split-2">
        {/* Career Twin Profile */}
        <div className="glass-card career-twin-card">
          <h3 className="card-heading-title">
            <Users size={16} style={{ color: 'var(--accent-primary)' }} />
            <span>Matched SDE Career Twin</span>
          </h3>
          {careerTwin ? (
            <div className="career-twin-body">
              <div className="twin-profile-row">
                <div className="twin-avatar"><User size={18} /></div>
                <div className="twin-meta">
                  <div className="twin-name">{careerTwin.name || 'Aditya Sharma'}</div>
                  <div className="twin-role">{careerTwin.role_name || 'Software Development Engineer'}</div>
                  <div className="twin-match-percentage">{(careerTwin.similarity_score * 100).toFixed(0)}% Similarity Match</div>
                </div>
              </div>
              <div className="twin-career-path-flow">
                <div className="flow-title">Successful Path Flow:</div>
                <div className="flow-nodes">
                  {(() => {
                    const pathNodes = Array.isArray(careerTwin.career_path)
                      ? careerTwin.career_path
                      : (typeof careerTwin.career_path === 'string'
                        ? careerTwin.career_path.split('->').map(s => s.trim()).filter(Boolean)
                        : ['Intern', 'SDE-1', 'SDE-2']);
                    return pathNodes.map((node, index) => (
                      <React.Fragment key={index}>
                        <span className="flow-node-badge">{node}</span>
                        {index < pathNodes.length - 1 && (
                          <span className="flow-arrow">&rarr;</span>
                        )}
                      </React.Fragment>
                    ));
                  })()}
                </div>
              </div>
            </div>
          ) : (
            <div className="no-data-msg">No similar peer profile resolved in database.</div>
          )}
        </div>

        {/* Top Gaps */}
        <div className="glass-card skill-gaps-card">
          <h3 className="card-heading-title">
            <Award size={16} style={{ color: 'var(--accent-secondary)' }} />
            <span>Identified Skill Gaps</span>
          </h3>
          <p className="card-desc-text">Acquiring these key missing skills aligns your profile with the target hiring bar.</p>
          <div className="gaps-badges-list">
            {gaps.length > 0 ? (
              gaps.map(g => <span key={g} className="dashboard-gap-badge">{g}</span>)
            ) : (
              <span className="dashboard-gap-badge success">✓ No skill gaps! Ready for SDE evaluation.</span>
            )}
          </div>
        </div>
      </div>

      {/* Continue CTA */}
      <div className="dashboard-cta-banner">
        <div className="cta-left">
          <h3>Your SDE Workspace is Active!</h3>
          <p>Ready to close your remaining skill gaps and study selective coding blueprints?</p>
        </div>
        <button
          className="cta-nav-button"
          onClick={() => navigate('/roadmap')}
        >
          <span>Continue Journey</span>
          <ArrowRight size={18} />
        </button>
      </div>
    </motion.div>
  );
}
