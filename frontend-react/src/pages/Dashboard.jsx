import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp, API_BASE } from '../App';
import { BarChart3, Users, Award, Shield, BookOpen, AlertCircle, Compass, CheckCircle, User, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';
import './Dashboard.css';

export default function Dashboard() {
  const { sessionId, careerPlan, setCareerPlan, updateSessionStatus } = useApp();
  const [loading, setLoading] = useState(true);
  const [statsData, setStatsData] = useState(null);
  const [error, setError] = useState(null);
  const [loaderSteps, setLoaderSteps] = useState([
    { label: 'Loading candidate profile', status: 'active' },
    { label: 'Computing readiness score', status: 'pending' },
    { label: 'Matching similar engineers', status: 'pending' },
    { label: 'Analyzing hiring intelligence', status: 'pending' },
    { label: 'Preparing dashboard', status: 'pending' }
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
        const [readinessRes, statsRes] = await Promise.all([
          fetch(`${API_BASE}/api/readiness/${sessionId}`).then(res => res.ok ? res.json() : null),
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
            setError("No active placement session found. Please complete onboarding first.");
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
        updateStep(4, 'active');

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

        updateStep(4, 'completed');
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
        <div className="informative-loader-container glass-panel">
          <div className="loader-header">
            <div className="loader-spinner animate-spin"></div>
            <h3>Preparing Dashboard</h3>
          </div>
          <div className="loader-steps">
            {loaderSteps.map((step, idx) => (
              <div key={idx} className={`loader-step-item ${step.status}`}>
                <span className="step-icon">
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

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.05
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { type: 'spring', stiffness: 100, damping: 16 }
    }
  };

  const plan = careerPlan || {};
  const score = plan.readiness_score || 35;
  const gaps = Array.from(new Set([
    ...(plan.gaps?.high_priority_missing || []),
    ...(plan.gaps?.medium_priority_missing || [])
  ]));

  // AI Coach advice generator
  const getCoachSummary = () => {
    const name = plan.name || "Candidate";
    const company = plan.dream_company || "Blinkit";
    const role = plan.target_role || "SDE-1";
    const g = plan.gaps?.high_priority_missing || [];
    
    if (score < 40) {
      return `Welcome, ${name}! Your profile aligns at ${score}% readiness for ${company}'s ${role} criteria. The similarity engine indicates strong gaps in critical high-throughput SDE skills, specifically ${g.join(', ') || 'distributed systems and message brokers'}. Your immediate focus should be finishing Stage 1 (Core Alignment) and executing the hands-on microservices blueprints.`;
    } else if (score < 70) {
      return `Excellent start, ${name}! You have achieved ${score}% readiness. The vector matcher shows you have aligned key core SDE layers, but you need to refine low-latency data structures and distributed indexing databases to lock down your target at ${company}. Keep practicing real company experiences inside your interview plan.`;
    } else {
      return `Outstanding, ${name}! You are in the top tier with ${score}% placement probability for ${company}'s hiring bar. Most matching engineers transitioned within 3 weeks after executing our mock interviews. Review the last deployment sprint to lock your alignment.`;
    }
  };

  // Extract Career Twin (top matching peer from similar_engineers)
  const peersList = plan.similar_engineers || [];
  const careerTwin = peersList.length > 0 ? peersList[0] : null;
  const otherPeers = peersList.slice(1, 5);

  const maxFreq = statsData?.skills?.[0]?.frequency || 1000;

  return (
    <motion.div 
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="dashboard-wrapper"
    >
      {/* Title */}
      <motion.div className="welcome-banner-row" variants={itemVariants}>
        <h1>Welcome, {plan.name || 'Candidate'}!</h1>
        <p>Here is your SDE placement readiness assessment and corporate alignment metrics.</p>
      </motion.div>

      {/* Row 1: Estimated Timeline & Target Info */}
      <motion.div className="dashboard-metrics-grid" variants={itemVariants}>
        <div className="glass-card metric-item">
          <div className="metric-lbl">Target Company & Role</div>
          <div className="metric-val">{plan.dream_company || 'Blinkit'}</div>
          <div className="metric-sub" style={{ color: 'var(--primary)' }}>{plan.target_role || 'Junior SDE'}</div>
        </div>

        <div className="glass-card metric-item">
          <div className="metric-lbl">Estimated Timeline</div>
          <div className="metric-val">{plan.timeline?.months_remaining || 18} Months</div>
          <div className="metric-sub">{plan.timeline?.weekly_hours_recommended || 25} weekly study hours</div>
        </div>

        <div className="glass-card metric-item">
          <div className="metric-lbl">Target Target Sector</div>
          <div className="metric-val">{plan.dream_sector || 'Quick-Commerce'}</div>
          <div className="metric-sub">Cut-off CGPA: 8.0</div>
        </div>
      </motion.div>

      {/* Row 2: Readiness Score + Coach Summary */}
      <motion.div className="dashboard-row-split-2" variants={itemVariants}>
        {/* Readiness Dial Card */}
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
              <div className="dial-value-text">{score}%</div>
            </div>
            <div className="dial-info-text">
              <h3>Readiness Score</h3>
              <p>Match probability rating computed against SDE developer benchmarks.</p>
            </div>
          </div>
        </div>

        {/* AI Coach Summary Card */}
        <div className="glass-card ai-coach-summary-card">
          <div className="ai-summary-header">
            <Shield className="ai-icon" />
            <h3>Placement Coach Insights</h3>
          </div>
          <p className="ai-summary-text">{getCoachSummary()}</p>
        </div>
      </motion.div>

      {/* Row 3: Career Twin & Top Skill Gaps */}
      <motion.div className="dashboard-row-split-2" variants={itemVariants}>
        {/* Career Twin Profile */}
        <div className="glass-card career-twin-card">
          <h3 className="card-heading-title">
            <Users size={16} />
            <span>Matched Career Twin</span>
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
                <div className="flow-title">Successful Corporate Pathway:</div>
                <div className="flow-nodes">
                  {(careerTwin.career_path || ['Intern', 'SDE-1', 'SDE-2']).map((node, index) => (
                    <React.Fragment key={index}>
                      <span className="flow-node-badge">{node}</span>
                      {index < (careerTwin.career_path || []).length - 1 && (
                        <ArrowRight size={14} style={{ color: 'var(--text-muted)', margin: '0 0.25rem' }} />
                      )}
                    </React.Fragment>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="no-data-msg">No similar peer profile resolved in PostgreSQL.</div>
          )}
        </div>

        {/* Top Skill Gaps Card */}
        <div className="glass-card skill-gaps-card">
          <h3 className="card-heading-title">
            <Award size={16} />
            <span>Top Skill Gaps</span>
          </h3>
          <p className="card-desc-text">Closing these knowledge gaps aligns your profile with the target hiring bar.</p>
          <div className="gaps-badges-list">
            {gaps.length > 0 ? (
              gaps.map(g => <span key={g} className="dashboard-gap-badge">{g}</span>)
            ) : (
              <span className="dashboard-gap-badge success">✓ No Gaps! Ready for target.</span>
            )}
          </div>
        </div>
      </motion.div>

      {/* Navigation CTA banner (Continue Preparation) */}
      <motion.div className="dashboard-cta-banner" variants={itemVariants}>
        <div className="cta-left">
          <h3>Your Placement Plan is Active!</h3>
          <p>Ready to start closing your gaps and practicing interactive mock coding sandboxes?</p>
        </div>
        <button className="cta-nav-button" onClick={() => navigate('/roadmap')}>
          <span>Continue Preparation</span>
          <ArrowRight size={18} />
        </button>
      </motion.div>
    </motion.div>
  );
}
