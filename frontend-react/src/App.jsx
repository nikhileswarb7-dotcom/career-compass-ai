import React, { createContext, useState, useEffect, useContext } from 'react';
import { HashRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import Layout from './components/Layout';
import Welcome from './pages/Welcome';
import Login from './pages/Login';
import StudentForm from './pages/StudentForm';
import ProfileAnalysis from './pages/ProfileAnalysis';
import Dashboard from './pages/Dashboard';
import Recommendations from './pages/Recommendations';
import InterviewPlan from './pages/InterviewPlan';
import Roadmap from './pages/Roadmap';
import CareerReport from './pages/CareerReport';
import Analytics from './pages/Analytics';
import ProfileBuilder from './pages/ProfileBuilder';
import AIMentor from './pages/AIMentor';

// Create App Context for Shared State
export const AppContext = createContext();

export const useApp = () => useContext(AppContext);

// Real Backend Config
export const API_BASE = window.location.origin.includes('localhost:') || window.location.origin.includes('127.0.0.1:') 
  ? 'http://127.0.0.1:8000' 
  : window.location.origin;

function AppProvider({ children }) {
  const [user, setUser] = useState(localStorage.getItem('logged_in_user') || null);
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark');
  const [sessionId, setSessionId] = useState(localStorage.getItem('session_id') || null);
  const [studentId, setStudentId] = useState(localStorage.getItem('student_id') || null);
  const [sessionStatus, setSessionStatus] = useState(localStorage.getItem('session_status') || 'registered');
  const [careerPlan, setCareerPlan] = useState(null);
  const [sessionDetails, setSessionDetails] = useState(null);

  // Initialize Theme
  useEffect(() => {
    const html = document.documentElement;
    if (theme === 'light') {
      html.classList.add('light-theme');
    } else {
      html.classList.remove('light-theme');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Load career plan from local cache on start
  useEffect(() => {
    const cachedPlan = localStorage.getItem('career_plan');
    if (cachedPlan) {
      try {
        setCareerPlan(JSON.parse(cachedPlan));
      } catch (e) {
        console.error("Failed to parse cached plan", e);
      }
    }
  }, []);

  const login = (username) => {
    setUser(username);
    localStorage.setItem('logged_in_user', username);
  };

  const logout = () => {
    setUser(null);
    setSessionId(null);
    setStudentId(null);
    setSessionStatus('registered');
    setCareerPlan(null);
    setSessionDetails(null);
    
    // Clear everything except theme and registered_users
    const activeTheme = localStorage.getItem('theme');
    localStorage.clear();
    if (activeTheme) localStorage.setItem('theme', activeTheme);
  };

  const updateSession = (sessId, studId, planData) => {
    setSessionId(sessId);
    setStudentId(studId);
    setCareerPlan(planData);
    if (sessId) localStorage.setItem('session_id', sessId);
    if (studId) localStorage.setItem('student_id', studId);
    if (planData) localStorage.setItem('career_plan', JSON.stringify(planData));
  };

  const updateSessionStatus = (status) => {
    setSessionStatus(status);
    localStorage.setItem('session_status', status);
  };

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  return (
    <AppContext.Provider value={{
      user,
      theme,
      sessionId,
      studentId,
      sessionStatus,
      careerPlan,
      sessionDetails,
      setCareerPlan,
      setSessionDetails,
      login,
      logout,
      updateSession,
      updateSessionStatus,
      toggleTheme
    }}>
      {children}
    </AppContext.Provider>
  );
}

// Route Guard to verify user is logged in
function RequireAuth({ children }) {
  const { user } = useApp();
  const location = useLocation();

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return children;
}

// Route Guard to verify student has completed onboarding session
function RequireSession({ children, requiredLevel }) {
  const { sessionId, sessionStatus, updateSessionStatus } = useApp();
  const [loading, setLoading] = useState(true);
  const [allowed, setAllowed] = useState(false);
  const [redirectPath, setRedirectPath] = useState('/student-form');

  useEffect(() => {
    if (!sessionId) {
      setAllowed(false);
      setLoading(false);
      return;
    }

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

    if (currentLevel < requiredLevel) {
      setAllowed(false);
      let target = '/student-form';
      if (currentLevel >= 2) target = '/profile-analysis';
      if (currentLevel >= 3) target = '/dashboard';
      if (currentLevel >= 4) target = '/recommendations';
      if (currentLevel >= 5) target = '/interview-plan';
      if (currentLevel >= 6) target = '/roadmap';
      if (currentLevel >= 7) target = '/career-report';
      
      setRedirectPath(target);
    } else {
      setAllowed(true);
    }
    setLoading(false);

    // Call API to verify session status in background to ensure local state is synced
    async function verifySession() {
      try {
        const response = await fetch(`${API_BASE}/api/session/${sessionId}`);
        if (response.ok) {
          const sessionData = await response.json();
          // Sync the local status state if it drifts, but NEVER downgrade it to prevent race conditions during transitions
          if (sessionData.status !== sessionStatus) {
            const dbLevel = statusLevels[sessionData.status] || 1;
            const localLevel = statusLevels[sessionStatus] || 1;
            if (dbLevel > localLevel) {
              updateSessionStatus(sessionData.status);
            }
          }
        }
      } catch (err) {
        console.error("Session background sync error:", err);
      }
    }

    verifySession();
  }, [sessionId, requiredLevel, sessionStatus, updateSessionStatus]);

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100vh', gap: '1rem', background: 'var(--bg-dark)' }}>
        <div className="loader-spinner animate-spin" style={{ margin: '0 auto' }}></div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', fontFamily: 'var(--font-title)' }}>Verifying active intelligence session...</p>
      </div>
    );
  }

  if (!allowed) {
    return <Navigate to={redirectPath} replace />;
  }

  return children;
}

// Page transition variants
const pageTransition = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.18, ease: [0.16, 1, 0.3, 1] } },
  exit: { opacity: 0, y: -8, transition: { duration: 0.1, ease: 'easeIn' } }
};

