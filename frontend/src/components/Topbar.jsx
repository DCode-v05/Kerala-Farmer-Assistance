import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import TranslationWidget from './TranslationWidget';

export default function Topbar({ title, onMenuClick, showMenuButton }) {
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [userInfo, setUserInfo] = useState({ name: 'Guest User', id: null });
  const navigate = useNavigate();

  useEffect(() => {
    fetchUserProfile();
  }, []);

  const fetchUserProfile = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/check-session', {
        method: 'GET',
        credentials: 'include'
      });
      const data = await response.json();
      
      if (data.success && data.logged_in) {
        setUserInfo({
          name: data.farmer?.name || 'Farmer',
          id: data.farmer?.id || null
        });
      }
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
    }
  };

  const handleLogout = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/logout', {
        method: 'POST',
        credentials: 'include'
      });
      
      if (response.ok) {
        navigate('/login');
      }
    } catch (error) {
      console.error('Logout failed:', error);
      // Force redirect even if API fails
      navigate('/login');
    }
  };

  const handleTranslate = async (languageCode) => {
    try {
      // Call translation API
      const response = await fetch('http://localhost:5000/api/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          text: 'Page content translation',
          target_language: languageCode === 'ml' ? 'malayalam' : 'english'
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        console.log('Translation successful:', data);
        // Here you could implement actual page content translation
      } else {
        throw new Error(data.error || 'Translation failed');
      }
    } catch (error) {
      console.error('Translation error:', error);
      throw error; // Re-throw so TranslationWidget can handle it
    }
  };
  
  return (
    <div className="topbar">
      <div className="topbar-left">
        {showMenuButton && (
          <button 
            className="mobile-menu-btn"
            onClick={onMenuClick}
            aria-label="Toggle menu"
          >
            <span className="hamburger">
              <span></span>
              <span></span>
              <span></span>
            </span>
          </button>
        )}
        <h1 className="page-title">{title}</h1>
      </div>
      
      <div className="topbar-actions">
        <TranslationWidget 
          onTranslate={handleTranslate}
          position="topbar"
        />
        
        <div className="profile">
          <button 
            className="profile-button"
            onClick={() => setShowProfileMenu(!showProfileMenu)}
            aria-expanded={showProfileMenu}
            aria-label="User profile"
          >
            <div className="avatar">
              <span>👤</span>
            </div>
            <span className="username">{userInfo.name}</span>
            <span className="dropdown-arrow">▼</span>
          </button>
          
          {showProfileMenu && (
            <div className="profile-menu">
              <div className="profile-header">
                <div className="avatar large">
                  <span>👤</span>
                </div>
                <div className="profile-info">
                  <div className="name">{userInfo.name}</div>
                  <div className="email">{userInfo.id ? `ID: ${userInfo.id}` : 'Kerala Farmer'}</div>
                </div>
              </div>
              <div className="menu-divider"></div>
              <ul className="menu-items">
                <li className="menu-item">
                  <button className="menu-button">
                    <span className="menu-icon">👤</span>
                    <span>My Profile</span>
                  </button>
                </li>
                <div className="menu-divider"></div>
                <li className="menu-item">
                  <button className="menu-button text-red" onClick={handleLogout}>
                    <span className="menu-icon">🚪</span>
                    <span>Logout</span>
                  </button>
                </li>
              </ul>
            </div>
          )}
        </div>
      </div>
      
      {showProfileMenu && (
        <div 
          className="overlay" 
          onClick={() => setShowProfileMenu(false)}
        />
      )}
      
      <style jsx>{`
        .topbar {
          background: #2e7d32;
          padding: 0 2rem;
          height: 70px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
          position: relative;
          z-index: 100;
        }
        
        .page-title {
          font-size: 1.5rem;
          font-weight: 600;
          color: white;
          margin: 0;
        }
        
        .topbar-actions {
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }
        
        .profile-button {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          background: rgba(255, 255, 255, 0.2);
          border: none;
          border-radius: 20px;
          padding: 0.4rem 1rem 0.4rem 0.6rem;
          cursor: pointer;
          transition: all 0.2s;
          color: white;
        }
        
        .profile-button:hover {
          background: rgba(255, 255, 255, 0.3);
        }
        
        .avatar {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background: #e0e0e0;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.1rem;
        }
        
        .avatar.large {
          width: 48px;
          height: 48px;
          font-size: 1.5rem;
        }
        
        .username {
          font-weight: 500;
          font-size: 0.9rem;
          color: white;
        }
        
        .dropdown-arrow {
          font-size: 0.6rem;
          color: rgba(255, 255, 255, 0.8);
          margin-left: 0.25rem;
        }
        
        .profile-menu {
          position: absolute;
          top: 70px;
          right: 2rem;
          width: 280px;
          background: white;
          border-radius: 8px;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
          z-index: 101;
          overflow: hidden;
          animation: fadeIn 0.2s ease-out;
        }
        
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        .profile-header {
          padding: 1.25rem;
          display: flex;
          align-items: center;
          gap: 1rem;
          background: linear-gradient(135deg, #4CAF50, #45a049);
          color: white;
        }
        
        .profile-info {
          flex: 1;
          overflow: hidden;
        }
        
        .profile-info .name {
          font-weight: 600;
          font-size: 1rem;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        
        .profile-info .email {
          font-size: 0.85rem;
          opacity: 0.9;
          margin-top: 0.2rem;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        
        .menu-divider {
          height: 1px;
          background-color: #f0f0f0;
          margin: 0.5rem 0;
        }
        
        .menu-items {
          padding: 0.5rem 0;
          list-style: none;
          margin: 0;
        }
        
        .menu-item {
          margin: 0;
        }
        
        .menu-button {
          width: 100%;
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.7rem 1.25rem;
          background: none;
          border: none;
          text-align: left;
          font-size: 0.9rem;
          color: #333;
          cursor: pointer;
          transition: background-color 0.2s;
        }
        
        .menu-button:hover {
          background-color: #f8f8f8;
        }
        
        .menu-icon {
          width: 20px;
          text-align: center;
        }
        
        .text-red {
          color: #f44336;
        }
        
        .overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.2);
          z-index: 99;
          animation: fadeIn 0.2s ease-out;
        }
      `}</style>
    </div>
  );
}