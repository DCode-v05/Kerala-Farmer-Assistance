import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar.jsx';
import Topbar from './components/Topbar.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import { useUser } from './contexts/UserContext';
import Login from './pages/Login.jsx';
import Dashboard from './pages/Dashboard.jsx';
import Financials from './pages/Financials.jsx';
import PestDetection from './pages/PestDetection.jsx';
import Marketplace from './pages/Marketplace.jsx';
import MarketAnalysis from './pages/MarketAnalysis.jsx';
import Weather from './pages/Weather.jsx';
import KnowledgeHub from './pages/KnowledgeHub.jsx';
import Schemes from './pages/Schemes.jsx';
import Community from './pages/Community.jsx';
import Future from './pages/Future.jsx';
import Chat from './pages/Chat.jsx';
import AskOfficer from './pages/AskOfficer.jsx';
import MyProfile from './pages/MyProfile.jsx';
import ChatWidget from './components/ChatWidget.jsx';

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const { user } = useUser();
  const location = useLocation();
  const isLoginPage = location.pathname === '/login';

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 768);
      if (window.innerWidth > 768) {
        setSidebarOpen(false); // Close mobile sidebar on desktop
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Set data attribute for current page to help with CSS targeting
  useEffect(() => {
    const currentPage = location.pathname.replace('/', '') || 'dashboard';
    document.body.setAttribute('data-page', currentPage);
    
    return () => {
      document.body.removeAttribute('data-page');
    };
  }, [location.pathname]);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const closeSidebar = () => {
    setSidebarOpen(false);
  };

  // Check if user is on login page
  if (isLoginPage) {
    return (
      <div className="app-shell">
        <Routes>
          <Route path="/login" element={<Login />} />
        </Routes>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />
      <div className="content-column">
        <Topbar 
          title={user ? `Welcome back, ${user.name}!` : "Welcome back, Guest!"} 
          onMenuClick={toggleSidebar}
          showMenuButton={isMobile}
        />
        <main className="content-area">
          <Routes>
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/financials" element={
              <ProtectedRoute>
                <Financials />
              </ProtectedRoute>
            } />
            <Route path="/pest-detection" element={
              <ProtectedRoute>
                <PestDetection />
              </ProtectedRoute>
            } />
            <Route path="/marketplace" element={
              <ProtectedRoute>
                <Marketplace />
              </ProtectedRoute>
            } />
            <Route path="/market-analysis" element={
              <ProtectedRoute>
                <MarketAnalysis />
              </ProtectedRoute>
            } />
            <Route path="/weather" element={
              <ProtectedRoute>
                <Weather />
              </ProtectedRoute>
            } />
            <Route path="/knowledge-hub" element={
              <ProtectedRoute>
                <KnowledgeHub />
              </ProtectedRoute>
            } />
            <Route path="/schemes" element={
              <ProtectedRoute>
                <Schemes />
              </ProtectedRoute>
            } />
            <Route path="/community" element={
              <ProtectedRoute>
                <Community />
              </ProtectedRoute>
            } />
            <Route path="/future" element={
              <ProtectedRoute>
                <Future />
              </ProtectedRoute>
            } />
            <Route path="/chat" element={
              <ProtectedRoute>
                <Chat />
              </ProtectedRoute>
            } />
            <Route path="/ask-officer" element={
              <ProtectedRoute>
                <AskOfficer />
              </ProtectedRoute>
            } />
            <Route path="/my-profile" element={
              <ProtectedRoute>
                <MyProfile />
              </ProtectedRoute>
            } />
          </Routes>
        </main>
      </div>
      <ProtectedRoute>
        <ChatWidget />
      </ProtectedRoute>
    </div>
  );
}