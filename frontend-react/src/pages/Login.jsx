import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp, API_BASE } from '../App';
import { Sun, Moon, Compass, Lock, User, AlertCircle, CheckCircle, Lightbulb } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './Login.css';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.02, delayChildren: 0.02 }
  }
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: { type: 'spring', stiffness: 350, damping: 25 }
  }
};

export default function Login() {
  const { theme, toggleTheme, login } = useApp();
  const [mode, setMode] = useState('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [alertInfo, setAlertInfo] = useState({ show: false, type: '', message: '' });
  const navigate = useNavigate();
  
  const handleFillDemo = () => {
    setUsername('student');
    setPassword('password123');
  };

  const handleAuth = async (e) => {
    e.preventDefault();
    setLoading(true);
    setAlertInfo({ show: false, type: '', message: '' });

    const endpoint = mode === 'login' ? '/api/login' : '/api/register';
    
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Authentication failed. Please check your credentials.');
      }

      if (mode === 'login') {
        setAlertInfo({ show: true, type: 'success', message: 'Success! Logging in...' });
        setTimeout(() => { login(data.username); navigate('/'); }, 800);
      } else {
        setAlertInfo({ show: true, type: 'success', message: 'Account created successfully! Logging you in...' });
        setTimeout(() => { login(username); navigate('/'); }, 1000);
      }
    } catch (err) {
      setAlertInfo({ show: true, type: 'error', message: `${err.message}` });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <motion.button 
        onClick={toggleTheme} 
        className="theme-toggle-login" 
        aria-label="Toggle Theme"
        whileHover={{ scale: 1.15, rotate: 15 }}
        whileTap={{ scale: 0.9 }}
      >
        {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
      </motion.button>

      <motion.div 
        className="login-card glass-panel"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.div className="login-brand" variants={itemVariants}>
          <motion.div
            whileHover={{ rotate: 360 }}
            transition={{ duration: 0.15, ease: 'easeInOut' }}
          >
            <Compass className="login-logo-icon" />
          </motion.div>
          <span>CareerCompass AI</span>
        </motion.div>
        
        <motion.p className="login-subtitle" variants={itemVariants}>
          SDE Placement Coach & Analytics Engine
        </motion.p>

        {/* Auth Tab Group with animated pill indicator */}
        <motion.div className="login-tab-group" variants={itemVariants}>
          <button 
            type="button"
            className={`login-tab-btn ${mode === 'login' ? 'active' : ''}`}
            onClick={() => { setMode('login'); setAlertInfo({ show: false, type: '', message: '' }); }}
          >
            Sign In
            {mode === 'login' && (
              <motion.div 
                className="tab-active-pill" 
                layoutId="activeTab"
                transition={{ type: 'spring', stiffness: 600, damping: 20 }}
              />
            )}
          </button>
          <button 
            type="button"
            className={`login-tab-btn ${mode === 'register' ? 'active' : ''}`}
            onClick={() => { setMode('register'); setAlertInfo({ show: false, type: '', message: '' }); }}
          >
            Create Account
            {mode === 'register' && (
              <motion.div 
                className="tab-active-pill" 
                layoutId="activeTab"
                transition={{ type: 'spring', stiffness: 600, damping: 20 }}
              />
            )}
          </button>
        </motion.div>

        {/* Alert banner with AnimatePresence */}
        <AnimatePresence mode="wait">
          {alertInfo.show && (
            <motion.div 
              className={`login-alert-banner alert-${alertInfo.type}`}
              initial={{ opacity: 0, y: -10, height: 0 }}
              animate={{ opacity: 1, y: 0, height: 'auto' }}
              exit={{ opacity: 0, y: -10, height: 0 }}
              transition={{ duration: 0.07 }}
            >
              {alertInfo.type === 'error' ? <AlertCircle size={16} /> : <CheckCircle size={16} />}
              <span>{alertInfo.message}</span>
            </motion.div>
          )}
        </AnimatePresence>

        <motion.form onSubmit={handleAuth} className="login-form" variants={itemVariants}>
          <motion.div 
            className="form-group"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.15 }}
          >
            <label className="form-label" htmlFor="username">Username</label>
            <div className="input-with-icon">
              <User size={16} className="input-icon" />
              <input 
                type="text" 
                id="username" 
                required 
                placeholder="e.g. rahul123" 
                className="form-input custom-login-input"
                value={username}
                onChange={e => setUsername(e.target.value)}
                disabled={loading}
              />
            </div>
          </motion.div>

          <motion.div 
            className="form-group"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <label className="form-label" htmlFor="password">Password</label>
            <div className="input-with-icon">
              <Lock size={16} className="input-icon" />
              <input 
                type="password" 
                id="password" 
                required 
                placeholder="••••••••" 
                className="form-input custom-login-input"
                value={password}
                onChange={e => setPassword(e.target.value)}
                disabled={loading}
              />
            </div>
          </motion.div>

          <motion.button 
            type="submit" 
            disabled={loading} 
            className="btn-primary login-submit-btn"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
          >
            {loading ? (
              <span className="animate-spin" style={{ width: '16px', height: '16px', border: '2px solid white', borderTop: '2px solid transparent', borderRadius: '50%', display: 'inline-block' }}></span>
            ) : (
              mode === 'login' ? 'Sign In' : 'Create Account'
            )}
          </motion.button>
        </motion.form>

        <AnimatePresence>
          {mode === 'login' && (
            <motion.div 
              className="login-demo-box" 
              style={{ cursor: 'pointer' }} 
              onClick={handleFillDemo} 
              title="Click to auto-fill sandbox credentials"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              transition={{ duration: 0.08 }}
            >
              <div className="demo-box-title" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.25rem' }}>
                <Lightbulb size={14} style={{ color: 'var(--amber)' }} />
                <span>Sandbox Environment (Click to auto-fill credentials)</span>
              </div>
              <div>
                Username: <strong style={{ color: 'var(--text-main)' }}>student</strong> &nbsp;&bull;&nbsp; Password: <strong style={{ color: 'var(--text-main)' }}>password123</strong>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
