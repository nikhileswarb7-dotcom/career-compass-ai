import React, { useState } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useApp } from '../App';
import { 
  BarChart3, 
  Lightbulb, 
  Target, 
  Map, 
  TrendingUp, 
  FileText, 
  Sun, 
  Moon, 
  LogOut, 
  Menu, 
  User,
  Compass,
  Lock
} from 'lucide-react';
import './Layout.css';

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
    { name: 'Dashboard', path: '/dashboard', icon: BarChart3, level: 3, step: 'Overview' },
    { name: 'Recommendations', path: '/recommendations', icon: Lightbulb, level: 3 },
    { name: 'Interview Plan', path: '/interview-plan', icon: Target, level: 3 },
    { name: 'Prep Roadmap', path: '/roadmap', icon: Map, level: 3 },
    { name: 'Hiring Signals', path: '/analytics', icon: TrendingUp, level: 0, step: 'Trends' }, // public
    { name: 'Career Report', path: '/career-report', icon: FileText, level: 3 }
  ];

  // Helper to determine if a route is locked based on session status
  const isLocked = (item) => {
    if (item.level === 0) return false; // public is never locked
    if (!sessionId) return true;
    
    // Check status
    const statusLevels = {
      'registered': 1,
      'analyzed': 2,
      'skills_confirmed': 3,
      'dashboard_unlocked': 4,
      'recommendations_completed': 5,
      'interview_completed': 6,
      'roadmap_completed': 7,
      'career_report_completed': 8
    };
    
    const currentLevel = statusLevels[sessionStatus] || 1;
    return item.level > currentLevel;
  };

  // Profile parser is hidden once completed
  const showOnboardingLink = sessionId ? false : true;


  return (
    <div className="layout-container">
      {/* Mobile Menu Header */}
      <header className="mobile-header">
        <div className="logo-area">
          <Compass className="logo-icon" />
          <span className="logo-text">CareerCompass AI</span>
        </div>
        <button className="menu-toggle-btn" onClick={() => setSidebarOpen(!sidebarOpen)}>
          <Menu size={20} />
        </button>
      </header>

      {/* Sidebar Navigation */}
      <aside className={`sidebar-aside ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-brand">
          <Compass className="brand-icon" />
          <span className="brand-text">CareerCompass AI</span>
        </div>

        {/* User Card */}
        <div className="sidebar-user-card">
          <div className="avatar-circle">
            <User size={18} />
          </div>
          <div className="user-card-info">
            <div className="user-card-name">{user || 'Guest User'}</div>
            <div className="user-card-target">
              {careerPlan?.dream_company ? `Target: ${careerPlan.dream_company}` : 'Public View'}
            </div>
          </div>
        </div>

        {/* Menu Nav Links */}
        <nav className="sidebar-navigation">
          {showOnboardingLink && (
            <NavLink to="/student-form" className={({ isActive }) => `nav-link-item ${isActive ? 'active' : ''}`}>
              <Compass size={18} />
              <span>Roadmap Creator</span>
            </NavLink>
          )}

          {menuItems.map(item => {
            const locked = isLocked(item);
            return (
              <NavLink
                key={item.name}
                to={locked ? '#' : item.path}
                onClick={(e) => locked && e.preventDefault()}
                className={({ isActive }) => `nav-link-item ${isActive && !locked ? 'active' : ''} ${locked ? 'locked' : ''}`}
                title={locked ? 'Locked - complete prior steps first' : ''}
              >
                <item.icon size={18} />
                <span>{item.name}</span>
                {locked ? (
                  <span className="lock-badge"><Lock size={12} /></span>
                ) : (
                  item.step && <span className="step-badge">{item.step}</span>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Sidebar Footer actions */}
        <div className="sidebar-action-footer">
          <div className="theme-switcher-container">
            <button 
              className={`theme-switcher-btn ${theme === 'light' ? 'active' : ''}`} 
              onClick={() => theme !== 'light' && toggleTheme()}
              title="Light Mode"
            >
              <Sun size={15} />
            </button>
            <button 
              className={`theme-switcher-btn ${theme === 'dark' ? 'active' : ''}`} 
              onClick={() => theme !== 'dark' && toggleTheme()}
              title="Dark Mode"
            >
              <Moon size={15} />
            </button>
          </div>

          {user && (
            <button className="logout-sidebar-btn" onClick={handleLogout}>
              <LogOut size={16} />
              <span>Logout</span>
            </button>
          )}
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="layout-main-content">
        <div className="main-content-wrapper animate-fade-in">
          {children}
        </div>
      </main>

      {/* Mobile Sidebar overlay */}
      {sidebarOpen && <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />}
    </div>
  );
}
