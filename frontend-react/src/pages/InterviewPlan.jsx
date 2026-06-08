import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp, API_BASE } from '../App';
import { Target, ChevronDown, AlertCircle, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';
import './InterviewPlan.css';

export default function InterviewPlan() {
  const { sessionId, careerPlan, updateSessionStatus } = useApp();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({ source: '', questions: [] });
  const [openQuestions, setOpenQuestions] = useState(new Set());
  const [loaderSteps, setLoaderSteps] = useState([
    { label: 'Loading company selective bars', status: 'active' },
    { label: 'Selecting coding questions', status: 'pending' },
    { label: 'Generating behavioral guidance', status: 'pending' }
  ]);
  const [error, setError] = useState(null);
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

    async function loadInterviewPlan() {
      if (data.questions && data.questions.length > 0) {
        setLoading(false);
      } else {
        setLoading(true);
      }
      setError(null);
      
      updateStep(0, 'active');

      let cachedPlan = null;
      const planStr = localStorage.getItem('career_plan');
      if (planStr) {
        try {
          cachedPlan = JSON.parse(planStr);
        } catch (e) {
          console.error("Failed to parse cached plan", e);
        }
      }

      let planData = {
        source: 'Local Cache Fallback',
        questions: cachedPlan?.recommended_questions || []
      };

      try {
        const response = await fetch(`${API_BASE}/api/interview-plan/${sessionId}`);
        updateStep(0, 'completed');
        updateStep(1, 'active');
        if (response.ok) {
          const apiData = await response.json();
          planData = {
            source: 'PostgreSQL Database',
            questions: apiData.recommended_questions || []
          };
        }
        updateStep(1, 'completed');
        updateStep(2, 'active');
      } catch (err) {
        console.warn("Interview Plan API offline. Using fallbacks.", err);
        updateStep(0, 'completed');
        updateStep(1, 'completed');
        updateStep(2, 'active');
      }

      setData(planData);

      try {
        await fetch(`${API_BASE}/api/session/${sessionId}/progress`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'interview_completed' })
        });
        updateSessionStatus('interview_completed');
      } catch (e) {
        console.warn("Failed to update gating status on backend", e);
        updateSessionStatus('interview_completed');
      }

      updateStep(2, 'completed');
      setLoading(false);
    }

    loadInterviewPlan();
  }, [sessionId, updateSessionStatus]);

  const toggleQuestion = (idx) => {
    const next = new Set(openQuestions);
    if (next.has(idx)) {
      next.delete(idx);
    } else {
      next.add(idx);
    }
    setOpenQuestions(next);
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08,
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

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '70vh' }}>
        <div className="informative-loader-container glass-panel">
          <div className="loader-header">
            <div className="loader-spinner animate-spin"></div>
            <h3>Generating Interview Guidance</h3>
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

  const company = careerPlan?.dream_company || 'Blinkit';

  return (
    <motion.div 
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="interview-plan-wrapper"
    >
      <motion.div className="welcome-banner-row" variants={itemVariants}>
        <h1>Personalized Interview Plan</h1>
        <p>Master real-world engineering concepts frequently tested in technical rounds at {company}.</p>
      </motion.div>

      <motion.div className="section-header-row" variants={itemVariants}>
        <div className="section-header-title">
          <Target size={18} />
          <span>Recommended Technical Questions</span>
        </div>
      </motion.div>

      <motion.div className="questions-container" variants={itemVariants}>
        {data.questions && data.questions.length > 0 ? (
          data.questions.map((q, idx) => {
            const isOpen = openQuestions.has(idx);
            const diff = q.difficulty || 'Medium';
            const diffClass = `difficulty-${diff.toLowerCase()}`;
            
            return (
              <div key={idx} className={`glass-card question-card ${isOpen ? 'open' : ''}`}>
                <div className="question-header">
                  <div className="question-title">{idx + 1}. {q.question}</div>
                  <div className="badges-row">
                    <span className="badge category">{q.category || 'Core'}</span>
                    <span className={`badge ${diffClass}`}>{diff}</span>
                    <span className="badge frequency">{q.frequency || 'Frequent'}</span>
                  </div>
                </div>
                
                <button className="accordion-trigger" onClick={() => toggleQuestion(idx)}>
                  <span>{isOpen ? 'Hide Solution Blueprint' : 'View Solution Blueprint'}</span>
                  <ChevronDown className="accordion-arrow" size={16} />
                </button>
 
                <div className="accordion-content">
                  <div className="solution-description">
                    <div style={{ marginBottom: '0.5rem' }}>
                      <strong>Solution Approach:</strong>
                    </div>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: '1.5' }}>
                      {q.solution || 'Study concepts related to system architecture, low-latency queues and indexing.'}
                    </p>
                    <div className="complexity-box">
                      <span><strong>Time Complexity:</strong> O(N) average</span>
                      <span><strong>Space Complexity:</strong> O(N) space</span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        ) : (
          <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
            <AlertCircle size={40} style={{ color: 'var(--text-muted)', marginBottom: '1rem' }} />
            <h3 style={{ fontFamily: 'var(--font-title)', fontSize: '1.25rem', marginBottom: '0.5rem' }}>No Custom Questions Prepared</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Practice core skills listed in your timeline stages.</p>
          </div>
        )}
      </motion.div>

      {/* Navigation CTA banner */}
      <motion.div className="dashboard-cta-banner" variants={itemVariants}>
        <div className="cta-left">
          <h3>Step 3 Completed: Prep Plan Ready!</h3>
          <p>Your technical questions are reviewed. Ready to begin your interactive coding sandbox and training curriculum?</p>
        </div>
        <button className="cta-nav-button" onClick={() => navigate('/roadmap')}>
          <span>Proceed to Prep Roadmap</span>
          <ArrowRight size={18} />
        </button>
      </motion.div>
    </motion.div>
  );
}
