import React, { useState, useEffect } from 'react';
import { API_BASE } from '../App';
import { TrendingUp, Users } from 'lucide-react';
import { motion } from 'framer-motion';
import './Analytics.css';

export default function Analytics() {
  const [loading, setLoading] = useState(true);
  const [signals, setSignals] = useState([]);
  const [transitions, setTransitions] = useState([]);

  useEffect(() => {
    async function loadAnalytics() {
      setLoading(true);

      let sigList = [];
      let transList = [];

      try {
        const response = await fetch(`${API_BASE}/api/analytics/signals`);
        if (response.ok) {
          sigList = await response.json();
        }
      } catch (err) {
        console.error("Failed to fetch analytics signals:", err);
      }

      try {
        const response = await fetch(`${API_BASE}/api/analytics/transitions`);
        if (response.ok) {
          transList = await response.json();
        }
      } catch (err) {
        console.error("Failed to fetch analytics transitions:", err);
      }

      setSignals(sigList);
      setTransitions(transList);
      setLoading(false);
    }

    loadAnalytics();
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '60vh', gap: '1rem' }}>
        <div className="animate-spin" style={{ width: '40px', height: '40px', border: '3px solid var(--border-glass)', borderTop: '3px solid var(--primary)', borderRadius: '50%' }}></div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', fontFamily: 'var(--font-title)' }}>Synthesizing macro industry hiring datasets...</p>
      </div>
    );
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="analytics-wrapper"
    >
      <div className="analytics-header">
        <h1>Macro SDE Hiring Signals</h1>
        <p>Calculated representation weights and transitions observed among successful software developers.</p>
      </div>

      <div className="analytics-grid">
        
        {/* Left column: Hiring Signals Table */}
        <div className="glass-card signals-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
            <TrendingUp size={16} style={{ color: 'var(--primary)' }} />
            <h3 style={{ margin: 0, fontFamily: 'var(--font-title)', fontWeight: 800 }}>Top Hiring Signals</h3>
          </div>

          <table className="signals-table">
            <thead>
              <tr>
                <th>Signal</th>
                <th>Type</th>
                <th>Weight</th>
                <th>Insight</th>
              </tr>
            </thead>
            <tbody>
              {signals.slice(0, 10).map((sig, idx) => (
                <tr key={idx}>
                  <td><strong>{sig.name}</strong></td>
                  <td>
                    <span className={`badge-sig ${sig.type.toLowerCase()}`}>
                      {sig.type}
                    </span>
                  </td>
                  <td>
                    <span className="signal-weight-tag">{sig.weight}/10</span>
                  </td>
                  <td style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>
                    {sig.description}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Right column: Common Career Transitions */}
        <div className="glass-card transitions-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
            <Users size={16} style={{ color: 'var(--primary)' }} />
            <h3 style={{ margin: 0, fontFamily: 'var(--font-title)', fontWeight: 800 }}>Common Transitions</h3>
          </div>

          <div className="transition-list">
            {transitions.map((trans, idx) => {
              const parts = trans.path.split(' → ');
              return (
                <div key={idx} className="transition-item">
                  <div className="path-flow">
                    <span>{parts[0]}</span>
                    <span className="path-arrow">→</span>
                    <span>{parts[1]}</span>
                  </div>
                  <span className="path-count">{trans.count} Profiles</span>
                </div>
              );
            })}
          </div>
        </div>

      </div>
    </motion.div>
  );
}
