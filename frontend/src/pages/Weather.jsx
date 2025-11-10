import React, { useState, useEffect } from 'react';
import '../styles/App.css';

const Weather = () => {
  const [currentWeather, setCurrentWeather] = useState(null);
  const [forecast, setForecast] = useState([]);
  const [advisory, setAdvisory] = useState(null);
  const [weatherAnalysis, setWeatherAnalysis] = useState(null);
  const [smartRecommendations, setSmartRecommendations] = useState(null);
  const [activitySuggestions, setActivitySuggestions] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('current');

  useEffect(() => {
    fetchWeatherData();
  }, []);

  const fetchWeatherData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch current weather with proper base URL
      const currentResponse = await fetch('http://localhost:5000/api/weather', {
        credentials: 'include'
      });
      const currentData = await currentResponse.json();
      
      // Fetch forecast
      const forecastResponse = await fetch('http://localhost:5000/api/weather/forecast', {
        credentials: 'include'
      });
      const forecastData = await forecastResponse.json();
      
      // Fetch advisory
      const advisoryResponse = await fetch('http://localhost:5000/api/weather/advisory', {
        credentials: 'include'
      });
      const advisoryData = await advisoryResponse.json();
      
      // Fetch enhanced weather analysis
      try {
        const analysisResponse = await fetch('http://localhost:5000/api/weather/analysis', {
          credentials: 'include'
        });
        const analysisData = await analysisResponse.json();
        if (analysisData.success) {
          setWeatherAnalysis(analysisData.analysis);
        }
      } catch (e) {
        console.log('Weather analysis not available:', e);
      }
      
      // Try to fetch smart recommendations (requires authentication)
      try {
        const smartRecResponse = await fetch('http://localhost:5000/api/weather/smart-recommendations', {
          credentials: 'include'
        });
        const smartRecData = await smartRecResponse.json();
        if (smartRecData.success) {
          setSmartRecommendations(smartRecData.smart_recommendations);
        }
      } catch (e) {
        console.log('Smart recommendations not available:', e);
      }
      
      // Try to fetch activity suggestions
      try {
        const activityResponse = await fetch('http://localhost:5000/api/weather/activity-suggestions', {
          credentials: 'include'
        });
        const activityData = await activityResponse.json();
        if (activityData.success) {
          setActivitySuggestions(activityData.activity_suggestions);
        }
      } catch (e) {
        console.log('Activity suggestions not available:', e);
      }
      
      if (currentData.success) {
        setCurrentWeather(currentData.weather);
      } else {
        console.error('Current weather failed:', currentData.error);
      }
      
      if (forecastData.success) {
        setForecast(forecastData.forecast?.forecast || []);
      } else {
        console.error('Forecast failed:', forecastData.error);
      }
      
      if (advisoryData.success) {
        setAdvisory(advisoryData.advisory);
      } else {
        console.error('Advisory failed:', advisoryData.error);
      }
      
      // Only set error if all main services fail
      if (!currentData.success && !forecastData.success && !advisoryData.success) {
        setError('Weather services are currently unavailable. Please check your connection and try again.');
      }
    } catch (error) {
      console.error('Weather fetch error:', error);
      setError('Unable to connect to weather service. Please check if the server is running.');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric'
    });
  };

  const getWeatherIcon = (condition) => {
    const iconMap = {
      'clear': '☀️',
      'sunny': '☀️',
      'partly cloudy': '⛅',
      'cloudy': '☁️',
      'overcast': '☁️',
      'rain': '🌧️',
      'rainy': '🌧️',
      'drizzle': '🌦️',
      'thunderstorm': '⛈️',
      'fog': '🌫️',
      'mist': '🌫️'
    };
    
    const lowerCondition = condition?.toLowerCase() || '';
    for (const key in iconMap) {
      if (lowerCondition.includes(key)) {
        return iconMap[key];
      }
    }
    return '🌤️'; // Default icon
  };

  if (loading) {
    return (
      <div className="weather-container">
        <div className="weather-header">
          <h1>Weather & Farming Advisory</h1>
          <div className="tabs">
            <button className="tab active">🌤️ Current</button>
            <button className="tab">📅 Forecast</button>
            <button className="tab">💡 Advisory</button>
            <button className="tab">📊 Analysis</button>
          </div>
        </div>
        
        <div className="weather-loading">
          <div className="loading-card">
            <div className="weather-loading-animation">
              <div className="cloud">
                <div className="cloud-part cloud-part-1"></div>
                <div className="cloud-part cloud-part-2"></div>
                <div className="cloud-part cloud-part-3"></div>
              </div>
              <div className="rain">
                <div className="raindrop"></div>
                <div className="raindrop"></div>
                <div className="raindrop"></div>
              </div>
            </div>
            <p>Fetching weather data for Kerala...</p>
            <div className="loading-progress">
              <div className="progress-bar"></div>
            </div>
          </div>
        </div>
        
        <style jsx>{`
          .weather-loading {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 400px;
            padding: 20px;
          }
          
          .loading-card {
            background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);
            padding: 40px;
            border-radius: 20px;
            text-align: center;
            color: white;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            max-width: 400px;
            width: 100%;
          }
          
          .weather-loading-animation {
            position: relative;
            margin-bottom: 20px;
            height: 80px;
          }
          
          .cloud {
            position: relative;
            width: 60px;
            height: 60px;
            margin: 0 auto;
          }
          
          .cloud-part {
            position: absolute;
            background: white;
            border-radius: 50%;
            opacity: 0.9;
          }
          
          .cloud-part-1 {
            width: 50px;
            height: 50px;
            top: 10px;
            left: 10px;
            animation: float 2s ease-in-out infinite;
          }
          
          .cloud-part-2 {
            width: 30px;
            height: 30px;
            top: 15px;
            left: 35px;
            animation: float 2s ease-in-out infinite 0.5s;
          }
          
          .cloud-part-3 {
            width: 25px;
            height: 25px;
            top: 25px;
            left: 0px;
            animation: float 2s ease-in-out infinite 1s;
          }
          
          .rain {
            position: absolute;
            top: 50px;
            left: 50%;
            transform: translateX(-50%);
          }
          
          .raindrop {
            width: 2px;
            height: 15px;
            background: #ffffff;
            margin: 0 3px;
            border-radius: 2px;
            opacity: 0.7;
            animation: rain 1s linear infinite;
            display: inline-block;
          }
          
          .raindrop:nth-child(2) {
            animation-delay: 0.3s;
          }
          
          .raindrop:nth-child(3) {
            animation-delay: 0.6s;
          }
          
          .loading-progress {
            margin-top: 20px;
            width: 100%;
            height: 4px;
            background: rgba(255,255,255,0.3);
            border-radius: 2px;
            overflow: hidden;
          }
          
          .progress-bar {
            height: 100%;
            background: white;
            border-radius: 2px;
            animation: progress 2s ease-in-out infinite;
          }
          
          @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
          }
          
          @keyframes rain {
            0% { transform: translateY(-10px); opacity: 0; }
            50% { opacity: 0.7; }
            100% { transform: translateY(15px); opacity: 0; }
          }
          
          @keyframes progress {
            0% { width: 0%; }
            50% { width: 70%; }
            100% { width: 100%; }
          }
          
          .loading-card p {
            font-size: 16px;
            margin: 0;
            font-weight: 500;
          }
        `}</style>
      </div>
    );
  }

  if (error) {
    return (
      <div className="weather-container">
        <div className="error">
          <p>⚠️ {error}</p>
          <button onClick={fetchWeatherData} className="retry-btn">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="weather-container">
      <h1>Weather & Farming Advisory</h1>
      
      {/* Tab Navigation */}
      <div className="weather-tabs">
        <button 
          className={activeTab === 'current' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('current')}
        >
          Current Weather
        </button>
        <button 
          className={activeTab === 'forecast' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('forecast')}
        >
          7-Day Forecast
        </button>
        <button 
          className={activeTab === 'advisory' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('advisory')}
        >
          Farming Advisory
        </button>
        <button 
          className={activeTab === 'analysis' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('analysis')}
        >
          Weather Analysis
        </button>
        {smartRecommendations && (
          <button 
            className={activeTab === 'recommendations' ? 'tab active' : 'tab'}
            onClick={() => setActiveTab('recommendations')}
          >
            Smart Recommendations
          </button>
        )}
        {activitySuggestions && (
          <button 
            className={activeTab === 'activities' ? 'tab active' : 'tab'}
            onClick={() => setActiveTab('activities')}
          >
            Activity Suggestions
          </button>
        )}
      </div>

      {/* Current Weather Tab */}
      {activeTab === 'current' && currentWeather && (
        <div className="weather-tab-content">
          <div className="current-weather-card">
            <div className="weather-header">
              <h2>Current Weather in Kerala</h2>
              <div className="weather-icon">
                {getWeatherIcon(currentWeather.climate_summary?.most_likely_climate)}
              </div>
            </div>
            
            <div className="weather-details">
              <div className="temperature">
                <span className="temp-value">{Math.round(currentWeather.temperature)}°C</span>
                <span className="condition">{currentWeather.climate_summary?.most_likely_climate || 'Moderate'}</span>
              </div>
              
              <div className="weather-stats">
                <div className="stat">
                  <span className="label">Humidity</span>
                  <span className="value">{currentWeather.humidity}%</span>
                </div>
                <div className="stat">
                  <span className="label">Rainfall</span>
                  <span className="value">{currentWeather.rainfall} mm</span>
                </div>
                {currentWeather.windspeed && (
                  <div className="stat">
                    <span className="label">Wind Speed</span>
                    <span className="value">{currentWeather.windspeed} km/h</span>
                  </div>
                )}
                <div className="stat">
                  <span className="label">Location</span>
                  <span className="value">{currentWeather.location || 'Kerala'}</span>
                </div>
              </div>
              
              {/* Climate Summary */}
              {currentWeather.climate_summary && (
                <div className="climate-summary">
                  <h3>Climate Probabilities</h3>
                  <div className="climate-bars">
                    <div className="climate-bar">
                      <span>☀️ Sunny: {currentWeather.climate_summary.sunny_probability}%</span>
                      <div className="bar">
                        <div className="fill sunny" style={{width: `${currentWeather.climate_summary.sunny_probability}%`}}></div>
                      </div>
                    </div>
                    <div className="climate-bar">
                      <span>🌧️ Rainy: {currentWeather.climate_summary.rainy_probability}%</span>
                      <div className="bar">
                        <div className="fill rainy" style={{width: `${currentWeather.climate_summary.rainy_probability}%`}}></div>
                      </div>
                    </div>
                    <div className="climate-bar">
                      <span>☁️ Cloudy: {currentWeather.climate_summary.cloudy_probability}%</span>
                      <div className="bar">
                        <div className="fill cloudy" style={{width: `${currentWeather.climate_summary.cloudy_probability}%`}}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Forecast Tab */}
      {activeTab === 'forecast' && forecast.length > 0 && (
        <div className="weather-tab-content">
          <div className="forecast-container">
            <h2>7-Day Weather Forecast</h2>
            <div className="forecast-grid">
              {forecast.map((day, index) => (
                <div key={index} className="forecast-card">
                  <div className="forecast-date">{formatDate(day.date)}</div>
                  <div className="forecast-icon">
                    {getWeatherIcon(day.climate_summary?.most_likely_climate)}
                  </div>
                  <div className="forecast-temp">
                    <span className="high">{Math.round(day.temp_max || day.temperature)}°</span>
                    <span className="low">{Math.round(day.temp_min || day.temperature - 5)}°</span>
                  </div>
                  <div className="forecast-condition">{day.climate_summary?.most_likely_climate || 'Moderate'}</div>
                  <div className="rain-chance">
                    🌧️ {day.rainfall}mm
                  </div>
                  <div className="humidity">
                    💧 {day.humidity}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Advisory Tab */}
      {activeTab === 'advisory' && advisory && (
        <div className="weather-tab-content">
          <div className="advisory-container">
            <h2>Farming Advisory</h2>
            
            {advisory.overall_advisory && (
              <div className="advisory-section">
                <h3>🌾 Overall Farming Advisory</h3>
                <p className="advisory-text">{advisory.overall_advisory}</p>
              </div>
            )}
            
            {advisory.irrigation_advice && (
              <div className="advisory-section">
                <h3>💧 Irrigation Recommendations</h3>
                <p className="advisory-text">{advisory.irrigation_advice}</p>
              </div>
            )}
            
            {advisory.pest_disease_alert && (
              <div className="advisory-section alert">
                <h3>⚠️ Pest & Disease Alert</h3>
                <p className="advisory-text">{advisory.pest_disease_alert}</p>
              </div>
            )}
            
            {advisory.harvesting_advice && (
              <div className="advisory-section">
                <h3>🚜 Harvesting Guidance</h3>
                <p className="advisory-text">{advisory.harvesting_advice}</p>
              </div>
            )}
            
            {advisory.general_tips && advisory.general_tips.length > 0 && (
              <div className="advisory-section">
                <h3>💡 General Tips</h3>
                <ul className="tips-list">
                  {advisory.general_tips.map((tip, index) => (
                    <li key={index}>{tip}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Weather Analysis Tab */}
      {activeTab === 'analysis' && weatherAnalysis && (
        <div className="weather-tab-content">
          <div className="analysis-container">
            <h2>🔍 Weather Analysis & Insights</h2>
            
            {weatherAnalysis.climate_insights && (
              <div className="analysis-section">
                <h3>📊 Climate Pattern Analysis</h3>
                <div className="insight-grid">
                  <div className="insight-card">
                    <span className="label">Weather Trend</span>
                    <span className="value trend">{weatherAnalysis.climate_insights.weather_trend}</span>
                  </div>
                  <div className="insight-card">
                    <span className="label">Risk Level</span>
                    <span className={`value risk ${weatherAnalysis.climate_insights.risk_assessment?.level}`}>
                      {weatherAnalysis.climate_insights.risk_assessment?.level}
                    </span>
                  </div>
                </div>
                
                {weatherAnalysis.climate_insights.key_patterns && (
                  <div className="patterns-list">
                    <h4>Key Patterns Observed:</h4>
                    <ul>
                      {weatherAnalysis.climate_insights.key_patterns.map((pattern, index) => (
                        <li key={index}>{pattern}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
            
            {weatherAnalysis.crop_recommendations && (
              <div className="analysis-section">
                <h3>🌱 Recommended Crops</h3>
                <div className="crop-grid">
                  {weatherAnalysis.crop_recommendations.map((crop, index) => (
                    <div key={index} className="crop-card">
                      <div className="crop-name">{crop.crop}</div>
                      <div className={`suitability ${crop.suitability}`}>{crop.suitability} suitability</div>
                      <div className="crop-reason">{crop.reason}</div>
                      <div className="planting-time">Plant: {crop.planting_time}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {weatherAnalysis.irrigation_schedule && (
              <div className="analysis-section">
                <h3>💧 Irrigation Schedule</h3>
                <div className="irrigation-info">
                  <p><strong>Strategy:</strong> {weatherAnalysis.irrigation_schedule.strategy}</p>
                  <div className="schedule-list">
                    <h4>7-Day Schedule:</h4>
                    {weatherAnalysis.irrigation_schedule.next_7_days?.map((day, index) => (
                      <div key={index} className="schedule-day">
                        <span className="date">{formatDate(day.date)}</span>
                        <span className={`need ${day.irrigation_need}`}>{day.irrigation_need} irrigation</span>
                        <span className="reason">{day.reason}</span>
                      </div>
                    ))}
                  </div>
                  {weatherAnalysis.irrigation_schedule.water_conservation_tips && (
                    <div className="conservation-tips">
                      <h4>Water Conservation Tips:</h4>
                      <ul>
                        {weatherAnalysis.irrigation_schedule.water_conservation_tips.map((tip, index) => (
                          <li key={index}>{tip}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {weatherAnalysis.pest_disease_alerts && weatherAnalysis.pest_disease_alerts.length > 0 && (
              <div className="analysis-section alert">
                <h3>⚠️ Pest & Disease Alerts</h3>
                <div className="alerts-grid">
                  {weatherAnalysis.pest_disease_alerts.map((alert, index) => (
                    <div key={index} className={`alert-card ${alert.risk_level}`}>
                      <div className="alert-type">{alert.type.toUpperCase()}</div>
                      <div className="pest-name">{alert.pest_disease}</div>
                      <div className="risk-level">Risk: {alert.risk_level}</div>
                      <div className="description">{alert.description}</div>
                      <div className="prevention">{alert.prevention}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Smart Recommendations Tab */}
      {activeTab === 'recommendations' && smartRecommendations && (
        <div className="weather-tab-content">
          <div className="recommendations-container">
            <h2>🤖 AI-Powered Smart Recommendations</h2>
            
            {smartRecommendations.priority_actions && (
              <div className="rec-section priority">
                <h3>🚨 Priority Actions</h3>
                <div className="actions-list">
                  {smartRecommendations.priority_actions.map((action, index) => (
                    <div key={index} className={`action-card ${action.urgency}`}>
                      <div className="action-urgency">{action.urgency.toUpperCase()}</div>
                      <div className="action-text">{action.action}</div>
                      <div className="action-reason">{action.reason}</div>
                      <div className="action-deadline">Deadline: {action.deadline}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {smartRecommendations.crop_management && (
              <div className="rec-section">
                <h3>🌾 Crop Management</h3>
                <div className="crop-management-grid">
                  {smartRecommendations.crop_management.map((crop, index) => (
                    <div key={index} className="crop-management-card">
                      <div className="crop-title">{crop.crop}</div>
                      <div className="weather-impact">{crop.weather_impact}</div>
                      <ul className="recommendations-list">
                        {crop.recommendations.map((rec, recIndex) => (
                          <li key={recIndex}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {smartRecommendations.market_timing && (
              <div className="rec-section">
                <h3>📈 Market Timing Advice</h3>
                <div className="market-advice">
                  <div className="advice-item">
                    <strong>Harvest:</strong> {smartRecommendations.market_timing.harvest_advice}
                  </div>
                  <div className="advice-item">
                    <strong>Storage:</strong> {smartRecommendations.market_timing.storage_tips}
                  </div>
                  <div className="advice-item">
                    <strong>Strategy:</strong> {smartRecommendations.market_timing.market_strategy}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Activity Suggestions Tab */}
      {activeTab === 'activities' && activitySuggestions && (
        <div className="weather-tab-content">
          <div className="activities-container">
            <h2>📅 7-Day Activity Planner</h2>
            
            {activitySuggestions.week_summary && (
              <div className="week-summary">
                <div className="summary-stats">
                  <div className="stat-item">
                    <span className="stat-value">{activitySuggestions.week_summary.total_suitable_days}</span>
                    <span className="stat-label">Excellent Days</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-value">{activitySuggestions.week_summary.challenging_days}</span>
                    <span className="stat-label">Challenging Days</span>
                  </div>
                </div>
                <div className="week-focus">
                  <strong>Weekly Focus:</strong> {activitySuggestions.week_summary.recommended_focus}
                </div>
              </div>
            )}
            
            {activitySuggestions.daily_activities && (
              <div className="daily-activities">
                {activitySuggestions.daily_activities.map((day, index) => (
                  <div key={index} className="day-card">
                    <div className="day-header">
                      <div className="day-info">
                        <span className="day-name">{day.day_name}</span>
                        <span className="day-date">{formatDate(day.date)}</span>
                      </div>
                      <div className={`suitability-badge ${day.weather_suitability}`}>
                        {day.weather_suitability}
                      </div>
                    </div>
                    
                    <div className="weather-summary">
                      <span>🌡️ {day.weather_summary.temperature}°C</span>
                      <span>💧 {day.weather_summary.humidity}%</span>
                      <span>🌧️ {day.weather_summary.rainfall}mm</span>
                      <span>☁️ {day.weather_summary.climate}</span>
                    </div>
                    
                    <div className="activities-timeline">
                      {day.activities.map((activity, actIndex) => (
                        <div key={actIndex} className={`activity-item ${activity.priority}`}>
                          <div className="activity-time">{activity.time}</div>
                          <div className="activity-details">
                            <div className="activity-name">{activity.activity}</div>
                            <div className="activity-reason">{activity.reason}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Refresh Button */}
      <div className="weather-actions">
        <button onClick={fetchWeatherData} className="refresh-btn">
          🔄 Refresh Weather Data
        </button>
        <p className="last-updated">
          Last updated: {new Date().toLocaleTimeString()}
        </p>
      </div>

      <style jsx>{`
        .weather-container {
          padding: 20px;
          max-width: 1200px;
          margin: 0 auto;
        }

        .weather-tabs {
          display: flex;
          margin-bottom: 20px;
          border-bottom: 2px solid #e1e5e9;
        }

        .tab {
          padding: 12px 24px;
          border: none;
          background: none;
          cursor: pointer;
          font-size: 16px;
          border-bottom: 3px solid transparent;
          transition: all 0.3s ease;
        }

        .tab.active {
          color: #4CAF50;
          border-bottom-color: #4CAF50;
          font-weight: 600;
        }

        .tab:hover {
          background-color: #f5f5f5;
        }

        .current-weather-card {
          background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);
          color: white;
          border-radius: 15px;
          padding: 30px;
          margin-bottom: 20px;
        }

        .weather-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .weather-icon {
          font-size: 60px;
        }

        .temperature {
          text-align: center;
          margin-bottom: 30px;
        }

        .temp-value {
          font-size: 72px;
          font-weight: 300;
          display: block;
        }

        .condition {
          font-size: 24px;
          opacity: 0.9;
          text-transform: capitalize;
        }

        .weather-stats {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 20px;
        }

        .stat {
          text-align: center;
          padding: 15px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 10px;
          backdrop-filter: blur(10px);
        }

        .stat .label {
          display: block;
          font-size: 14px;
          opacity: 0.8;
          margin-bottom: 5px;
        }

        .stat .value {
          font-size: 24px;
          font-weight: 600;
        }

        .forecast-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 15px;
          margin-top: 20px;
        }

        .forecast-card {
          background: white;
          border-radius: 12px;
          padding: 20px;
          text-align: center;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          transition: transform 0.3s ease;
        }

        .forecast-card:hover {
          transform: translateY(-2px);
        }

        .forecast-date {
          font-weight: 600;
          color: #333;
          margin-bottom: 10px;
        }

        .forecast-icon {
          font-size: 40px;
          margin: 10px 0;
        }

        .forecast-temp {
          margin: 10px 0;
        }

        .forecast-temp .high {
          font-size: 20px;
          font-weight: 600;
          color: #333;
          margin-right: 10px;
        }

        .forecast-temp .low {
          font-size: 16px;
          color: #666;
        }

        .forecast-condition {
          font-size: 14px;
          color: #666;
          text-transform: capitalize;
        }

        .rain-chance {
          margin-top: 8px;
          font-size: 12px;
          color: #2e7d32;
          font-weight: 600;
        }

        .advisory-container {
          background: white;
          border-radius: 12px;
          overflow: hidden;
        }

        .advisory-section {
          padding: 25px;
          border-bottom: 1px solid #e1e5e9;
        }

        .advisory-section:last-child {
          border-bottom: none;
        }

        .advisory-section.alert {
          background: #fff3cd;
          border-left: 4px solid #ffc107;
        }

        .advisory-section h3 {
          color: #333;
          margin-bottom: 15px;
          font-size: 18px;
        }

        .advisory-text {
          color: #555;
          line-height: 1.6;
          margin: 0;
        }

        .tips-list {
          margin: 0;
          padding-left: 20px;
        }

        .tips-list li {
          color: #555;
          line-height: 1.6;
          margin-bottom: 8px;
        }

        .weather-actions {
          text-align: center;
          margin-top: 30px;
          padding-top: 20px;
          border-top: 1px solid #e1e5e9;
        }

        .refresh-btn {
          background: #4CAF50;
          color: white;
          border: none;
          padding: 12px 24px;
          border-radius: 25px;
          cursor: pointer;
          font-size: 16px;
          transition: background 0.3s ease;
        }

        .refresh-btn:hover {
          background: #45a049;
        }

        .last-updated {
          margin-top: 10px;
          color: #666;
          font-size: 14px;
        }

        .loading, .error {
          text-align: center;
          padding: 50px;
        }

        .spinner {
          border: 4px solid #f3f3f3;
          border-top: 4px solid #4CAF50;
          border-radius: 50%;
          width: 40px;
          height: 40px;
          animation: spin 1s linear infinite;
          margin: 0 auto 20px;
        }

        .retry-btn {
          background: #f44336;
          color: white;
          border: none;
          padding: 10px 20px;
          border-radius: 5px;
          cursor: pointer;
          margin-top: 10px;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        /* Climate Summary Styles */
        .climate-summary {
          margin-top: 20px;
          padding: 15px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 10px;
        }
        
        .climate-summary h3 {
          margin-bottom: 15px;
          font-size: 16px;
        }
        
        .climate-bars {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        
        .climate-bar {
          display: flex;
          flex-direction: column;
          gap: 5px;
        }
        
        .bar {
          height: 6px;
          background: rgba(255, 255, 255, 0.2);
          border-radius: 3px;
          overflow: hidden;
        }
        
        .fill {
          height: 100%;
          transition: width 0.3s ease;
        }
        
        .fill.sunny { background: #FFD700; }
        .fill.rainy { background: #4A90E2; }
        .fill.cloudy { background: #95A5A6; }

        /* Analysis Tab Styles */
        .analysis-container, .recommendations-container, .activities-container {
          background: white;
          border-radius: 12px;
          overflow: hidden;
        }
        
        .analysis-section, .rec-section {
          padding: 25px;
          border-bottom: 1px solid #e1e5e9;
        }
        
        .analysis-section:last-child, .rec-section:last-child {
          border-bottom: none;
        }
        
        .insight-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 15px;
          margin-bottom: 20px;
        }
        
        .insight-card {
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 20px;
          background: #f8f9fa;
          border-radius: 8px;
        }
        
        .insight-card .label {
          font-size: 14px;
          color: #666;
          margin-bottom: 5px;
        }
        
        .insight-card .value {
          font-size: 18px;
          font-weight: 600;
          text-transform: capitalize;
        }
        
        .value.trend { color: #4CAF50; }
        .value.risk.low { color: #4CAF50; }
        .value.risk.medium { color: #FF9800; }
        .value.risk.high { color: #f44336; }
        
        .crop-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 15px;
        }
        
        .crop-card {
          padding: 20px;
          background: #f8f9fa;
          border-radius: 8px;
          border-left: 4px solid #4CAF50;
        }
        
        .crop-name {
          font-size: 18px;
          font-weight: 600;
          margin-bottom: 10px;
        }
        
        .suitability {
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 600;
          text-transform: uppercase;
          margin-bottom: 10px;
          display: inline-block;
        }
        
        .suitability.high { background: #d4edda; color: #155724; }
        .suitability.medium { background: #fff3cd; color: #856404; }
        .suitability.low { background: #f8d7da; color: #721c24; }
        
        .schedule-day {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 10px;
          background: #f8f9fa;
          margin-bottom: 5px;
          border-radius: 4px;
        }
        
        .need.none { color: #6c757d; }
        .need.light { color: #28a745; }
        .need.moderate { color: #ffc107; }
        .need.heavy { color: #dc3545; }
        
        .alerts-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 15px;
        }
        
        .alert-card {
          padding: 20px;
          border-radius: 8px;
          border-left: 4px solid;
        }
        
        .alert-card.low { border-color: #28a745; background: #d4edda; }
        .alert-card.medium { border-color: #ffc107; background: #fff3cd; }
        .alert-card.high { border-color: #dc3545; background: #f8d7da; }
        
        /* Smart Recommendations Styles */
        .actions-list {
          display: flex;
          flex-direction: column;
          gap: 15px;
        }
        
        .action-card {
          padding: 20px;
          border-radius: 8px;
          border-left: 4px solid;
        }
        
        .action-card.high { border-color: #dc3545; background: #f8d7da; }
        .action-card.medium { border-color: #ffc107; background: #fff3cd; }
        .action-card.low { border-color: #28a745; background: #d4edda; }
        
        .action-urgency {
          font-size: 12px;
          font-weight: 600;
          margin-bottom: 10px;
        }
        
        .action-text {
          font-size: 16px;
          font-weight: 600;
          margin-bottom: 10px;
        }
        
        /* Activity Suggestions Styles */
        .week-summary {
          background: #e3f2fd;
          padding: 20px;
          border-radius: 8px;
          margin-bottom: 20px;
        }
        
        .summary-stats {
          display: flex;
          justify-content: center;
          gap: 40px;
          margin-bottom: 15px;
        }
        
        .stat-item {
          text-align: center;
        }
        
        .stat-value {
          display: block;
          font-size: 24px;
          font-weight: 600;
          color: #1976d2;
        }
        
        .stat-label {
          font-size: 14px;
          color: #666;
        }
        
        .day-card {
          background: white;
          border-radius: 8px;
          margin-bottom: 20px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          overflow: hidden;
        }
        
        .day-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 15px 20px;
          background: #f8f9fa;
          border-bottom: 1px solid #e1e5e9;
        }
        
        .day-name {
          font-size: 18px;
          font-weight: 600;
        }
        
        .suitability-badge {
          padding: 4px 12px;
          border-radius: 20px;
          font-size: 12px;
          font-weight: 600;
          text-transform: uppercase;
        }
        
        .suitability-badge.excellent { background: #d4edda; color: #155724; }
        .suitability-badge.good { background: #fff3cd; color: #856404; }
        .suitability-badge.challenging { background: #f8d7da; color: #721c24; }
        
        .weather-summary {
          display: flex;
          justify-content: space-around;
          padding: 15px 20px;
          background: #f1f3f4;
          font-size: 14px;
        }
        
        .activities-timeline {
          padding: 20px;
        }
        
        .activity-item {
          display: flex;
          gap: 15px;
          padding: 15px;
          margin-bottom: 10px;
          border-radius: 6px;
          border-left: 4px solid;
        }
        
        .activity-item.high { border-color: #dc3545; background: #fff5f5; }
        .activity-item.medium { border-color: #ffc107; background: #fffbf0; }
        .activity-item.low { border-color: #28a745; background: #f0fff4; }
        
        .activity-time {
          font-weight: 600;
          color: #666;
          min-width: 120px;
        }
        
        .activity-name {
          font-weight: 600;
          margin-bottom: 5px;
        }
        
        .activity-reason {
          font-size: 14px;
          color: #666;
        }

        .humidity {
          margin-top: 4px;
          font-size: 12px;
          color: #2e7d32;
          font-weight: 600;
        }

        @media (max-width: 768px) {
          .weather-container {
            padding: 15px;
          }
          
          .temp-value {
            font-size: 48px;
          }
          
          .weather-stats {
            grid-template-columns: repeat(2, 1fr);
          }
          
          .forecast-grid {
            grid-template-columns: repeat(2, 1fr);
          }
          
          .insight-grid {
            grid-template-columns: 1fr;
          }
          
          .crop-grid {
            grid-template-columns: 1fr;
          }
          
          .summary-stats {
            flex-direction: column;
            gap: 20px;
          }
          
          .weather-tabs {
            flex-wrap: wrap;
          }
          
          .tab {
            flex: 1;
            min-width: 120px;
          }
        }
      `}</style>
    </div>
  );
};

export default Weather;
