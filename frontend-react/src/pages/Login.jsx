import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp, API_BASE } from '../App';
import { Sun, Moon, Compass, Lock, User, AlertCircle, CheckCircle, Lightbulb } from 'lucide-react';
import { motion } from 'framer-motion';
import './Login.css';

export default function Login() {
  const { theme, toggleTheme, login } = useApp();
  const [mode, setMode] = useState('login'); // 'login' or 'register'
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
        setAlertInfo({
          show: true,
          type: 'success',
          message: 'Success! Logging in...'
        });
        
        setTimeout(() => {
          login(data.username);
          navigate('/');
        }, 800);
      } else {
        setAlertInfo({
          show: true,
          type: 'success',
          message: 'Account created successfully! Logging you in...'
        });
        
        setTimeout(() => {
          login(username);
          navigate('/');
        }, 1000);
      }
    } catch (err) {
      setAlertInfo({
        show: true,
        type: 'error',
        message: `${err.message}`
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="login-container"
    >
      <button onClick={toggleTheme} className="theme-toggle-login" aria-label="Toggle Theme">
        {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
      </button>

      <div className="login-card glass-panel animate-fade-in">
        <div className="login-brand">
          <Compass className="login-logo-icon" />
          <span>CareerCompass AI</span>
        </div>
        <p className="login-subtitle">SDE Placement Coach & Analytics Engine</p>

        {/* Auth Tab Group */}
        <div className="login-tab-group">
          <button 
            type="button"
            className={`login-tab-btn ${mode === 'login' ? 'active' : ''}`}
            onClick={() => { setMode('login'); setAlertInfo({ show: false, type: '', message: '' }); }}
          >
            Sign In
          </button>
          <button 
            type="button"
            className={`login-tab-btn ${mode === 'register' ? 'active' : ''}`}
            onClick={() => { setMode('register'); setAlertInfo({ show: false, type: '', message: '' }); }}
          >
            Create Account
          </button>
        </div>

        {/* Error / Success alert banner */}
        {alertInfo.show && (
          <div className={`login-alert-banner alert-${alertInfo.type}`}>
            {alertInfo.type === 'error' ? <AlertCircle size={16} /> : <CheckCircle size={16} />}
            <span>{alertInfo.message}</span>
          </div>
        )}

        <form onSubmit={handleAuth} className="login-form">
          <div className="form-group">
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
          </div>

          <div className="form-group">
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
          </div>

          <button type="submit" disabled={loading} className="btn-primary login-submit-btn">
            {loading ? (
              <span className="animate-spin" style={{ width: '16px', height: '16px', border: '2px solid white', borderTop: '2px solid transparent', borderRadius: '50%' }}></span>
            ) : (
              mode === 'login' ? 'Sign In' : 'Create Account'
            )}
          </button>
        </form>

        {mode === 'login' && (
          <div className="login-demo-box" style={{ cursor: 'pointer' }} onClick={handleFillDemo} title="Click to auto-fill sandbox credentials">
            <div className="demo-box-title" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.25rem' }}>
              <Lightbulb size={14} style={{ color: 'var(--amber)' }} />
              <span>Sandbox Environment (Click to auto-fill credentials)</span>
            </div>
            <div>
              Username: <strong style={{ color: 'var(--text-main)' }}>student</strong> &nbsp;&bull;&nbsp; Password: <strong style={{ color: 'var(--text-main)' }}>password123</strong>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
