import React from 'react';
import { Link } from 'react-router-dom';

function Dashboard() {
  const stats = [
    { title: 'Total Land Area', value: '12.5', unit: 'acres', trend: '↑ 2.5%', trendType: 'up' },
    { title: 'Current Yield', value: '42', unit: 'quintals', trend: '↑ 5.2%', trendType: 'up' },
    { title: 'Water Usage', value: '3.8', unit: 'ML', trend: '↓ 1.1%', trendType: 'down' },
    { title: 'Crop Health', value: '87', unit: '%', trend: '↑ 3.4%', trendType: 'up' }
  ];

  const activities = [
    { id: 1, type: 'irrigation', time: '2 hours ago', details: 'Irrigation completed in Field A' },
    { id: 2, type: 'fertilizer', time: '1 day ago', details: 'Fertilizer applied to Wheat crop' },
    { id: 3, type: 'pest', time: '2 days ago', details: 'Pest detected in Rice field' },
    { id: 4, type: 'harvest', time: '1 week ago', details: 'Harvest completed for Maize crop' }
  ];

  const quickActions = [
    { title: 'Pest Detection', icon: '🐛', path: '/pest-detection' },
    { title: 'Marketplace', icon: '🛒', path: '/marketplace' },
    { title: 'Ask Officer', icon: '👨‍🌾', path: '/ask-officer' },
    { title: 'Knowledge Hub', icon: '📚', path: '/knowledge-hub' }
  ];

  const getActivityIcon = (type) => {
    switch (type) {
      case 'irrigation':
        return '💧';
      case 'fertilizer':
        return '🌱';
      case 'pest':
        return '🐜';
      case 'harvest':
        return '🌾';
      default:
        return '📝';
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Welcome back, Rajesh!</h1>
        <p>Here's what's happening with your farm today</p>
      </div>

      <div className="stats-grid">
        {stats.map((stat, index) => (
          <div key={index} className="stat-card">
            <div className="stat-value">
              {stat.value} <span className="stat-unit">{stat.unit}</span>
            </div>
            <div className="stat-title">{stat.title}</div>
            <div className={`stat-trend ${stat.trendType}`}>
              {stat.trend}
            </div>
          </div>
        ))}
      </div>

      <div className="dashboard-content">
        <div className="recent-activity">
          <div className="section-header">
            <h2>Recent Activities</h2>
            <Link to="/activities" className="view-all">View All</Link>
          </div>
          <div className="activity-list">
            {activities.map(activity => (
              <div key={activity.id} className="activity-item">
                <div className="activity-icon">
                  {getActivityIcon(activity.type)}
                </div>
                <div className="activity-details">
                  <div className="activity-message">{activity.details}</div>
                  <div className="activity-time">{activity.time}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="quick-actions">
          <h2>Quick Actions</h2>
          <div className="actions-grid">
            {quickActions.map((action, index) => (
              <Link to={action.path} key={index} className="action-card">
                <div className="action-icon">{action.icon}</div>
                <div className="action-title">{action.title}</div>
              </Link>
            ))}
          </div>
        </div>
      </div>

      <div className="weather-forecast">
        <h2>Weather Forecast</h2>
        <div className="forecast-days">
          {['Today', 'Tue', 'Wed', 'Thu', 'Fri'].map((day, index) => (
            <div key={index} className="forecast-day">
              <div className="day-name">{day}</div>
              <div className="weather-icon">🌤️</div>
              <div className="temp">32°</div>
              <div className="rain-chance">10%</div>
            </div>
          ))}
        </div>
      </div>

      <style jsx>{`
        .dashboard {
          max-width: 1200px;
          margin: 0 auto;
          padding: 2rem 1rem;
        }
        
        .dashboard-header h1 {
          color: #2c3e50;
          margin-bottom: 0.5rem;
        }
        
        .dashboard-header p {
          color: #555;
          margin-bottom: 2rem;
          font-size: 1.1rem;
        }
        
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
          gap: 1.5rem;
          margin-bottom: 2rem;
        }
        
        .stat-card {
          background: white;
          border-radius: 10px;
          padding: 1.5rem;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
          position: relative;
          overflow: hidden;
        }
        
        .stat-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          width: 5px;
          height: 100%;
          background: #27ae60;
        }
        
        .stat-value {
          font-size: 2rem;
          font-weight: 600;
          color: #2c3e50;
          margin-bottom: 0.5rem;
        }
        
        .stat-unit {
          font-size: 1rem;
          color: #777;
          font-weight: normal;
        }
        
        .stat-title {
          color: #555;
          margin-bottom: 0.5rem;
        }
        
        .stat-trend {
          font-size: 0.9rem;
          font-weight: 500;
        }
        
        .stat-trend.up {
          color: #27ae60;
        }
        
        .stat-trend.down {
          color: #e74c3c;
        }
        
        .dashboard-content {
          display: grid;
          grid-template-columns: 1fr 350px;
          gap: 2rem;
          margin-bottom: 2rem;
        }
        
        .section-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
        }
        
        .section-header h2 {
          color: #2c3e50;
          margin: 0;
          font-size: 1.5rem;
        }
        
        .view-all {
          color: #27ae60;
          text-decoration: none;
          font-weight: 500;
        }
        
        .activity-list {
          background: white;
          border-radius: 10px;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
          overflow: hidden;
        }
        
        .activity-item {
          display: flex;
          padding: 1.25rem;
          border-bottom: 1px solid #eee;
          transition: background 0.2s;
        }
        
        .activity-item:last-child {
          border-bottom: none;
        }
        
        .activity-item:hover {
          background: #f9f9f9;
        }
        
        .activity-icon {
          font-size: 1.5rem;
          margin-right: 1rem;
          width: 40px;
          height: 40px;
          background: #f1f8e9;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .activity-message {
          color: #2c3e50;
          margin-bottom: 0.25rem;
        }
        
        .activity-time {
          color: #777;
          font-size: 0.85rem;
        }
        
        .quick-actions h2 {
          color: #2c3e50;
          margin-bottom: 1.5rem;
          font-size: 1.5rem;
        }
        
        .actions-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 1rem;
        }
        
        .action-card {
          background: white;
          border-radius: 10px;
          padding: 1.5rem 1rem;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
          text-align: center;
          text-decoration: none;
          color: inherit;
          transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .action-card:hover {
          transform: translateY(-3px);
          box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .action-icon {
          font-size: 2rem;
          margin-bottom: 0.75rem;
        }
        
        .action-title {
          color: #2c3e50;
          font-weight: 500;
        }
        
        .weather-forecast {
          background: white;
          border-radius: 10px;
          padding: 1.5rem;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }
        
        .weather-forecast h2 {
          color: #2c3e50;
          margin-top: 0;
          margin-bottom: 1.5rem;
          font-size: 1.5rem;
        }
        
        .forecast-days {
          display: flex;
          justify-content: space-between;
          text-align: center;
        }
        
        .forecast-day {
          flex: 1;
          padding: 0.5rem;
        }
        
        .day-name {
          font-weight: 500;
          margin-bottom: 0.5rem;
        }
        
        .weather-icon {
          font-size: 1.5rem;
          margin-bottom: 0.5rem;
        }
        
        .temp {
          font-weight: 600;
          margin-bottom: 0.25rem;
        }
        
        .rain-chance {
          font-size: 0.85rem;
          color: #3498db;
        }
        
        @media (max-width: 992px) {
          .dashboard-content {
            grid-template-columns: 1fr;
          }
          
          .stats-grid {
            grid-template-columns: repeat(2, 1fr);
          }
          
          .forecast-days {
            overflow-x: auto;
            padding-bottom: 1rem;
          }
          
          .forecast-day {
            min-width: 80px;
          }
        }
        
        @media (max-width: 576px) {
          .stats-grid {
            grid-template-columns: 1fr;
          }
          
          .actions-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
}

export default Dashboard;
