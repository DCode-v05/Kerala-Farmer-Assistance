import React, { useState } from 'react';

function Future() {
  const [activeTab, setActiveTab] = useState('cropPrediction');
  const [predictionResult, setPredictionResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const cropData = [
    { name: 'Rice', suitability: 'High', profit: '₹45,000', risk: 'Low', season: 'Kharif' },
    { name: 'Wheat', suitability: 'Medium', profit: '₹38,000', risk: 'Medium', season: 'Rabi' },
    { name: 'Cotton', suitability: 'High', profit: '₹52,000', risk: 'High', season: 'Kharif' },
    { name: 'Soybean', suitability: 'Medium', profit: '₹41,000', risk: 'Medium', season: 'Kharif' },
    { name: 'Maize', suitability: 'High', profit: '₹48,000', risk: 'Low', season: 'Kharif' },
  ];

  const weatherForecast = [
    { day: 'Today', condition: 'Sunny', high: '32°', low: '24°', rain: '10%' },
    { day: 'Tue', condition: 'Partly Cloudy', high: '31°', low: '24°', rain: '20%' },
    { day: 'Wed', condition: 'Cloudy', high: '30°', low: '25°', rain: '40%' },
    { day: 'Thu', condition: 'Rain', high: '28°', low: '24°', rain: '70%' },
    { day: 'Fri', condition: 'Rain', high: '27°', low: '23°', rain: '80%' },
  ];

  const handlePredict = () => {
    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      setPredictionResult({
        recommendedCrop: 'Rice',
        confidence: '87%',
        reason: 'Optimal soil conditions and weather forecast for the next 3 months show ideal growing conditions for rice in your region.',
        expectedYield: '28-32 quintals/acre',
        marketDemand: 'High',
        priceTrend: 'Increasing',
        riskFactors: ['Moderate chance of pest infestation', 'Monitor water levels during dry spells']
      });
      setIsLoading(false);
    }, 2000);
  };

  return (
    <div className="future">
      <h1>Future Insights</h1>
      <p className="subtitle">Make informed decisions with predictive analytics and future planning tools</p>
      
      <div className="tabs">
        <button 
          className={activeTab === 'cropPrediction' ? 'active' : ''}
          onClick={() => setActiveTab('cropPrediction')}
        >
          Crop Prediction
        </button>
        <button 
          className={activeTab === 'weather' ? 'active' : ''}
          onClick={() => setActiveTab('weather')}
        >
          Weather Forecast
        </button>
        <button 
          className={activeTab === 'marketTrends' ? 'active' : ''}
          onClick={() => setActiveTab('marketTrends')}
        >
          Market Trends
        </button>
      </div>
      
      <div className="tab-content">
        {activeTab === 'cropPrediction' && (
          <div className="crop-prediction">
            <div className="prediction-card">
              <h3>Get Crop Recommendation</h3>
              <p>Enter your farm details to get AI-powered crop recommendations for the next season.</p>
              
              <div className="form-group">
                <label>Soil Type</label>
                <select>
                  <option value="">Select soil type</option>
                  <option value="clay">Clay</option>
                  <option value="loam">Loam</option>
                  <option value="sandy">Sandy</option>
                  <option value="silt">Silt</option>
                  <option value="black">Black (Regur)</option>
                  <option value="red">Red</option>
                </select>
              </div>
              
              <div className="form-group">
                <label>Region</label>
                <select>
                  <option value="">Select region</option>
                  <option value="north">North India</option>
                  <option value="south">South India</option>
                  <option value="east">East India</option>
                  <option value="west">West India</option>
                  <option value="northeast">Northeast</option>
                </select>
              </div>
              
              <div className="form-group">
                <label>Water Availability</label>
                <select>
                  <option value="">Select water availability</option>
                  <option value="high">High (Good irrigation facilities)</option>
                  <option value="medium">Medium (Limited irrigation)</option>
                  <option value="low">Low (Rain-fed)</option>
                </select>
              </div>
              
              <div className="form-group">
                <label>Season</label>
                <select>
                  <option value="kharif">Kharif (June-October)</option>
                  <option value="rabi">Rabi (October-March)</option>
                  <option value="zaid">Zaid (March-June)</option>
                </select>
              </div>
              
              <button 
                className="predict-button"
                onClick={handlePredict}
                disabled={isLoading}
              >
                {isLoading ? 'Analyzing...' : 'Get Recommendation'}
              </button>
              
              {isLoading && (
                <div className="loading">
                  <p>🌾 Analyzing your farm conditions...</p>
                </div>
              )}
              
              {predictionResult && !isLoading && (
                <div className="prediction-result">
                  <h4>🎯 Recommendation: {predictionResult.recommendedCrop}</h4>
                  <p><strong>Confidence:</strong> {predictionResult.confidence}</p>
                  <p><strong>Reason:</strong> {predictionResult.reason}</p>
                  <p><strong>Expected Yield:</strong> {predictionResult.expectedYield}</p>
                  <p><strong>Market Demand:</strong> {predictionResult.marketDemand}</p>
                  <p><strong>Price Trend:</strong> {predictionResult.priceTrend}</p>
                  <div>
                    <strong>Risk Factors:</strong>
                    <ul>
                      {predictionResult.riskFactors.map((factor, index) => (
                        <li key={index}>{factor}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
            
            <div className="prediction-card">
              <h3>Top Crop Recommendations for Your Region</h3>
              <div className="crop-recommendations">
                {cropData.map((crop, index) => (
                  <div key={index} className="crop-card">
                    <h4>{crop.name}</h4>
                    <div className="crop-info">
                      <div className="info-item">
                        <span>Suitability:</span>
                        <span className={`suitability ${crop.suitability.toLowerCase()}`}>
                          {crop.suitability}
                        </span>
                      </div>
                      <div className="info-item">
                        <span>Expected Profit:</span>
                        <span>{crop.profit}</span>
                      </div>
                      <div className="info-item">
                        <span>Risk Level:</span>
                        <span>{crop.risk}</span>
                      </div>
                      <div className="info-item">
                        <span>Season:</span>
                        <span>{crop.season}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'weather' && (
          <div className="weather-container">
            <h3>7-Day Weather Forecast</h3>
            <div className="weather-grid">
              {weatherForecast.map((day, index) => (
                <div key={index} className="weather-card">
                  <div className="day">{day.day}</div>
                  <div 
                    className={`weather-icon ${day.condition.toLowerCase().replace(' ', '-')}`}
                  >
                    {day.condition === 'Sunny' ? '☀️' : 
                     day.condition === 'Partly Cloudy' ? '⛅' : 
                     day.condition === 'Cloudy' ? '☁️' : '🌧️'}
                  </div>
                  <div className="condition">{day.condition}</div>
                  <div className="temp-range">
                    <span className="high">{day.high}</span>
                    <span className="low">{day.low}</span>
                  </div>
                  <div className="rain-chance">{day.rain}</div>
                </div>
              ))}
            </div>
            
            <div className="weather-summary">
              <h4>🌦️ Weekly Summary</h4>
              <p>Expect moderate rainfall this week with temperatures ranging from 23°-32°C. 
                 Thursday and Friday show higher chances of rain - perfect for recently planted crops. 
                 Consider postponing harvesting activities until the weekend.</p>
            </div>
          </div>
        )}
        
        {activeTab === 'marketTrends' && (
          <div className="trends-container">
            <h3>Market Price Trends</h3>
            <div className="trends-grid">
              <div className="trend-card">
                <h4>Rice</h4>
                <div className="price-trend">
                  <span className="trend-icon up">📈</span>
                  <span>₹2,150/quintal (+5.2%)</span>
                </div>
                <p>Strong demand, good export prospects</p>
              </div>
              
              <div className="trend-card">
                <h4>Wheat</h4>
                <div className="price-trend">
                  <span className="trend-icon stable">➡️</span>
                  <span>₹2,050/quintal (±0.8%)</span>
                </div>
                <p>Stable prices, steady market</p>
              </div>
              
              <div className="trend-card">
                <h4>Cotton</h4>
                <div className="price-trend">
                  <span className="trend-icon up">📈</span>
                  <span>₹6,800/quintal (+8.1%)</span>
                </div>
                <p>High global demand, favorable prices</p>
              </div>
              
              <div className="trend-card">
                <h4>Sugarcane</h4>
                <div className="price-trend">
                  <span className="trend-icon down">📉</span>
                  <span>₹340/quintal (-2.3%)</span>
                </div>
                <p>Oversupply concerns, prices declining</p>
              </div>
            </div>
            
            <div className="market-insights">
              <h4>💡 Market Insights</h4>
              <ul>
                <li>Cotton prices are expected to remain strong due to global supply constraints</li>
                <li>Rice export opportunities are driving up domestic prices</li>
                <li>Consider diversifying into cash crops for better returns</li>
                <li>Government MSP announcements expected next month</li>
              </ul>
            </div>
            
            <table className="price-table">
              <thead>
                <tr>
                  <th>Crop</th>
                  <th>Current Price (₹/quintal)</th>
                  <th>Last Week</th>
                  <th>Change</th>
                  <th>Trend</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Rice</td>
                  <td>₹2,150</td>
                  <td>₹2,040</td>
                  <td className="price-change positive">+5.4%</td>
                  <td>📈</td>
                </tr>
                <tr>
                  <td>Wheat</td>
                  <td>₹2,050</td>
                  <td>₹2,035</td>
                  <td className="price-change positive">+0.7%</td>
                  <td>➡️</td>
                </tr>
                <tr>
                  <td>Cotton</td>
                  <td>₹6,800</td>
                  <td>₹6,290</td>
                  <td className="price-change positive">+8.1%</td>
                  <td>📈</td>
                </tr>
                <tr>
                  <td>Sugarcane</td>
                  <td>₹340</td>
                  <td>₹348</td>
                  <td className="price-change negative">-2.3%</td>
                  <td>📉</td>
                </tr>
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default Future;