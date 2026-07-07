import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp, API_BASE } from '../App';
import { Lightbulb, BookOpen, Layers, ExternalLink, Shield, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';
import './Recommendations.css';

export default function Recommendations() {
  const { sessionId, careerPlan, updateSessionStatus } = useApp();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({ source: '', projects: [], resources: [] });
  const [loaderSteps, setLoaderSteps] = useState([
    { label: 'Loading verified skill gaps', status: 'active' },
    { label: 'Fetching recommended microservices blueprints', status: 'pending' },
    { label: 'Gathering target learning platform resources', status: 'pending' }
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

    async function loadRecommendations() {
      if (data.projects && data.projects.length > 0) {
        setLoading(false);
      } else {
        setLoading(true);
      }
      
      updateStep(0, 'active');

      let cachedPlan = null;
      const planStr = localStorage.getItem('career_plan');
      if (planStr) {
        try {
          cachedPlan = JSON.parse(planStr);
        } catch (e) {}
      }

      let recs = {
        source: 'Local Cache Fallback',
        projects: cachedPlan?.projects || [],
        resources: cachedPlan?.resources || []
      };

      try {
        const skipLlm = localStorage.getItem('skip_llm') === 'true' ? '?skip_llm=true' : '';
        const response = await fetch(`${API_BASE}/api/recommendations/${sessionId}${skipLlm}`);
        updateStep(0, 'completed');
        updateStep(1, 'active');
        if (response.ok) {
          const apiData = await response.json();
          recs = {
            source: 'PostgreSQL Database',
            projects: apiData.projects,
            resources: apiData.resources
          };
        }
        updateStep(1, 'completed');
        updateStep(2, 'active');
      } catch (err) {
        console.warn("Recommendations API offline. Using fallbacks.", err);
        updateStep(0, 'completed');
        updateStep(1, 'completed');
        updateStep(2, 'active');
      }

      setData(recs);

      try {
        await fetch(`${API_BASE}/api/session/${sessionId}/progress`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'recommendations_completed' })
        });
        updateSessionStatus('recommendations_completed');
      } catch (e) {
        console.warn("Failed to set progress status", e);
        updateSessionStatus('recommendations_completed');
      }

      updateStep(2, 'completed');
      setLoading(false);
    }

    loadRecommendations();
  }, [sessionId]);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.02,
        delayChildren: 0.01
      }
    }
  };

  const itemVariants = {
    hidden: { y: 25, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { type: 'spring', stiffness: 350, damping: 25 }
    }
  };

  const cardVariants = {
    hidden: { y: 20, opacity: 0, scale: 0.97 },
    visible: (i) => ({
      y: 0,
      opacity: 1,
      scale: 1,
      transition: { delay: i * 0.02, type: 'spring', stiffness: 350, damping: 25 }
    })
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '70vh' }}>
        <div className="informative-loader-container glass-panel">
          <div className="loader-header">
            <div className="loader-spinner animate-spin"></div>
            <h3>Generating SDE Blueprints</h3>
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

  return (
    <motion.div 
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="recommendations-wrapper"
    >
      <motion.div className="welcome-banner-row" variants={itemVariants}>
        <h1>Custom SDE Recommendations</h1>
        <p>Curated hands-on microservices projects and target resources addressing your core missing preparation gaps.</p>
      </motion.div>

      {/* Row 1: Recommended Projects */}
      <motion.div className="section-header-row" variants={itemVariants}>
        <div className="section-header-title">
          <Layers size={18} />
          <span>Recommended SDE Projects</span>
        </div>
      </motion.div>

      <motion.div className="recommendations-projects-grid" variants={itemVariants}>
        {data.projects && data.projects.length > 0 ? (
          data.projects.map((p, idx) => {
            const isAdv = (p.difficulty || 'Advanced').toLowerCase() === 'advanced';
            return (
              <motion.div 
                key={idx} 
                className="glass-card project-recommend-card"
                custom={idx}
                variants={cardVariants}
                initial="hidden"
                animate="visible"
                whileHover={{ y: -4, transition: { duration: 0.1 } }}
              >
                <div className="project-header-meta">
                  <h4 className="project-card-title">{p.name}</h4>
                  <span className={`badge-pill ${isAdv ? 'adv' : 'int'}`}>
                    {p.difficulty || 'Advanced'}
                  </span>
                </div>
                <p className="project-card-desc">{p.details}</p>
                <div className="project-blueprint-box">
                  <div className="blueprint-title" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <Lightbulb size={14} />
                    <span>Core Architecture Blueprint</span>
                  </div>
                  <p className="blueprint-desc">
                    Designed to resolve matching gaps. Scaled to handle high concurrency using thread worker pools, relational index normalization, and caching.
                  </p>
                </div>
              </motion.div>
            );
          })
        ) : (
          <div className="no-data-card glass-card">
            No custom project blueprints generated. Master your active timeline stages!
          </div>
        )}
      </motion.div>

      {/* Row 2: Learning Resources */}
      <motion.div className="section-header-row" style={{ marginTop: '2rem' }} variants={itemVariants}>
        <div className="section-header-title">
          <BookOpen size={18} />
          <span>Learning & Prep Resources</span>
        </div>
      </motion.div>

      <motion.div className="recommendations-resources-grid" variants={itemVariants}>
        {data.resources && data.resources.length > 0 ? (
          data.resources.map((r, idx) => (
            <motion.div 
              key={idx} 
              className="glass-card resource-recommend-card"
              custom={idx}
              variants={cardVariants}
              initial="hidden"
              animate="visible"
              whileHover={{ y: -4, transition: { duration: 0.1 } }}
            >
              <div className="resource-meta-info">
                <h4 className="resource-title-text" title={r.title}>{r.title}</h4>
                <div className="resource-badges-row">
                  <span className="platform-tag">{r.platform || 'Platform'}</span>
                  <span className="type-tag">{r.type || 'SDE Prep'}</span>
                </div>
              </div>
              <a 
                href={r.url || '#'} 
                target="_blank" 
                rel="noreferrer" 
                className="btn-primary resource-action-link"
              >
                <span>Study</span>
                <ExternalLink size={12} />
              </a>
            </motion.div>
          ))
        ) : (
          <div className="no-data-card glass-card">
            No learning links recommended. Review active concepts inside the player.
          </div>
        )}
      </motion.div>

      {/* Navigation CTA banner */}
      <motion.div className="dashboard-cta-banner" variants={itemVariants}>
        <div className="cta-left">
          <h3>Step 2 Completed: Blueprints Unlocked!</h3>
          <p>Your recommendations are loaded. Ready to review your customized SDE interview training checklist?</p>
        </div>
        <button className="cta-nav-button" onClick={() => navigate('/interview-plan')}>
          <span>Proceed to Interview Plan</span>
          <ArrowRight size={18} />
        </button>
      </motion.div>
    </motion.div>
  );
}
