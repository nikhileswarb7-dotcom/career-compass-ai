import React, { useState } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useApp } from '../App';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  TrendingUp, 
  Sun, 
  Moon, 
  LogOut, 
  Menu, 
  User,
  Compass,
  Lock,
  X,
  Sparkles,
  Map,
  Target,
  FileText,
  Award,
  ChevronRight
} from 'lucide-react';
import './Layout.css';

const navItemVariants = {
  hidden: { opacity: 0, x: -10 },
  visible: (i) => ({
    opacity: 1,
    x: 0,
    transition: { delay: i * 0.02, type: 'spring', stiffness: 380, damping: 26 }
  })
};

export default function Layout({ children }) {
  const { user, theme, sessionId, sessionStatus, careerPlan, toggleTheme, logout } = useApp();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const menuItems = [
    { name: 'Home Workspace', path: '/', icon: Compass, level: 0 },
    { name: 'AI Mentor', path: '/ai-mentor', icon: Sparkles, level: 3 },
    { name: 'Learning Journey', path: '/roadmap', icon: Map, level: 3 },
    { name: 'Practice Hub', path: '/interview-plan', icon: Target, level: 3 },
    { name: 'Portfolio & ATS', path: '/profile-builder', icon: FileText, level: 3 },
    { name: 'Macro Trends', path: '/analytics', icon: TrendingUp, level: 0 },
    { name: 'Career Report', path: '/career-report', icon: Award, level: 3 }
  ];

  const isLocked = (item) => {
    if (item.level === 0) return false;
    if (!sessionId) return true;
    const statusLevels = {
      'registered': 1, 'analyzed': 2, 'skills_confirmed': 3,
      'dashboard_unlocked': 4, 'recommendations_completed': 5,
      'interview_completed': 6, 'roadmap_completed': 7, 'career_report_completed': 8
    };
    const currentLevel = statusLevels[sessionStatus] || 1;
    return item.level > currentLevel;
  };

  return (
    <div className="layout-container">
      {/* Mobile Menu Header */}
      <header className="mobile-header">
        <div className="logo-area">
          <Compass className="logo-icon animate-pulse-glow" />
          <span className="logo-text">CareerCompass AI</span>
        </div>
        <button className="menu-toggle-btn" onClick={() => setSidebarOpen(!sidebarOpen)}>
          <Menu size={20} />
        </button>
      </header>

      {/* Desktop Sidebar */}
      <aside className={`sidebar-aside ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-brand" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
          <motion.div 
            className="brand-icon-wrapper"
            whileHover={{ rotate: 180 }}
            transition={{ duration: 0.2, ease: 'easeInOut' }}
          >
            <Compass className="brand-icon" />
          </motion.div>
          <span className="brand-text">CareerCompass AI</span>
        </div>

        {/* User Card & SDE Target Badge */}
        <motion.div 
          className="sidebar-user-card"
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ type: 'spring', stiffness: 300, damping: 20 }}
        >
          <div className="avatar-circle">
            <User size={16} />
          </div>
          <div className="user-card-info">
            <div className="user-card-name">{user || 'Guest User'}</div>
            {careerPlan?.dream_company ? (
              <div className="user-card-target" title={`${careerPlan.target_role || 'SDE'} @ ${careerPlan.dream_company}`}>
                Target: <strong>{careerPlan.dream_company}</strong>
                <div className="target-role-sub">{careerPlan.target_role?.split(' (')[0] || 'SDE'}</div>
              </div>
            ) : (
              <div className="user-card-target">Workspace Inactive</div>
            )}
          </div>
        </motion.div>

        {/* Menu Nav Links */}
        <nav className="sidebar-navigation">
          {menuItems.map((item, idx) => {
            const locked = isLocked(item);
            const isActive = location.pathname === item.path;
            
            return (
              <motion.div
                key={item.name}
                custom={idx}
                variants={navItemVariants}
                initial="hidden"
                animate="visible"
              >
                <NavLink
                  to={locked ? '#' : item.path}
                  onClick={(e) => locked && e.preventDefault()}
                  className={`nav-link-item ${isActive && !locked ? 'active' : ''} ${locked ? 'locked' : ''}`}
                  title={locked ? 'Complete onboarding & verification steps first' : ''}
                >
                  <item.icon size={18} className="nav-icon" />
                  <span className="nav-text">{item.name}</span>
                  {locked && (
                    <span className="lock-badge"><Lock size={12} /></span>
                  )}
                  {isActive && !locked && (
                    <motion.div 
                      className="active-indicator" 
                      layoutId="activeIndicator"
                      transition={{ type: "spring", stiffness: 380, damping: 30 }}
                    />
                  )}
                </NavLink>
              </motion.div>
            );
          })}
        </nav>

        {/* Sidebar Footer */}
        <div className="sidebar-action-footer">
          <div className="theme-switcher-container">
            <motion.button 
              className={`theme-switcher-btn ${theme === 'light' ? 'active' : ''}`} 
              onClick={() => theme !== 'light' && toggleTheme()}
              title="Light Theme"
              whileTap={{ scale: 0.95 }}
            >
              <Sun size={14} />
            </motion.button>
            <motion.button 
              className={`theme-switcher-btn ${theme === 'dark' ? 'active' : ''}`} 
              onClick={() => theme !== 'dark' && toggleTheme()}
              title="Dark Theme"
              whileTap={{ scale: 0.95 }}
            >
              <Moon size={14} />
            </motion.button>
          </div>

          {user && (
            <motion.button 
              className="logout-sidebar-btn" 
              onClick={handleLogout}
              whileHover={{ x: 3 }}
              whileTap={{ scale: 0.97 }}
            >
              <LogOut size={14} />
              <span>Sign Out</span>
            </motion.button>
          )}
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="layout-main-content">
        <div className="main-content-wrapper">
          {children}
        </div>
      </main>

      {/* Mobile Sidebar overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div 
            className="sidebar-overlay" 
            onClick={() => setSidebarOpen(false)}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
