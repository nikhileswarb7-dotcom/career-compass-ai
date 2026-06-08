import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp, API_BASE } from '../App';
import { Sun, Moon, Sparkles, Compass, TrendingUp, Key } from 'lucide-react';
import { motion } from 'framer-motion';
import './Welcome.css';

export default function Welcome() {
  const { theme, sessionId, logout, toggleTheme } = useApp();
  const navigate = useNavigate();

  const handleStartNew = () => {
    // Clear session & plan state, keeping theme & user
    const loggedInUser = localStorage.getItem('logged_in_user');
    const users = localStorage.getItem('registered_users');
    const activeTheme = localStorage.getItem('theme');

    localStorage.clear();

    if (loggedInUser) localStorage.setItem('logged_in_user', loggedInUser);
    if (users) localStorage.setItem('registered_users', users);
    if (activeTheme) localStorage.setItem('theme', activeTheme);

    navigate('/student-form');
  };

  const handleContinue = async () => {
    if (!sessionId) {
      alert("No active session found. Please start a new analysis first.");
      navigate('/student-form');
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/session/${sessionId}`);
      if (!response.ok) {
        alert("Your session could not be validated or has expired. Please start a new analysis.");
        handleStartNew();
        return;
      }
      const sessionData = await response.json();
      const status = sessionData.status;

      // Status mapping to target pages
      if (status === 'registered') {
        navigate('/student-form');
      } else if (status === 'analyzed') {
        navigate('/profile-analysis');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      console.error("Error connecting to server:", err);
      alert("Server is offline. Unable to load session.");
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="welcome-container"
    >
      <button onClick={toggleTheme} className="theme-toggle-welcome" aria-label="Toggle Theme">
        {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
      </button>

      <button onClick={handleLogout} className="logout-welcome-btn">
        Logout
      </button>

      <div className="welcome-card glass-panel animate-fade-in">
        <div className="welcome-brand">
          <Compass className="welcome-logo-icon" />
          <span>CareerCompass AI</span>
        </div>
        <p className="welcome-tagline">Personalized NLP SDE Placement Advisor & Roadmap Generator</p>

        <div className="welcome-grid">
          <button onClick={handleStartNew} className="welcome-btn-card">
            <div className="welcome-btn-title start-new">
              <Sparkles size={18} />
              <span>Start New</span>
            </div>
            <div className="welcome-btn-desc">
              Initialize a new onboarding session, upload your PDF resume, and build a fresh career roadmap.
            </div>
          </button>

          <button onClick={handleContinue} className="welcome-btn-card">
            <div className="welcome-btn-title continue">
              <Compass size={18} />
              <span>Continue</span>
            </div>
            <div className="welcome-btn-desc">
              Resume your previous active analysis flow or view your currently unlocked dashboard/roadmap.
            </div>
          </button>

          <button onClick={() => navigate('/analytics')} className="welcome-btn-card">
            <div className="welcome-btn-title analytics">
              <TrendingUp size={18} />
              <span>Analytics</span>
            </div>
            <div className="welcome-btn-desc">
              Explore macro SDE hiring trends, placement signals, and general database metrics.
            </div>
          </button>
        </div>
      </div>
    </motion.div>
  );
}
