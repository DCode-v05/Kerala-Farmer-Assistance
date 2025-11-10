import React from 'react';
import { NavLink } from 'react-router-dom';

const NavBtn = ({ to, icon, label }) => (
  <NavLink to={to} className={({isActive}) => `nav-btn ${isActive ? 'active' : ''}`}>
    <span className="icon">{icon}</span>
    <span>{label}</span>
  </NavLink>
);

export default function Sidebar({ isOpen, onClose }) {
  const handleNavClick = () => {
    // Close sidebar on mobile when navigation item is clicked
    if (onClose) {
      onClose();
    }
  };

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div 
          className="sidebar-backdrop" 
          onClick={onClose}
          aria-hidden="true"
        />
      )}
      
      <nav className={`sidebar ${isOpen ? 'open' : ''}`}>
        <h2 className="brand">Krishi Sakhi</h2>
        <div onClick={handleNavClick}>
          <NavBtn to="/dashboard" icon="🏠" label="Dashboard" />
          <NavBtn to="/weather" icon="🌤️" label="Weather Analysis" />
          <NavBtn to="/market-analysis" icon="📈" label="Market Analysis" />
          <NavBtn to="/financials" icon="📊" label="Financials" />
          <NavBtn to="/pest-detection" icon="🪲" label="Pest Detection" />
          <NavBtn to="/marketplace" icon="🛒" label="Marketplace" />
          <NavBtn to="/knowledge-hub" icon="📚" label="Knowledge Hub" />
          <NavBtn to="/schemes" icon="📜" label="Schemes" />
          <NavBtn to="/community" icon="👥" label="Community" />
          <NavBtn to="/future" icon="🚀" label="Future Features" />
          <NavBtn to="/ask-officer" icon="👮" label="Ask an Officer" />
          <NavBtn to="/my-profile" icon="👤" label="My Profile" />
        </div>

      </nav>
    </>
  );
}