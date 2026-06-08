import React, { useState, useEffect } from 'react';
import { useApp, API_BASE } from '../App';
import { motion } from 'framer-motion';
import { 
  Award, 
  Users, 
  Map, 
  FileText, 
  AlertCircle, 
  Compass, 
  TrendingUp, 
  Cpu, 
  Zap, 
  ShieldCheck,
  Check,
  Save,
  Target,
  Lightbulb
} from 'lucide-react';
import './CareerReport.css';

export default function CareerReport() {
  const { sessionId, studentId, careerPlan, updateSessionStatus } = useApp();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Data states
  const [readinessData, setReadinessData] = useState(null);
  const [recsData, setRecsData] = useState(null);
  const [outcomeData, setOutcomeData] = useState(null);

  // Feedback note state
  const [feedbackNotes, setFeedbackNotes] = useState('');
  const [savingFeedback, setSavingFeedback] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (!sessionId) return;

    async function loadReportData() {
      setLoading(true);
      setError(null);

      // 1. Fetch readiness details
      let readData = null;
      try {
        const res = await fetch(`${API_BASE}/api/readiness/${sessionId}`);
        if (res.ok) {
          readData = await res.json();
          setReadinessData(readData);
        }
      } catch (err) {
        console.error("Failed to fetch readiness data:", err);
      }

      // If no API data, fallback to careerPlan or show error
      if (!readData) {
        const cached = localStorage.getItem('career_plan');
        if (cached) {
          readData = JSON.parse(cached);
          setReadinessData(readData);
        } else {
          setError("Failed to retrieve SDE Placement Report data from the backend. Please ensure the API services are active.");
          setLoading(false);
          return;
        }
      }

      // 2. Fetch recommendations
      try {
        const res = await fetch(`${API_BASE}/api/recommendations/${sessionId}`);
        if (res.ok) {
          const rData = await res.json();
          setRecsData(rData);
        }
      } catch (err) {
        console.error("Failed to fetch recommendations:", err);
      }

      // 3. Fetch placement outcomes from student_outcomes table (if studentId exists)
      const currentStudentId = studentId || readData?.student_id;
      if (currentStudentId) {
        try {
          const res = await fetch(`${API_BASE}/api/student/${currentStudentId}/outcome`);
          if (res.ok) {
            const outData = await res.json();
            setOutcomeData(outData);
            setFeedbackNotes(outData.feedback_notes || '');
          }
        } catch (err) {
          console.error("Failed to fetch placement outcome:", err);
        }
      }

      try {
        await fetch(`${API_BASE}/api/session/${sessionId}/progress`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'career_report_completed' })
        });
        updateSessionStatus('career_report_completed');
      } catch (e) {
        console.warn("Failed to set career report completed progress status:", e);
      } finally {
        setLoading(false);
      }
    }

    loadReportData();
  }, [sessionId, studentId, updateSessionStatus]);

  // Handle saving feedback to database
  const handleSaveFeedback = async () => {
    const currentStudentId = studentId || readinessData?.student_id;
    if (!currentStudentId) return;

    setSavingFeedback(true);
    setSaveSuccess(false);

    try {
      const response = await fetch(`${API_BASE}/api/student/${currentStudentId}/outcome/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feedback_notes: feedbackNotes })
      });

      if (response.ok) {
        setSaveSuccess(true);
        setTimeout(() => setSaveSuccess(false), 3000);
      }
    } catch (err) {
      console.error("Failed to save outcome feedback:", err);
    } finally {
      setSavingFeedback(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '60vh', gap: '1rem' }}>
        <div className="animate-spin" style={{ width: '40px', height: '40px', border: '3px solid var(--border-glass)', borderTop: '3px solid var(--primary)', borderRadius: '50%' }}></div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', fontFamily: 'var(--font-title)' }}>Assembling circular metrics and placement forecast reports...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '60vh', gap: '1rem', padding: '2rem', textAlign: 'center' }}>
        <AlertCircle size={40} style={{ color: 'var(--rose)' }} />
        <h3 style={{ fontFamily: 'var(--font-title)', fontSize: '1.25rem', fontWeight: 700, color: 'var(--rose)' }}>Data Connection Issue</h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', maxWidth: '400px', lineHeight: '1.5' }}>{error}</p>
      </div>
    );
  }

  const scores = readinessData?.assessment_scores || {
    skill_strength: 70,
    project_strength: 70,
    interview_strength: 70,
    profile_strength: 70
  };

  const careerStage = scores.career_stage || {
    career_stage: "Initial Assessment",
    track_status: "On Schedule"
  };

  const companyReadiness = scores.company_readiness || {
    company_fit_score: 65.0,
    fit_category: "Moderate Alignment"
  };

  // Radial Ring helper
  const renderProgressRing = (value, className) => {
    const radius = 50;
    const circ = 2 * Math.PI * radius; // ~314.159
    const offset = circ - (value / 100) * circ;

    return (
      <div className="gauge-svg-container">
        <svg width="120" height="120" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r={radius} className="gauge-bg-circle" />
          <circle 
            cx="60" 
            cy="60" 
            r={radius} 
            className={`gauge-active-circle ${className}`}
            style={{
              strokeDasharray: circ,
              strokeDashoffset: offset
            }}
          />
        </svg>
        <div className="gauge-percentage">{value}%</div>
      </div>
    );
  };

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

  return (
    <motion.div 
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="career-report-wrapper"
    >
      <motion.div className="report-header-banner" variants={itemVariants}>
        <h1>SDE Placement & Career Twin Report</h1>
        <p>Comprehensive analytical dashboard outlining SDE placement indicators, outcomes forecast, and corporate twin similarity records.</p>
      </motion.div>

      {/* Row 1: Circular Progress Gauges */}
      <motion.div className="section-header-row" variants={itemVariants}>
        <div className="section-header-title">
          <Cpu size={18} />
          <span>Preparation Component Strengths</span>
        </div>
      </motion.div>

      <motion.div className="gauges-grid" variants={itemVariants}>
        <div className="glass-card gauge-card">
          {renderProgressRing(scores.skill_strength, 'circle-skills')}
          <div className="gauge-title">Skill Strength</div>
        </div>

        <div className="glass-card gauge-card">
          {renderProgressRing(scores.project_strength, 'circle-projects')}
          <div className="gauge-title">Project Strength</div>
        </div>

        <div className="glass-card gauge-card">
          {renderProgressRing(scores.interview_strength, 'circle-interview')}
          <div className="gauge-title">Interview Strength</div>
        </div>

        <div className="glass-card gauge-card">
          {renderProgressRing(scores.profile_strength, 'circle-profile')}
          <div className="gauge-title">Profile Strength</div>
        </div>
      </motion.div>

      {/* Row 2: Outcomes Forecast & Alignment summaries */}
      <motion.div className="report-row-split-2" variants={itemVariants}>
        
        {/* Placement Forecast Card using student_outcomes table */}
        <div className="glass-card forecast-card">
          <h3 className="section-header-title" style={{ marginBottom: '1.25rem' }}>
            <Zap size={16} style={{ color: 'var(--amber)' }} />
            <span>Placement Forecast & Outcomes</span>
          </h3>
          
          {outcomeData ? (
            <div className="forecast-details">
              <div className="forecast-row">
                <span className="forecast-lbl">Forecasted Employer:</span>
                <span className="forecast-val">{outcomeData.placed_company}</span>
              </div>
              <div className="forecast-row">
                <span className="forecast-lbl">Forecasted Role:</span>
                <span className="forecast-val">{outcomeData.placed_role}</span>
              </div>
              <div className="forecast-row">
                <span className="forecast-lbl">Expected Package LPA:</span>
                <span className="forecast-val" style={{ color: 'var(--emerald)' }}>
                  ₹ {outcomeData.package_lpa} LPA
                </span>
              </div>
              <div className="forecast-row">
                <span className="forecast-lbl">Prediction Accuracy:</span>
                <span className="forecast-val">
                  {(outcomeData.prediction_accuracy_score * 100).toFixed(0)}% Confidence
                </span>
              </div>
              <div className="forecast-row">
                <span className="forecast-lbl">Startup Scalability Index:</span>
                <span className="forecast-val" style={{ color: 'var(--primary)' }}>
                  {outcomeData.startup_scalability_score.toFixed(0)}/100
                </span>
              </div>

              {/* Editable Feedback notes */}
              <div className="feedback-input-box">
                <label htmlFor="feedback-notes">Placement Officer / Candidate Feedback Notes</label>
                <textarea 
                  id="feedback-notes"
                  className="feedback-textarea"
                  rows="3"
                  placeholder="Enter comments on prediction matching or placement updates..."
                  value={feedbackNotes}
                  onChange={e => setFeedbackNotes(e.target.value)}
                />
                <button 
                  className="btn-secondary" 
                  onClick={handleSaveFeedback} 
                  disabled={savingFeedback}
                  style={{ alignSelf: 'flex-end', padding: '0.4rem 1rem', fontSize: '0.8rem', marginTop: '0.5rem' }}
                >
                  {savingFeedback ? (
                    <span>Saving...</span>
                  ) : saveSuccess ? (
                    <>
                      <Check size={12} style={{ color: 'var(--emerald)' }} />
                      <span style={{ color: 'var(--emerald)' }}>Feedback Saved!</span>
                    </>
                  ) : (
                    <>
                      <Save size={12} />
                      <span>Save Feedback</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          ) : (
            <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem 0' }}>
              No forecast resolved. Onboarding data must be finalized.
            </div>
          )}
        </div>

        {/* Alignment summary */}
        <div className="glass-card alignment-card">
          <h3 className="section-header-title" style={{ marginBottom: '1.5rem' }}>
            <ShieldCheck size={16} style={{ color: 'var(--primary)' }} />
            <span>Corporate Fit & Stage Metrics</span>
          </h3>

          <div className="alignment-metric-item">
            <span className="alignment-icon">
              <TrendingUp size={18} style={{ color: 'var(--emerald)' }} />
            </span>
            <div className="alignment-text">
              <h4>Active Preparation Phase</h4>
              <p>{careerStage.career_stage} <span style={{ color: 'var(--emerald)', fontWeight: 600 }}>({careerStage.track_status})</span></p>
            </div>
          </div>

          <div className="alignment-metric-item">
            <span className="alignment-icon">
              <Target size={18} style={{ color: 'var(--primary)' }} />
            </span>
            <div className="alignment-text">
              <h4>Target Company Match Fit</h4>
              <p>
                {companyReadiness.company_fit_score.toFixed(1)}% Alignment Rating 
                <span style={{ color: 'var(--primary)', fontWeight: 600, marginLeft: '0.5rem' }}>({companyReadiness.fit_category})</span>
              </p>
            </div>
          </div>

          <div className="alignment-metric-item">
            <span className="alignment-icon">
              <Award size={18} style={{ color: 'var(--amber)' }} />
            </span>
            <div className="alignment-text">
              <h4>Placement Status</h4>
              <p>{outcomeData?.placement_status || 'Seeking Placement'}</p>
            </div>
          </div>
        </div>

      </motion.div>

      {/* Row 3: Similar SDE peers */}
      <motion.div className="glass-panel peers-section-card" variants={itemVariants}>
        <h3 className="section-header-title">
          <Users size={18} />
          <span>Matched SDE Career Twins</span>
        </h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.25rem' }}>
          Successful developer transitions that match your profile vector indices.
        </p>

        <div className="peers-grid-list">
          {readinessData?.similar_engineers && readinessData.similar_engineers.length > 0 ? (
            readinessData.similar_engineers.map((p, idx) => (
              <div key={idx} className="peer-card">
                <div className="peer-match">
                  <span>SDE Twin #{idx + 1}</span>
                  <span>{(p.similarity_score * 100).toFixed(0)}% Match</span>
                </div>
                <div className="peer-company">{p.company_name}</div>
                <div className="peer-role">{p.role_name}</div>
                <div className="peer-path">
                  <strong>Path:</strong> {p.career_path ? p.career_path.join(' ➔ ') : 'CS Graduate ➔ Intern ➔ SDE-1'}
                </div>
              </div>
            ))
          ) : (
            <div style={{ gridColumn: '1 / -1', color: 'var(--text-muted)', padding: '1rem', textAlign: 'center' }}>
              No similar peers calculated.
            </div>
          )}
        </div>
      </motion.div>

      {/* Row 4: Gaps Table */}
      <motion.div className="glass-panel gaps-table-card" variants={itemVariants}>
        <h3 className="section-header-title">
          <AlertCircle size={18} />
          <span>Curated Skills Gap Analysis</span>
        </h3>
        
        <table className="gaps-table">
          <thead>
            <tr>
              <th>Skill / Technology</th>
              <th>Priority Weight</th>
              <th>Impact Level</th>
              <th>Coach Reasoning</th>
            </tr>
          </thead>
          <tbody>
            {recsData?.coach_recommendations && recsData.coach_recommendations.length > 0 ? (
              recsData.coach_recommendations.map((rec, idx) => {
                let badgeClass = "low";
                if (rec.priority >= 7.5) badgeClass = "high";
                else if (rec.priority >= 4.5) badgeClass = "medium";

                return (
                  <tr key={idx}>
                    <td style={{ fontWeight: 600 }}>{rec.skill}</td>
                    <td>
                      <span className={`priority-badge ${badgeClass}`}>
                        {rec.priority.toFixed(1)}
                      </span>
                    </td>
                    <td>
                      <span className={`impact-badge ${rec.impact || 'Medium'}`}>
                        {rec.impact || 'Medium'}
                      </span>
                    </td>
                    <td style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{rec.reason}</td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan="4" style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>
                  No missing gaps detected. All requirements met!
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </motion.div>

      {/* Row 5: Milestones timeline */}
      <motion.div className="glass-panel timeline-card" variants={itemVariants}>
        <h3 className="section-header-title">
          <Map size={18} />
          <span>Milestone Curriculum Stages</span>
        </h3>

        <div className="milestones-timeline">
          {readinessData?.timeline?.stages && readinessData.timeline.stages.length > 0 ? (
            readinessData.timeline.stages.map((st, idx) => {
              let focusText = st.focus || "";
              let annotationText = "";
              const annotIndex = focusText.indexOf("(Coach Coach-Explanation:");
              if (annotIndex !== -1) {
                annotationText = focusText.substring(annotIndex + 25, focusText.length - 1);
                focusText = focusText.substring(0, annotIndex).trim();
              }

              return (
                <div key={idx} className="milestone-item">
                  <div className="milestone-dot" />
                  <div className="milestone-item-card">
                    <div className="milestone-header">
                      <div className="milestone-title">Stage {idx + 1}: {st.title}</div>
                      <div className="milestone-duration">{st.duration_weeks} Weeks</div>
                    </div>
                    <div className="milestone-focus">{focusText}</div>
                    {annotationText && (
                      <div className="milestone-annotation" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                        <Lightbulb size={14} style={{ color: 'var(--amber)' }} />
                        <span><strong>Coach Note:</strong> {annotationText}</span>
                      </div>
                    )}
                  </div>
                </div>
              );
            })
          ) : (
            <div style={{ color: 'var(--text-muted)', padding: '1rem' }}>No milestones loaded.</div>
          )}
        </div>
      </motion.div>

    </motion.div>
  );
}
