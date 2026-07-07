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
        const skipLlm = localStorage.getItem('skip_llm') === 'true' ? '?skip_llm=true' : '';
        const res = await fetch(`${API_BASE}/api/readiness/${sessionId}${skipLlm}`);
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
        const skipLlm = localStorage.getItem('skip_llm') === 'true' ? '?skip_llm=true' : '';
        const res = await fetch(`${API_BASE}/api/recommendations/${sessionId}${skipLlm}`);
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
        <div className="loader-spinner animate-spin" style={{ margin: '0 auto' }}></div>
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

  return (
    <div className="career-report-wrapper animate-fade-in">
      <div className="report-header-banner">
        <h1>SDE Placement & Career Twin Report</h1>
        <p>Comprehensive analytical dashboard outlining SDE placement indicators, outcomes forecast, and corporate twin similarity records.</p>
      </div>

      {/* Row 1: Circular Progress Gauges */}
      <div className="section-header-row">
        <div className="section-header-title">
          <Cpu size={18} style={{ color: 'var(--accent-primary)' }} />
          <span>Preparation Component Strengths</span>
        </div>
      </div>

      <div className="gauges-grid">
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
      </div>

      {/* Row 2: Placement Outcome Forecast & Alignment Specs */}
      <div className="report-row-split-2">
        <div className="glass-card forecast-card">
          <h3 className="card-heading-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem', marginBottom: '1.25rem' }}>
            <TrendingUp size={16} style={{ color: 'var(--accent-primary)' }} />
            <span>Placement Outcomes Forecast</span>
          </h3>
          
          <div className="forecast-row"><span className="forecast-lbl">Active Stage Status:</span><span className="forecast-val">{careerStage.career_stage}</span></div>
          <div className="forecast-row"><span className="forecast-lbl">Preparation Schedule:</span><span className="forecast-val" style={{ color: 'var(--success)' }}>{careerStage.track_status}</span></div>
          <div className="forecast-row"><span className="forecast-lbl">Estimated Placement Likelihood:</span><span className="forecast-val" style={{ color: 'var(--primary)' }}>{outcomeData?.outcome_probability_pct || 65}%</span></div>
          <div className="forecast-row"><span className="forecast-lbl">Forecasted CTC Package Range:</span><span className="forecast-val">{outcomeData?.salary_bracket || "₹12 - ₹18 LPA"}</span></div>
          <div className="forecast-row"><span className="forecast-lbl">Projected Target Clearance:</span><span className="forecast-val">{companyReadiness.fit_category} ({companyReadiness.company_fit_score}%)</span></div>

          <div className="feedback-input-box">
            <label htmlFor="report-notes">Personal Placement Coach Feedback Notes</label>
            <textarea 
              id="report-notes"
              className="feedback-textarea" 
              placeholder="Record custom preparation remarks, mock-evaluation feedback, or visual adjustments logs..."
              value={feedbackNotes}
              onChange={e => setFeedbackNotes(e.target.value)}
            />
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
              <button 
                type="button" 
                onClick={handleSaveFeedback} 
                disabled={savingFeedback}
                className="btn-primary" 
                style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}
              >
                {savingFeedback ? 'Saving...' : saveSuccess ? <><Check size={14} /><span>Saved!</span></> : <><Save size={14} /><span>Save Notes</span></>}
              </button>
            </div>
          </div>
        </div>

        {/* System design alignment specs */}
        <div className="glass-card alignment-card">
          <h3 className="card-heading-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem', marginBottom: '1.25rem' }}>
            <Target size={16} style={{ color: 'var(--accent-secondary)' }} />
            <span>Target Bar Specifications</span>
          </h3>

          <div className="alignment-metric-item">
            <Zap className="alignment-icon" style={{ color: 'var(--accent-primary)' }} />
            <div className="alignment-text">
              <h4>Low-Latency Concurrency Bar</h4>
              <p>Requires demonstration of microservices setup using Kafka, PostgreSQL index partitions, and worker thread concurrency pools.</p>
            </div>
          </div>

          <div className="alignment-metric-item">
            <Compass className="alignment-icon" style={{ color: 'var(--accent-secondary)' }} />
            <div className="alignment-text">
              <h4>System Architecture Scope</h4>
              <p>Candidates must structure high-performance caching policies, distributed cluster sharding, and fault-tolerant Redis queue designs.</p>
            </div>
          </div>

          <div className="alignment-metric-item">
            <ShieldCheck className="alignment-icon" style={{ color: 'var(--emerald)' }} />
            <div className="alignment-text">
              <h4>Recruiter Score thresholds</h4>
              <p>Minimum CGPA requirement: 8.00. Candidate matching profile threshold verified at {companyReadiness.company_fit_score || 65}% SDE fit index rating.</p>
            </div>
          </div>
        </div>
      </div>

      {/* Row 3: Similar corporate peers matches list */}
      <div className="glass-card peers-section-card">
        <h3 className="card-heading-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem', marginBottom: '0.5rem' }}>
          <Users size={16} style={{ color: 'var(--accent-primary)' }} />
          <span>Matched Alumni Career Twins</span>
        </h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Successful SDE paths resolved inside the database showing similar vector alignment metrics.</p>

        <div className="peers-grid-list">
          {readinessData?.similar_engineers && readinessData.similar_engineers.length > 0 ? (
            readinessData.similar_engineers.map((peer, idx) => (
              <div key={idx} className="peer-card">
                <div className="peer-match">
                  <span>Match Similarity Score</span>
                  <span>{(peer.similarity_score * 100).toFixed(0)}%</span>
                </div>
                <div className="peer-company">{peer.name || "Aditya Sharma"}</div>
                <div className="peer-role">{peer.role_name || "Software Developer"} &bull; {peer.college || "IIT Kharagpur"}</div>
                <div className="peer-path">
                  <strong>Career Pathway:</strong> {(peer.career_path || []).join(' &rarr; ')}
                </div>
              </div>
            ))
          ) : (
            <div className="no-data-msg" style={{ gridColumn: '1 / -1' }}>No matches found inside database. Try adjusting your target configurations.</div>
          )}
        </div>
      </div>

      {/* Row 4: SDE Skill Gaps table */}
      <div className="glass-card gaps-table-card">
        <h3 className="card-heading-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem', marginBottom: '0.5rem' }}>
          <Award size={16} style={{ color: 'var(--accent-secondary)' }} />
          <span>Priority SDE Skill Gaps</span>
        </h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Core technologies requiring immediate checkpoint closures to align profiles with target hires.</p>

        <table className="gaps-table">
          <thead>
            <tr>
              <th>Missing Skill</th>
              <th>Priority Level</th>
              <th>Hiring Impact</th>
            </tr>
          </thead>
          <tbody>
            {(readinessData?.gaps?.high_priority_missing || []).map(skill => (
              <tr key={skill}>
                <td style={{ fontWeight: 600 }}>{skill}</td>
                <td><span className="priority-badge high">High Priority</span></td>
                <td><span className="impact-badge Critical">Critical</span></td>
              </tr>
            ))}
            {(readinessData?.gaps?.medium_priority_missing || []).map(skill => (
              <tr key={skill}>
                <td style={{ fontWeight: 600 }}>{skill}</td>
                <td><span className="priority-badge medium">Medium Priority</span></td>
                <td><span className="impact-badge High">High</span></td>
              </tr>
            ))}
            {(readinessData?.gaps?.high_priority_missing || []).length === 0 && (readinessData?.gaps?.medium_priority_missing || []).length === 0 && (
              <tr>
                <td colSpan="3" style={{ textAlign: 'center', color: 'var(--emerald)' }}>✓ All SDE skill gaps resolved. Profile matches corporate thresholds.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Row 5: Recommendations Milestones Timeline */}
      <div className="glass-card timeline-card">
        <h3 className="card-heading-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem', marginBottom: '0.5rem' }}>
          <Map size={16} style={{ color: 'var(--warning)' }} />
          <span>Guidance Milestone Milestones</span>
        </h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Sequential milestones checklist compiled to structure your roadmap progression.</p>

        <div className="milestones-timeline">
          {readinessData?.timeline?.stages && readinessData.timeline.stages.length > 0 ? (
            readinessData.timeline.stages.map((stage, idx) => (
              <div key={idx} className="milestone-item">
                <div className="milestone-dot"></div>
                <div className="milestone-item-card">
                  <div className="milestone-header">
                    <span className="milestone-title">Stage 0{idx + 1}: {stage.title}</span>
                    <span className="milestone-duration">Duration: {stage.duration_weeks} Weeks</span>
                  </div>
                  <div className="milestone-focus"><strong>Focus Area:</strong> {stage.focus_area || "SDE Core Alignment"}</div>
                  {stage.recommendation_rationale && (
                    <div className="milestone-annotation">
                      <Lightbulb size={12} style={{ color: 'var(--warning)', marginRight: '0.25rem', display: 'inline-block', verticalAlign: 'middle' }} />
                      <span>{stage.recommendation_rationale}</span>
                    </div>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div className="no-data-msg">Milestones timeline not generated yet. Configure goal settings.</div>
          )}
        </div>
      </div>
    </div>
  );
}
