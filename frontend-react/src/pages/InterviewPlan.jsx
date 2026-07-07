import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp, API_BASE } from '../App';
import { Target, ChevronDown, AlertCircle, ArrowRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './InterviewPlan.css';

export default function InterviewPlan() {
  const { sessionId, careerPlan, updateSessionStatus } = useApp();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({ source: '', questions: [] });
  const [openQuestions, setOpenQuestions] = useState(new Set());
  const [loaderSteps, setLoaderSteps] = useState([
    { label: 'Loading target company selection parameters', status: 'active' },
    { label: 'Formulating selective coding problems', status: 'pending' },
    { label: 'Compiling behavioral checklist modules', status: 'pending' }
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
        const skipLlm = localStorage.getItem('skip_llm') === 'true' ? '?skip_llm=true' : '';
        const response = await fetch(`${API_BASE}/api/interview-plan/${sessionId}${skipLlm}`);
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
        console.warn("Failed to update status on backend", e);
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

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '70vh' }}>
        <div className="informative-loader-container glass-panel animate-fade-in">
          <div className="loader-header">
            <div className="loader-spinner"></div>
            <h3>Formulating Practice Hub</h3>
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

  const company = careerPlan?.dream_company || 'Blinkit';

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.15 }}
      className="interview-plan-wrapper"
    >
      <div className="welcome-banner-row">
        <h1>Practice Hub</h1>
        <p>Master selective coding problems and behavioral scenarios frequently verified in technical interviews at {company}.</p>
      </div>

      <div className="section-header-row">
        <div className="section-header-title">
          <Target size={18} style={{ color: 'var(--accent-primary)' }} />
          <span>Recommended Technical Questions</span>
        </div>
      </div>

      <div className="questions-container">
        {data.questions && data.questions.length > 0 ? (
          data.questions.map((q, idx) => {
            const isOpen = openQuestions.has(idx);
            const diff = q.difficulty || 'Medium';
            const diffClass = `difficulty-${diff.toLowerCase()}`;
            
            return (
              <div 
                key={idx} 
                className="glass-card question-card"
              >
                <div className="question-header">
                  <div className="question-title">{idx + 1}. {q.question}</div>
                  <div className="badges-row">
                    <span className="badge category">{q.category || 'Core'}</span>
                    <span className={`badge ${diffClass}`}>{diff}</span>
                    <span className="badge frequency">{q.frequency || 'Frequent'}</span>
                  </div>
                </div>
                
                <button 
                  className="accordion-trigger" 
                  onClick={() => toggleQuestion(idx)}
                >
                  <span>{isOpen ? 'Hide Solution Blueprint' : 'Explore Solution Blueprint'}</span>
                  <ChevronDown size={14} style={{ transform: isOpen ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
                </button>
 
                {isOpen && (
                  <div className="solution-description">
                    <div style={{ marginBottom: '0.5rem' }}>
                      <strong>Solution Approach:</strong>
                    </div>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: '1.5' }}>
                      {q.solution || 'Focus on system design scaling benchmarks, indexing schema structures, and low latency caching modules.'}
                    </p>
                    <div className="complexity-box">
                      <span>Time Complexity: <strong>O(N)</strong> average</span>
                      <span>Space Complexity: <strong>O(N)</strong> space</span>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        ) : (
          <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
            <AlertCircle size={40} style={{ color: 'var(--text-muted)', marginBottom: '1rem' }} />
            <h3 style={{ fontFamily: 'var(--font-title)', fontSize: '1.25rem', marginBottom: '0.5rem' }}>No Selective Questions Generated</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Verify matching taxonomy skills inside your timeline stages first.</p>
          </div>
        )}
      </div>

      {/* Navigation CTA banner */}
      <div className="dashboard-cta-banner">
        <div className="cta-left">
          <h3>Prep Plan Assembled!</h3>
          <p>Ready to clearing coding sandboxes and take assessment milestones on your visual roadmap?</p>
        </div>
        <button className="cta-nav-button" onClick={() => navigate('/roadmap')}>
          <span>Begin Prep Roadmap</span>
          <ArrowRight size={18} />
        </button>
      </div>
    </motion.div>
  );
}