export function PageTransition({ children }) {
  return (
    <motion.div
      variants={pageTransition}
      initial="initial"
      animate="animate"
      exit="exit"
      className="page-transition-wrapper"
    >
      {children}
    </motion.div>
  );
}

function AnimatedRoutes() {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        {/* Guest Public routes */}
        <Route path="/login" element={<PageTransition><Login /></PageTransition>} />
        <Route path="/analytics" element={<PageTransition><Layout><Analytics /></Layout></PageTransition>} />

        {/* Authenticated routes */}
        <Route path="/" element={<RequireAuth><PageTransition><Welcome /></PageTransition></RequireAuth>} />
        <Route path="/student-form" element={<RequireAuth><PageTransition><Layout><StudentForm /></Layout></PageTransition></RequireAuth>} />
        <Route path="/profile-analysis" element={<RequireAuth><PageTransition><Layout><ProfileAnalysis /></Layout></PageTransition></RequireAuth>} />
        
        {/* Onboarding Session gated routes */}
        <Route path="/dashboard" element={
          <RequireAuth>
            <RequireSession requiredLevel={3}>
              <PageTransition><Layout><Dashboard /></Layout></PageTransition>
            </RequireSession>
          </RequireAuth>
        } />
        <Route path="/recommendations" element={
          <RequireAuth>
            <RequireSession requiredLevel={3}>
              <PageTransition><Layout><Recommendations /></Layout></PageTransition>
            </RequireSession>
          </RequireAuth>
        } />
        <Route path="/interview-plan" element={
          <RequireAuth>
            <RequireSession requiredLevel={3}>
              <PageTransition><Layout><InterviewPlan /></Layout></PageTransition>
            </RequireSession>
          </RequireAuth>
        } />
        <Route path="/roadmap" element={
          <RequireAuth>
            <RequireSession requiredLevel={3}>
              <PageTransition><Layout><Roadmap /></Layout></PageTransition>
            </RequireSession>
          </RequireAuth>
        } />
        <Route path="/career-report" element={
          <RequireAuth>
            <RequireSession requiredLevel={3}>
              <PageTransition><Layout><CareerReport /></Layout></PageTransition>
            </RequireSession>
          </RequireAuth>
        } />
        <Route path="/profile-builder" element={
          <RequireAuth>
            <RequireSession requiredLevel={3}>
              <PageTransition><Layout><ProfileBuilder /></Layout></PageTransition>
            </RequireSession>
          </RequireAuth>
        } />
        <Route path="/ai-mentor" element={
          <RequireAuth>
            <RequireSession requiredLevel={3}>
              <PageTransition><Layout><AIMentor /></Layout></PageTransition>
            </RequireSession>
          </RequireAuth>
        } />

        {/* Catch-all fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AnimatePresence>
  );
}

export default function App() {
  return (
    <AppProvider>
      <HashRouter>
        <AnimatedRoutes />
      </HashRouter>
    </AppProvider>
  );
}
