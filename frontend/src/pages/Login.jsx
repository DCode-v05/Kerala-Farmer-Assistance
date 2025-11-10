import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../contexts/UserContext';

const Login = () => {
  const [formData, setFormData] = useState({
    farmer_id: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const { login, isAuthenticated } = useUser();
  const navigate = useNavigate();

  // Check if already logged in
  useEffect(() => {
    const checkSession = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/check-session', {
          method: 'GET',
          credentials: 'include'
        });
        const data = await response.json();
        
        if (data.success && data.logged_in) {
          if (data.farmer) {
            login(data.farmer);
          }
          setIsLoggedIn(true);
          navigate('/dashboard');
        }
      } catch (error) {
        console.log('Session check failed:', error);
      }
    };
    
    checkSession();
  }, [navigate, login]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:5000/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (data.success) {
        // Update user context with farmer data
        if (data.farmer) {
          login(data.farmer);
        }
        setIsLoggedIn(true);
        navigate('/dashboard');
      } else {
        setError(data.error || 'Login failed');
      }
    } catch {
      setError('Connection error. Please check if the server is running.');
    } finally {
      setLoading(false);
    }
  };

  if (isLoggedIn) {
    return <div>Redirecting...</div>;
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <div className="logo">
            <span className="logo-icon">🌾</span>
            <h1>Krishi Sakhi</h1>
            <p>Kerala Farmer Assistance System</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="farmer_id">Farmer ID</label>
            <input
              type="text"
              id="farmer_id"
              name="farmer_id"
              value={formData.farmer_id}
              onChange={handleInputChange}
              placeholder="Enter your Farmer ID (e.g., KL001)"
              required
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              placeholder="Enter your password"
              required
              autoComplete="current-password"
            />
          </div>

          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              {error}
            </div>
          )}

          <button
            type="submit"
            className="login-button"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Logging in...
              </>
            ) : (
              'Login'
            )}
          </button>
        </form>

        <div className="login-footer">
          <div className="help-text">
            <p>Need help? Contact your local agricultural officer</p>
            <p className="demo-info">
              Demo Login: ID: <strong>KL001</strong> | Password: <strong>RameshKL001@123</strong>
            </p>
          </div>
        </div>
      </div>

      <style jsx>{`
        .login-container {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
          padding: 20px;
        }

        .login-card {
          background: white;
          border-radius: 16px;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
          width: 100%;
          max-width: 400px;
          padding: 40px;
          animation: slideUp 0.5s ease-out;
        }

        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .login-header {
          text-align: center;
          margin-bottom: 30px;
        }

        .logo {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 8px;
        }

        .logo-icon {
          font-size: 3rem;
          margin-bottom: 10px;
        }

        .logo h1 {
          color: #2E7D32;
          font-size: 2rem;
          margin: 0;
          font-weight: 700;
        }

        .logo p {
          color: #666;
          margin: 0;
          font-size: 0.9rem;
        }

        .login-form {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .form-group label {
          font-weight: 600;
          color: #333;
          font-size: 0.9rem;
        }

        .form-group input {
          padding: 12px 16px;
          border: 2px solid #e0e0e0;
          border-radius: 8px;
          font-size: 1rem;
          transition: all 0.2s;
          background: #fafafa;
        }

        .form-group input:focus {
          outline: none;
          border-color: #4CAF50;
          background: white;
          box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
        }

        .error-message {
          background: #ffebee;
          color: #c62828;
          padding: 12px 16px;
          border-radius: 8px;
          border-left: 4px solid #f44336;
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 0.9rem;
        }

        .login-button {
          background: #4CAF50;
          color: white;
          border: none;
          padding: 14px 20px;
          border-radius: 8px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          margin-top: 10px;
        }

        .login-button:hover:not(:disabled) {
          background: #45a049;
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
        }

        .login-button:disabled {
          opacity: 0.7;
          cursor: not-allowed;
          transform: none;
        }

        .spinner {
          width: 16px;
          height: 16px;
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-top: 2px solid white;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          to {
            transform: rotate(360deg);
          }
        }

        .login-footer {
          margin-top: 30px;
          text-align: center;
        }

        .help-text p {
          color: #666;
          font-size: 0.85rem;
          margin: 8px 0;
        }

        .demo-info {
          background: #f0f8ff;
          padding: 12px;
          border-radius: 8px;
          border: 1px solid #e1f5fe;
          margin-top: 15px !important;
        }

        .demo-info strong {
          color: #2E7D32;
          background: rgba(76, 175, 80, 0.1);
          padding: 2px 6px;
          border-radius: 4px;
        }

        @media (max-width: 480px) {
          .login-card {
            padding: 30px 20px;
            margin: 10px;
          }
          
          .logo h1 {
            font-size: 1.5rem;
          }
        }
      `}</style>
    </div>
  );
};

export default Login;