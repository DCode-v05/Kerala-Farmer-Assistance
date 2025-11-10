import React, { useState, useEffect } from 'react';
import './Market.css';

const Market = () => {
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCrop, setSelectedCrop] = useState('Rice');
  const [activeTab, setActiveTab] = useState('overview');
  const [location, setLocation] = useState('Kerala');

  // Kerala's main crops for dropdown
  const keralaCrops = [
    'Rice', 'Coconut', 'Pepper', 'Cardamom', 'Rubber', 'Tea', 'Coffee', 
    'Banana', 'Ginger', 'Turmeric', 'Arecanut', 'Cashew', 'Vanilla', 'Cinnamon'
  ];

  useEffect(() => {
    fetchMarketData();
  }, [selectedCrop, location]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchMarketData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch comprehensive market analysis
      const response = await fetch(
        `http://localhost:5000/api/market/analysis?crop=${selectedCrop}&location=${location}&days=7`,
        {
          credentials: 'include'
        }
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch market data');
      }
      
      const data = await response.json();
      
      if (data.success) {
        setMarketData(data.analysis);
      } else {
        throw new Error(data.error || 'Failed to load market analysis');
      }
    } catch (err) {
      console.error('Market data error:', err);
      setError(err.message);
      // Load mock data for demonstration
      setMarketData(getMockMarketData());
    } finally {
      setLoading(false);
    }
  };

  const getMockMarketData = () => ({
    crop: selectedCrop,
    location: location,
    current_prices: [
      { market: 'Kochi', modal_price: 2500, trend: 'rising' },
      { market: 'Thrissur', modal_price: 2480, trend: 'stable' },
      { market: 'Kozhikode', modal_price: 2520, trend: 'rising' }
    ],
    price_trends: {
      summary: {
        trend_direction: 'rising',
        change_percent: 5.2,
        current_price: 2500,
        average_price: 2480
      }
    },
    ai_advisory: {
      advisory_type: 'AI-Powered Market Analysis',
      confidence: 'high',
      current_situation: 'Market showing positive momentum with increased demand',
      price_analysis: {
        current_price_range: [2400, 2600],
        trend_assessment: 'rising',
        market_strength: 'strong'
      },
      selling_recommendations: {
        best_markets: ['Kochi', 'Kozhikode', 'Thrissur'],
        optimal_timing: 'Good time to sell - prices trending upward',
        quality_focus: 'Ensure premium quality for best prices'
      }
    },
    market_insights: {
      market_overview: {
        average_price: 2500,
        price_range: { min: 2400, max: 2600 },
        volatility_percentage: 8.5,
        market_activity: 'high'
      },
      trend_analysis: {
        direction: 'rising',
        change_percentage: 5.2,
        momentum: 'strong'
      }
    }
  });

  const renderOverview = () => (
    <div className="market-overview">
      <div className="price-summary">
        <div className="price-card main">
          <h3>Current Market Price</h3>
          <div className="price-value">
            ₹{marketData?.price_trends?.summary?.current_price?.toFixed(2) || 'N/A'}
            <span className="unit">/Quintal</span>
          </div>
          <div className={`trend ${marketData?.price_trends?.summary?.trend_direction || 'stable'}`}>
            {marketData?.price_trends?.summary?.change_percent > 0 ? '↗' : 
             marketData?.price_trends?.summary?.change_percent < 0 ? '↘' : '→'} 
            {Math.abs(marketData?.price_trends?.summary?.change_percent || 0).toFixed(1)}%
          </div>
        </div>
        
        <div className="price-card">
          <h4>Price Range</h4>
          <div className="range">
            ₹{marketData?.market_insights?.market_overview?.price_range?.min || 0} - 
            ₹{marketData?.market_insights?.market_overview?.price_range?.max || 0}
          </div>
        </div>
        
        <div className="price-card">
          <h4>Market Activity</h4>
          <div className={`activity ${marketData?.market_insights?.market_overview?.market_activity || 'moderate'}`}>
            {marketData?.market_insights?.market_overview?.market_activity || 'Moderate'}
          </div>
        </div>
        
        <div className="price-card">
          <h4>Volatility</h4>
          <div className="volatility">
            {marketData?.market_insights?.market_overview?.volatility_percentage?.toFixed(1) || 0}%
          </div>
        </div>
      </div>

      <div className="market-highlights">
        <h3>Market Highlights</h3>
        <div className="highlights-grid">
          <div className="highlight-item">
            <strong>Trend Direction:</strong> 
            <span className={`trend-badge ${marketData?.market_insights?.trend_analysis?.direction || 'stable'}`}>
              {marketData?.market_insights?.trend_analysis?.direction || 'Stable'}
            </span>
          </div>
          <div className="highlight-item">
            <strong>Market Strength:</strong> 
            <span className="strength-badge">
              {marketData?.ai_advisory?.price_analysis?.market_strength || 'Moderate'}
            </span>
          </div>
          <div className="highlight-item">
            <strong>Momentum:</strong> 
            <span className="momentum-badge">
              {marketData?.market_insights?.trend_analysis?.momentum || 'Moderate'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );

  const renderPrices = () => (
    <div className="current-prices">
      <h3>Current Market Prices - {selectedCrop}</h3>
      <div className="prices-table">
        <div className="table-header">
          <span>Market</span>
          <span>Price (₹/Quintal)</span>
          <span>Trend</span>
          <span>District</span>
        </div>
        {marketData?.current_prices?.map((price, index) => (
          <div key={index} className="table-row">
            <span className="market-name">{price.market}</span>
            <span className="price-value">₹{price.modal_price?.toFixed(2) || price.price}</span>
            <span className={`trend-indicator ${price.trend}`}>
              {price.trend === 'rising' ? '↗' : price.trend === 'falling' ? '↘' : '→'}
              {price.trend}
            </span>
            <span className="district">{price.district || location}</span>
          </div>
        ))}
      </div>
    </div>
  );

  const renderAnalysis = () => (
    <div className="ai-analysis">
      <div className="analysis-header">
        <h3>AI Market Analysis</h3>
        <div className="confidence-badge">
          Confidence: {marketData?.ai_advisory?.confidence || 'Medium'}
        </div>
      </div>
      
      <div className="analysis-content">
        <div className="situation-overview">
          <h4>Current Market Situation</h4>
          <p>{marketData?.ai_advisory?.current_situation || 
             'Market analysis indicates stable conditions with moderate trading activity.'}</p>
        </div>

        <div className="price-analysis">
          <h4>Price Analysis</h4>
          <div className="analysis-grid">
            <div className="analysis-item">
              <strong>Assessment:</strong>
              <span className={`assessment ${marketData?.ai_advisory?.price_analysis?.trend_assessment || 'stable'}`}>
                {marketData?.ai_advisory?.price_analysis?.trend_assessment || 'Stable'}
              </span>
            </div>
            <div className="analysis-item">
              <strong>Market Strength:</strong>
              <span>{marketData?.ai_advisory?.price_analysis?.market_strength || 'Moderate'}</span>
            </div>
            <div className="analysis-item">
              <strong>Price Range:</strong>
              <span>
                ₹{marketData?.ai_advisory?.price_analysis?.current_price_range?.[0] || 0} - 
                ₹{marketData?.ai_advisory?.price_analysis?.current_price_range?.[1] || 0}
              </span>
            </div>
          </div>
        </div>

        {marketData?.ai_advisory?.market_insights && (
          <div className="market-insights">
            <h4>Market Insights</h4>
            <div className="insights-content">
              {marketData.ai_advisory.market_insights.demand_factors && (
                <p><strong>Demand Factors:</strong> {marketData.ai_advisory.market_insights.demand_factors}</p>
              )}
              {marketData.ai_advisory.market_insights.supply_situation && (
                <p><strong>Supply Situation:</strong> {marketData.ai_advisory.market_insights.supply_situation}</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderRecommendations = () => (
    <div className="recommendations">
      <h3>Selling Recommendations</h3>
      
      <div className="recommendations-content">
        <div className="timing-advice">
          <h4>Optimal Timing</h4>
          <div className="advice-box">
            <p>{marketData?.ai_advisory?.selling_recommendations?.optimal_timing || 
               'Monitor market conditions and sell when prices are favorable.'}</p>
          </div>
        </div>

        <div className="best-markets">
          <h4>Recommended Markets</h4>
          <div className="markets-list">
            {marketData?.ai_advisory?.selling_recommendations?.best_markets?.map((market, index) => (
              <div key={index} className="market-recommendation">
                <span className="market-name">{market}</span>
                <span className="recommendation-reason">Top performing market</span>
              </div>
            )) || (
              <div className="market-recommendation">
                <span className="market-name">Local Markets</span>
                <span className="recommendation-reason">Check local market conditions</span>
              </div>
            )}
          </div>
        </div>

        <div className="quality-focus">
          <h4>Quality Guidelines</h4>
          <div className="guidelines">
            <p>{marketData?.ai_advisory?.selling_recommendations?.quality_focus || 
               'Ensure proper grading and quality standards for better prices.'}</p>
          </div>
        </div>

        {marketData?.ai_advisory?.actionable_advice && (
          <div className="actionable-advice">
            <h4>Action Items</h4>
            <div className="advice-sections">
              {marketData.ai_advisory.actionable_advice.immediate_actions && (
                <div className="advice-section">
                  <strong>Immediate Actions:</strong>
                  <ul>
                    {marketData.ai_advisory.actionable_advice.immediate_actions.map((action, index) => (
                      <li key={index}>{action}</li>
                    ))}
                  </ul>
                </div>
              )}
              {marketData.ai_advisory.actionable_advice.preparation_tips && (
                <div className="advice-section">
                  <strong>Preparation Tips:</strong>
                  <ul>
                    {marketData.ai_advisory.actionable_advice.preparation_tips.map((tip, index) => (
                      <li key={index}>{tip}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderTrends = () => (
    <div className="price-trends">
      <h3>Price Trends - Last 7 Days</h3>
      
      <div className="trends-summary">
        <div className="trend-card">
          <h4>Current Price</h4>
          <div className="trend-value">
            ₹{marketData?.price_trends?.summary?.current_price?.toFixed(2) || 'N/A'}
          </div>
        </div>
        
        <div className="trend-card">
          <h4>Average Price</h4>
          <div className="trend-value">
            ₹{marketData?.price_trends?.summary?.average_price?.toFixed(2) || 'N/A'}
          </div>
        </div>
        
        <div className="trend-card">
          <h4>Change</h4>
          <div className={`trend-value ${marketData?.price_trends?.summary?.change_percent >= 0 ? 'positive' : 'negative'}`}>
            {marketData?.price_trends?.summary?.change_percent >= 0 ? '+' : ''}
            {marketData?.price_trends?.summary?.change_percent?.toFixed(2) || 0}%
          </div>
        </div>
        
        <div className="trend-card">
          <h4>Direction</h4>
          <div className={`trend-direction ${marketData?.price_trends?.summary?.trend_direction || 'stable'}`}>
            {marketData?.price_trends?.summary?.trend_direction || 'Stable'}
          </div>
        </div>
      </div>

      {marketData?.price_trends?.trend_points && (
        <div className="trends-chart">
          <h4>Price Movement</h4>
          <div className="chart-container">
            <div className="simple-chart">
              {marketData.price_trends.trend_points.map((point, index) => (
                <div key={index} className="chart-point">
                  <div className="point-date">{point.date}</div>
                  <div className="point-price">₹{point.price}</div>
                  <div className="point-markets">{point.market_count} markets</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderAlerts = () => (
    <div className="market-alerts">
      <h3>Market Alerts & Opportunities</h3>
      
      <div className="alerts-content">
        {marketData?.market_insights?.market_opportunities?.map((opportunity, index) => (
          <div key={index} className={`alert-item ${opportunity.urgency || 'medium'}`}>
            <div className="alert-header">
              <span className="alert-type">{opportunity.type}</span>
              <span className={`urgency-badge ${opportunity.urgency}`}>{opportunity.urgency}</span>
            </div>
            <h4>{opportunity.title}</h4>
            <p>{opportunity.description}</p>
          </div>
        )) || (
          <div className="alert-item medium">
            <div className="alert-header">
              <span className="alert-type">market_update</span>
              <span className="urgency-badge medium">Medium</span>
            </div>
            <h4>Regular Market Monitoring</h4>
            <p>Continue monitoring market conditions for optimal selling opportunities.</p>
          </div>
        )}

        {marketData?.ai_advisory?.risk_assessment && (
          <div className="risk-assessment">
            <h4>Risk Assessment</h4>
            <div className="risk-content">
              <div className="risk-item">
                <strong>Volatility Risk:</strong> 
                <span className={`risk-level ${marketData.ai_advisory.risk_assessment.volatility_risk}`}>
                  {marketData.ai_advisory.risk_assessment.volatility_risk}
                </span>
              </div>
              {marketData.ai_advisory.risk_assessment.market_risks && (
                <div className="risk-item">
                  <strong>Market Risks:</strong>
                  <p>{marketData.ai_advisory.risk_assessment.market_risks}</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="market-container">
        <div className="market-header">
          <h1>Kerala Market Analysis</h1>
        </div>
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading market data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="market-container">
      <div className="market-header">
        <h1>Kerala Market Analysis</h1>
        <div className="market-controls">
          <select 
            value={selectedCrop} 
            onChange={(e) => setSelectedCrop(e.target.value)}
            className="crop-selector"
          >
            {keralaCrops.map(crop => (
              <option key={crop} value={crop}>{crop}</option>
            ))}
          </select>
          <select 
            value={location} 
            onChange={(e) => setLocation(e.target.value)}
            className="location-selector"
          >
            <option value="Kerala">Kerala</option>
            <option value="Kochi">Kochi</option>
            <option value="Thrissur">Thrissur</option>
            <option value="Kozhikode">Kozhikode</option>
          </select>
          <button onClick={fetchMarketData} className="refresh-btn">
            🔄 Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <p>⚠️ {error}</p>
          <p>Showing sample data for demonstration.</p>
        </div>
      )}

      <div className="market-tabs">
        <button 
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📊 Overview
        </button>
        <button 
          className={`tab ${activeTab === 'prices' ? 'active' : ''}`}
          onClick={() => setActiveTab('prices')}
        >
          💰 Current Prices
        </button>
        <button 
          className={`tab ${activeTab === 'analysis' ? 'active' : ''}`}
          onClick={() => setActiveTab('analysis')}
        >
          🤖 AI Analysis
        </button>
        <button 
          className={`tab ${activeTab === 'recommendations' ? 'active' : ''}`}
          onClick={() => setActiveTab('recommendations')}
        >
          💡 Recommendations
        </button>
        <button 
          className={`tab ${activeTab === 'trends' ? 'active' : ''}`}
          onClick={() => setActiveTab('trends')}
        >
          📈 Trends
        </button>
        <button 
          className={`tab ${activeTab === 'alerts' ? 'active' : ''}`}
          onClick={() => setActiveTab('alerts')}
        >
          🚨 Alerts
        </button>
      </div>

      <div className="market-content">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'prices' && renderPrices()}
        {activeTab === 'analysis' && renderAnalysis()}
        {activeTab === 'recommendations' && renderRecommendations()}
        {activeTab === 'trends' && renderTrends()}
        {activeTab === 'alerts' && renderAlerts()}
      </div>

      <div className="market-footer">
        <p>Data updated: {marketData?.analysis_timestamp ? new Date(marketData.analysis_timestamp).toLocaleString() : 'Just now'}</p>
        <p>Analysis powered by AI • Kerala Agricultural Market System</p>
      </div>
    </div>
  );
};

export default Market;