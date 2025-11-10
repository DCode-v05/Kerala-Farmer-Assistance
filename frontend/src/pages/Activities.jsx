import React, { useState, useEffect } from 'react';
import '../styles/App.css';

const Activities = () => {
  const [activities, setActivities] = useState([]);
  const [activitySuggestions, setActivitySuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newActivity, setNewActivity] = useState({
    activity_type: '',
    description: '',
    crop: '',
    field_location: '',
    notes: ''
  });

  useEffect(() => {
    loadActivitiesData();
  }, []);

  const loadActivitiesData = async () => {
    try {
      setLoading(true);

      // Load farmer's activities
      const activitiesResponse = await fetch('/api/activities');
      if (activitiesResponse.ok) {
        const activitiesData = await activitiesResponse.json();
        if (activitiesData.success) {
          setActivities(activitiesData.activities || []);
        }
      }

      // Load smart activity suggestions
      const suggestionsResponse = await fetch('/api/smart-activity-suggestions');
      if (suggestionsResponse.ok) {
        const suggestionsData = await suggestionsResponse.json();
        if (suggestionsData.success) {
          setActivitySuggestions(suggestionsData.suggestions || []);
        }
      }

    } catch (error) {
      console.error('Activities loading error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddActivity = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/activities', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newActivity),
      });

      const data = await response.json();
      if (data.success) {
        setNewActivity({
          activity_type: '',
          description: '',
          crop: '',
          field_location: '',
          notes: ''
        });
        setShowAddForm(false);
        loadActivitiesData(); // Reload activities
      } else {
        alert('Failed to add activity: ' + data.error);
      }
    } catch (error) {
      alert('Network error: Unable to add activity');
      console.error('Add activity error:', error);
    }
  };

  const getActivityIcon = (type) => {
    const icons = {
      'planting': '🌱',
      'irrigation': '💧',
      'fertilizer': '🌿',
      'pest_control': '🐛',
      'harvest': '🌾',
      'soil_preparation': '🚜',
      'weeding': '🌿',
      'pruning': '✂️',
      'spraying': '💨',
      'monitoring': '👁️'
    };
    return icons[type] || '📝';
  };

  const getPriorityColor = (priority) => {
    const colors = {
      'high': '#dc3545',
      'medium': '#ffc107',
      'low': '#28a745'
    };
    return colors[priority] || '#6c757d';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="activities-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading your farming activities...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="activities-container">
      <div className="activities-header">
        <h1>🚜 Smart Activity Management</h1>
        <p>Track your farming activities and get AI-powered suggestions</p>
        <button 
          className="add-activity-btn"
          onClick={() => setShowAddForm(!showAddForm)}
        >
          + Add Activity
        </button>
      </div>

      {/* Add Activity Form */}
      {showAddForm && (
        <div className="add-activity-form">
          <h3>Log New Activity</h3>
          <form onSubmit={handleAddActivity}>
            <div className="form-row">
              <div className="form-group">
                <label>Activity Type</label>
                <select
                  value={newActivity.activity_type}
                  onChange={(e) => setNewActivity({...newActivity, activity_type: e.target.value})}
                  required
                >
                  <option value="">Select Activity</option>
                  <option value="planting">Planting</option>
                  <option value="irrigation">Irrigation</option>
                  <option value="fertilizer">Fertilizing</option>
                  <option value="pest_control">Pest Control</option>
                  <option value="harvest">Harvesting</option>
                  <option value="soil_preparation">Soil Preparation</option>
                  <option value="weeding">Weeding</option>
                  <option value="pruning">Pruning</option>
                  <option value="spraying">Spraying</option>
                  <option value="monitoring">Field Monitoring</option>
                </select>
              </div>
              <div className="form-group">
                <label>Crop</label>
                <input
                  type="text"
                  value={newActivity.crop}
                  onChange={(e) => setNewActivity({...newActivity, crop: e.target.value})}
                  placeholder="e.g., Rice, Wheat"
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Description</label>
                <input
                  type="text"
                  value={newActivity.description}
                  onChange={(e) => setNewActivity({...newActivity, description: e.target.value})}
                  placeholder="Brief description of the activity"
                  required
                />
              </div>
              <div className="form-group">
                <label>Field Location</label>
                <input
                  type="text"
                  value={newActivity.field_location}
                  onChange={(e) => setNewActivity({...newActivity, field_location: e.target.value})}
                  placeholder="e.g., North Field, Plot A"
                />
              </div>
            </div>
            <div className="form-group">
              <label>Additional Notes</label>
              <textarea
                value={newActivity.notes}
                onChange={(e) => setNewActivity({...newActivity, notes: e.target.value})}
                placeholder="Any additional details..."
                rows="3"
              />
            </div>
            <div className="form-actions">
              <button type="submit" className="submit-btn">Log Activity</button>
              <button type="button" className="cancel-btn" onClick={() => setShowAddForm(false)}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* AI Activity Suggestions */}
      {activitySuggestions.length > 0 && (
        <div className="activity-suggestions">
          <div className="section-header">
            <h2>🤖 AI Activity Suggestions</h2>
            <p>Smart recommendations based on your farm conditions and weather</p>
          </div>
          <div className="suggestions-grid">
            {activitySuggestions.map((suggestion, index) => (
              <div key={index} className="suggestion-card">
                <div className="suggestion-header">
                  <span className="suggestion-icon">{getActivityIcon(suggestion.activity_type)}</span>
                  <div className="suggestion-priority" style={{backgroundColor: getPriorityColor(suggestion.priority)}}>
                    {suggestion.priority?.toUpperCase()}
                  </div>
                </div>
                <div className="suggestion-content">
                  <h4>{suggestion.title}</h4>
                  <p className="suggestion-description">{suggestion.description}</p>
                  {suggestion.weather_consideration && (
                    <p className="weather-note">
                      <span className="weather-icon">🌤️</span>
                      {suggestion.weather_consideration}
                    </p>
                  )}
                  {suggestion.estimated_duration && (
                    <p className="duration-note">
                      <span className="time-icon">⏱️</span>
                      Duration: {suggestion.estimated_duration}
                    </p>
                  )}
                  {suggestion.malayalam_description && (
                    <p className="malayalam-text">{suggestion.malayalam_description}</p>
                  )}
                </div>
                <div className="suggestion-actions">
                  <button 
                    className="accept-btn"
                    onClick={() => {
                      setNewActivity({
                        activity_type: suggestion.activity_type,
                        description: suggestion.title,
                        crop: suggestion.recommended_crop || '',
                        field_location: '',
                        notes: suggestion.description
                      });
                      setShowAddForm(true);
                    }}
                  >
                    Log This Activity
                  </button>
                  <button className="skip-btn">Skip</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Activities */}
      <div className="recent-activities">
        <div className="section-header">
          <h2>📋 Recent Activities</h2>
          <p>Your farming activity history</p>
        </div>
        
        {activities.length === 0 ? (
          <div className="no-activities">
            <h3>No Activities Logged Yet</h3>
            <p>Start logging your farming activities to get personalized insights and suggestions.</p>
            <button className="start-logging-btn" onClick={() => setShowAddForm(true)}>
              Log Your First Activity
            </button>
          </div>
        ) : (
          <div className="activities-timeline">
            {activities.map((activity, index) => (
              <div key={index} className="activity-item">
                <div className="activity-icon-wrapper">
                  <span className="activity-icon">{getActivityIcon(activity.activity_type)}</span>
                </div>
                <div className="activity-content">
                  <div className="activity-header">
                    <h4>{activity.description || activity.activity_type}</h4>
                    <span className="activity-date">{formatDate(activity.created_at)}</span>
                  </div>
                  <div className="activity-details">
                    {activity.crop && (
                      <span className="activity-tag">🌾 {activity.crop}</span>
                    )}
                    {activity.field_location && (
                      <span className="activity-tag">📍 {activity.field_location}</span>
                    )}
                    {activity.activity_type && (
                      <span className="activity-tag">📋 {activity.activity_type}</span>
                    )}
                  </div>
                  {activity.notes && (
                    <p className="activity-notes">{activity.notes}</p>
                  )}
                  {activity.weather_at_time && (
                    <p className="weather-info">
                      <span className="weather-icon">🌤️</span>
                      Weather: {activity.weather_at_time.condition}, {activity.weather_at_time.temperature}°C
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Activity Analytics */}
      <div className="activity-analytics">
        <h2>📊 Activity Insights</h2>
        <div className="analytics-grid">
          <div className="analytics-card">
            <h4>Total Activities</h4>
            <div className="analytics-value">{activities.length}</div>
            <p>Activities logged this month</p>
          </div>
          <div className="analytics-card">
            <h4>Most Common Activity</h4>
            <div className="analytics-value">
              {activities.length > 0 ? 
                getActivityIcon(
                  activities.reduce((prev, current) => 
                    activities.filter(a => a.activity_type === current.activity_type).length > 
                    activities.filter(a => a.activity_type === prev.activity_type).length ? current : prev
                  ).activity_type
                ) : '📝'
              }
            </div>
            <p>Primary farming activity</p>
          </div>
          <div className="analytics-card">
            <h4>Active Crops</h4>
            <div className="analytics-value">
              {new Set(activities.filter(a => a.crop).map(a => a.crop)).size || 'N/A'}
            </div>
            <p>Different crops managed</p>
          </div>
          <div className="analytics-card">
            <h4>AI Suggestions</h4>
            <div className="analytics-value">{activitySuggestions.length}</div>
            <p>Smart recommendations available</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Activities;