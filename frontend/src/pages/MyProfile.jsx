import React, { useState, useEffect } from 'react';
import { useUser } from '../contexts/UserContext';

const MyProfile = () => {
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { user } = useUser();

  useEffect(() => {
    fetchProfileData();
  }, [user]);

  const fetchProfileData = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:5000/api/farmer/profile', {
        method: 'GET',
        credentials: 'include'
      });
      
      const data = await response.json();
      
      if (data.success) {
        setProfileData(data.profile);
      } else {
        setError(data.error || 'Failed to load profile');
      }
    } catch (err) {
      console.error('Profile fetch error:', err);
      setError('Unable to load profile data');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-IN');
  };

  if (loading) {
    return (
      <div className="profile-container">
        <div className="loading-state">
          <div className="profile-loading-animation">
            <div className="loading-avatar"></div>
            <div className="loading-text">Loading profile...</div>
          </div>
        </div>
        <style jsx>{`
          .profile-container {
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
          }
          
          .loading-state {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 400px;
          }
          
          .profile-loading-animation {
            text-align: center;
          }
          
          .loading-avatar {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: linear-gradient(90deg, #e0e0e0 25%, #f0f0f0 50%, #e0e0e0 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
            margin: 0 auto 20px;
          }
          
          .loading-text {
            color: #666;
            font-size: 16px;
          }
          
          @keyframes shimmer {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
          }
        `}</style>
      </div>
    );
  }

  if (error) {
    return (
      <div className="profile-container">
        <div className="error-state">
          <h2>⚠️ Profile Error</h2>
          <p>{error}</p>
          <button onClick={fetchProfileData} className="retry-btn">
            Retry Loading
          </button>
        </div>
        <style jsx>{`
          .error-state {
            text-align: center;
            padding: 40px;
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          }
          
          .retry-btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            margin-top: 15px;
          }
          
          .retry-btn:hover {
            background: #45a049;
          }
        `}</style>
      </div>
    );
  }

  if (!profileData) {
    return (
      <div className="profile-container">
        <div className="no-data">
          <h2>No Profile Data</h2>
          <p>Unable to load your farmer profile information.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <h1 className="profile-title">My Profile</h1>
      <p className="profile-subtitle">AIMS Farmer Registration Details</p>
      
      <div className="profile-grid">
        {/* Personal Information Card */}
        <div className="profile-card personal-info">
          <div className="card-header">
            <h2>👤 Personal Information</h2>
          </div>
          <div className="card-content">
            <div className="info-grid">
              <div className="info-item">
                <label>Full Name</label>
                <span>{profileData.name || 'N/A'}</span>
              </div>
              <div className="info-item">
                <label>Farmer ID</label>
                <span>{profileData.id || 'N/A'}</span>
              </div>
              <div className="info-item">
                <label>Kerala Farmer ID</label>
                <span>{profileData.kerala_farmer_id || 'N/A'}</span>
              </div>
              <div className="info-item">
                <label>Registration Number</label>
                <span>{profileData.registration_number || 'N/A'}</span>
              </div>
              <div className="info-item">
                <label>Gender</label>
                <span>{profileData.gender || 'N/A'}</span>
              </div>
              <div className="info-item">
                <label>Date of Birth</label>
                <span>{formatDate(profileData.dob)}</span>
              </div>
              <div className="info-item">
                <label>Category</label>
                <span>{profileData.category || 'N/A'}</span>
              </div>
              <div className="info-item">
                <label>Education Level</label>
                <span>{profileData.education_level || 'N/A'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Contact Information Card */}
        <div className="profile-card contact-info">
          <div className="card-header">
            <h2>📞 Contact Information</h2>
          </div>
          <div className="card-content">
            <div className="info-grid">
              <div className="info-item">
                <label>Mobile Number</label>
                <span>{profileData.mobile_no || 'N/A'}</span>
              </div>
              <div className="info-item">
                <label>Aadhaar Number</label>
                <span>{profileData.aadhaar_no ? `****-****-${profileData.aadhaar_no.slice(-4)}` : 'N/A'}</span>
              </div>
              <div className="info-item full-width">
                <label>Address</label>
                <span>{profileData.address || 'N/A'}</span>
              </div>
              <div className="info-item">
                <label>Post Office</label>
                <span>{profileData.post_office || 'N/A'}</span>
              </div>
              <div className="info-item">
                <label>PIN Code</label>
                <span>{profileData.pin_code || 'N/A'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Farm Information Card */}
        <div className="profile-card farm-info">
          <div className="card-header">
            <h2>🌾 Farm Information</h2>
          </div>
          <div className="card-content">
            <div className="info-grid">
              <div className="info-item">
                <label>Farm Area</label>
                <span>{profileData.area_acres ? `${profileData.area_acres} acres` : 'N/A'}</span>
              </div>
              <div className="info-item full-width">
                <label>Krishi Bhavan</label>
                <span>{profileData.farmhouse_krishibhavan || 'N/A'}</span>
              </div>
              <div className="info-item">
                <label>Marketing Interest</label>
                <span>{profileData.marketing_interest ? '✅ Yes' : '❌ No'}</span>
              </div>
              <div className="info-item">
                <label>Processing Interest</label>
                <span>{profileData.processing_interest ? '✅ Yes' : '❌ No'}</span>
              </div>
              <div className="info-item">
                <label>Latitude</label>
                <span>{profileData.lat || 'N/A'}</span>
              </div>
              <div className="info-item">
                <label>Longitude</label>
                <span>{profileData.lon || 'N/A'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Financial Information Card */}
        <div className="profile-card financial-info">
          <div className="card-header">
            <h2>💰 Financial Information</h2>
          </div>
          <div className="card-content">
            <div className="info-grid">
              <div className="info-item">
                <label>Bank Account</label>
                <span>{profileData.bank_account_no ? `****${profileData.bank_account_no.slice(-4)}` : 'N/A'}</span>
              </div>
              <div className="info-item">
                <label>IFSC Code</label>
                <span>{profileData.ifsc || 'N/A'}</span>
              </div>
              <div className="info-item">
                <label>Ration Card</label>
                <span>{profileData.ration_card_no || 'N/A'}</span>
              </div>
              <div className="info-item">
                <label>Registration Date</label>
                <span>{formatDate(profileData.created_at)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .profile-container {
          padding: 20px;
          max-width: 1200px;
          margin: 0 auto;
          background: #f5f5f5;
          min-height: 100vh;
        }

        .profile-title {
          color: #2e7d32;
          font-size: 2.5rem;
          font-weight: 700;
          margin-bottom: 8px;
          text-align: center;
        }

        .profile-subtitle {
          color: #666;
          font-size: 1.1rem;
          text-align: center;
          margin-bottom: 30px;
        }

        .profile-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
          gap: 20px;
          margin-top: 20px;
        }

        .profile-card {
          background: white;
          border-radius: 12px;
          box-shadow: 0 4px 15px rgba(0,0,0,0.1);
          overflow: hidden;
          transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .profile-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }

        .card-header {
          background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);
          color: white;
          padding: 20px;
        }

        .card-header h2 {
          margin: 0;
          font-size: 1.4rem;
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .card-content {
          padding: 25px;
        }

        .info-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
        }

        .info-item {
          display: flex;
          flex-direction: column;
        }

        .info-item.full-width {
          grid-column: 1 / -1;
        }

        .info-item label {
          font-weight: 600;
          color: #2e7d32;
          font-size: 0.9rem;
          margin-bottom: 5px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .info-item span {
          color: #333;
          font-size: 1rem;
          padding: 8px 12px;
          background: #f8f9fa;
          border-radius: 6px;
          border-left: 3px solid #4caf50;
        }

        @media (max-width: 768px) {
          .profile-container {
            padding: 15px;
          }

          .profile-grid {
            grid-template-columns: 1fr;
          }

          .info-grid {
            grid-template-columns: 1fr;
          }

          .profile-title {
            font-size: 2rem;
          }
        }
      `}</style>
    </div>
  );
};

export default MyProfile;