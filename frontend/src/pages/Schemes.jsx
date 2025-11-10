import React, { useState } from 'react';

function Schemes() {
  const [activeTab, setActiveTab] = useState('central');
  const [searchQuery, setSearchQuery] = useState('');
  
  const centralSchemes = [
    {
      id: 1,
      name: 'PM-KISAN',
      description: 'Income support of ₹6,000 per year to all farmer families across the country in three equal installments of ₹2,000 every four months.',
      eligibility: 'All farmer families, irrespective of the size of landholding',
      benefits: '₹6,000 per year in three installments',
      link: 'https://pmkisan.gov.in/',
      lastDate: 'Ongoing',
      category: 'central'
    },
    {
      id: 2,
      name: 'Pradhan Mantri Fasal Bima Yojana (PMFBY)',
      description: 'Comprehensive insurance coverage against crop failure, helping farmers cope with agricultural risks.',
      eligibility: 'All farmers including sharecroppers and tenant farmers',
      benefits: 'Premium as low as 2% for Kharif, 1.5% for Rabi, and 5% for commercial/horticultural crops',
      link: 'https://pmfby.gov.in/',
      lastDate: 'Varies by state and crop season',
      category: 'central'
    },
    {
      id: 3,
      name: 'Kisan Credit Card (KCC) Scheme',
      description: 'Provide farmers with timely access to credit for agricultural and other needs.',
      eligibility: 'Farmers, sharecroppers, oral lessees, and tenant farmers',
      benefits: 'Credit up to ₹3 lakh at 4% interest per annum',
      link: 'https://vikaspedia.in/agriculture/agri-insurance/kisan-credit-card',
      lastDate: 'Ongoing',
      category: 'central'
    }
  ];
  
  const stateSchemes = [
    {
      id: 4,
      name: 'Rythu Bandhu (Telangana)',
      description: 'Investment support scheme for farmers with direct benefit transfer of ₹5,000 per acre per season.',
      eligibility: 'All land-owning farmers in Telangana',
      benefits: '₹10,000 per year (₹5,000 per season)',
      link: 'https://rythubandhu.telangana.gov.in/',
      lastDate: 'Ongoing',
      category: 'state'
    },
    {
      id: 5,
      name: 'Krushak Assistance for Livelihood and Income Augmentation (KALIA) - Odisha',
      description: 'Support to cultivators and landless agricultural laborers.',
      eligibility: 'Small and marginal farmers, landless agricultural households, and vulnerable cultivators',
      benefits: '₹10,000 per family per year for cultivation and livelihood support',
      link: 'https://kalia.co.in/',
      lastDate: 'Ongoing',
      category: 'state'
    },
    {
      id: 6,
      name: 'Mukhyamantri Krishi Ashirwad Yojana (Jharkhand)',
      description: 'Financial assistance to farmers for agricultural inputs.',
      eligibility: 'Small and marginal farmers',
      benefits: '₹5,000 per year',
      link: 'https://jharkhand.gov.in/',
      lastDate: '31st December 2023',
      category: 'state'
    }
  ];
  
  const allSchemes = [...centralSchemes, ...stateSchemes];
  
  const filteredSchemes = allSchemes.filter(scheme => {
    const matchesSearch = scheme.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                         scheme.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesTab = activeTab === 'all' || scheme.category === activeTab;
    return matchesSearch && matchesTab;
  });

  return (
    <div className="schemes">
      <h1>Government Schemes</h1>
      <p className="subtitle">Explore various agricultural schemes and benefits for farmers</p>
      
      <div className="scheme-tabs">
        <button 
          className={`tab ${activeTab === 'all' ? 'active' : ''}`}
          onClick={() => setActiveTab('all')}
        >
          All Schemes
        </button>
        <button 
          className={`tab ${activeTab === 'central' ? 'active' : ''}`}
          onClick={() => setActiveTab('central')}
        >
          Central Government
        </button>
        <button 
          className={`tab ${activeTab === 'state' ? 'active' : ''}`}
          onClick={() => setActiveTab('state')}
        >
          State Government
        </button>
      </div>
      
      <div className="search-container">
        <input
          type="text"
          placeholder="Search schemes..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
        <button className="search-button">Search</button>
      </div>
      
      <div className="schemes-grid">
        {filteredSchemes.length > 0 ? (
          filteredSchemes.map(scheme => (
            <div key={scheme.id} className="scheme-card">
              <div className="scheme-header">
                <h3>{scheme.name}</h3>
                <span className={`scheme-tag ${scheme.category}`}>
                  {scheme.category === 'central' ? 'Central' : 'State'}
                </span>
              </div>
              <p className="scheme-description">{scheme.description}</p>
              
              <div className="scheme-details">
                <div className="detail-item">
                  <span className="detail-label">Eligibility:</span>
                  <span className="detail-value">{scheme.eligibility}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Benefits:</span>
                  <span className="detail-value">{scheme.benefits}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Last Date:</span>
                  <span className="detail-value">{scheme.lastDate}</span>
                </div>
              </div>
              
              <a 
                href={scheme.link} 
                target="_blank" 
                rel="noopener noreferrer"
                className="apply-button"
              >
                View Details & Apply
              </a>
            </div>
          ))
        ) : (
          <div className="no-results">
            <p>No schemes found matching your search criteria.</p>
          </div>
        )}
      </div>
      
      <div className="scheme-guidelines">
        <h2>How to Apply for Schemes</h2>
        <ol className="guidelines-list">
          <li>Check your eligibility for the scheme</li>
          <li>Gather required documents (Aadhaar, Land records, Bank details, etc.)</li>
          <li>Visit the official scheme website or nearest Common Service Center (CSC)</li>
          <li>Fill out the application form with accurate details</li>
          <li>Submit the form along with required documents</li>
          <li>Note down the application reference number for future tracking</li>
        </ol>
      </div>
      
      <div className="helpline">
        <h3>Need Help?</h3>
        <p>Call Kisan Call Center: <strong>1800-180-1551</strong> (Toll-Free)</p>
        <p>Email: <a href="mailto:kisan-ict@gov.in">kisan-ict@gov.in</a></p>
      </div>
      
      <style jsx>{`
        .schemes {
          max-width: 1200px;
          margin: 0 auto;
          padding: 2rem 1rem;
        }
        
        h1 {
          color: #2c3e50;
          text-align: center;
          margin-bottom: 0.5rem;
        }
        
        .subtitle {
          color: #555;
          text-align: center;
          margin-bottom: 2rem;
          font-size: 1.1rem;
        }
        
        .scheme-tabs {
          display: flex;
          justify-content: center;
          margin-bottom: 2rem;
          flex-wrap: wrap;
          gap: 0.5rem;
        }
        
        .tab {
          padding: 0.75rem 1.5rem;
          border: none;
          background: #f5f5f5;
          color: #555;
          border-radius: 30px;
          font-size: 1rem;
          cursor: pointer;
          transition: all 0.3s;
        }
        
        .tab:hover {
          background: #e0e0e0;
        }
        
        .tab.active {
          background: #27ae60;
          color: white;
        }
        
        .search-container {
          max-width: 600px;
          margin: 0 auto 2rem;
          display: flex;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          border-radius: 6px;
          overflow: hidden;
        }
        
        .search-input {
          flex: 1;
          padding: 0.75rem 1rem;
          border: 1px solid #ddd;
          border-right: none;
          font-size: 1rem;
          outline: none;
        }
        
        .search-button {
          background: #2c3e50;
          color: white;
          border: none;
          padding: 0 1.5rem;
          font-weight: 500;
          cursor: pointer;
          transition: background 0.2s;
        }
        
        .search-button:hover {
          background: #1a252f;
        }
        
        .schemes-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
          gap: 1.5rem;
          margin-bottom: 3rem;
        }
        
        .scheme-card {
          background: white;
          border-radius: 10px;
          overflow: hidden;
          box-shadow: 0 2px 10px rgba(0,0,0,0.05);
          transition: transform 0.3s, box-shadow 0.3s;
          display: flex;
          flex-direction: column;
        }
        
        .scheme-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        
        .scheme-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          padding: 1.5rem 1.5rem 0.5rem;
        }
        
        .scheme-header h3 {
          margin: 0;
          color: #2c3e50;
          font-size: 1.25rem;
        }
        
        .scheme-tag {
          font-size: 0.75rem;
          font-weight: 600;
          padding: 0.25rem 0.75rem;
          border-radius: 20px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        
        .scheme-tag.central {
          background: #e8f5e9;
          color: #2e7d32;
        }
        
        .scheme-tag.state {
          background: #e3f2fd;
          color: #1565c0;
        }
        
        .scheme-description {
          color: #444;
          line-height: 1.6;
          padding: 0 1.5rem 1rem;
          margin: 0;
          flex: 1;
        }
        
        .scheme-details {
          background: #f9f9f9;
          padding: 1.25rem 1.5rem;
          border-top: 1px solid #eee;
        }
        
        .detail-item {
          margin-bottom: 0.75rem;
          display: flex;
          gap: 0.5rem;
        }
        
        .detail-item:last-child {
          margin-bottom: 0;
        }
        
        .detail-label {
          font-weight: 600;
          color: #2c3e50;
          min-width: 80px;
        }
        
        .detail-value {
          color: #555;
          flex: 1;
        }
        
        .apply-button {
          display: block;
          text-align: center;
          background: #27ae60;
          color: white;
          text-decoration: none;
          padding: 0.75rem;
          font-weight: 500;
          transition: background 0.2s;
        }
        
        .apply-button:hover {
          background: #219653;
        }
        
        .no-results {
          grid-column: 1 / -1;
          text-align: center;
          padding: 3rem 1rem;
          color: #666;
          font-size: 1.1rem;
        }
        
        .scheme-guidelines {
          background: #f8f9fa;
          border-radius: 10px;
          padding: 2rem;
          margin: 3rem 0;
        }
        
        .scheme-guidelines h2 {
          color: #2c3e50;
          margin-top: 0;
          margin-bottom: 1.5rem;
          text-align: center;
        }
        
        .guidelines-list {
          max-width: 800px;
          margin: 0 auto;
          padding-left: 1.5rem;
        }
        
        .guidelines-list li {
          margin-bottom: 1rem;
          color: #444;
          line-height: 1.6;
        }
        
        .helpline {
          text-align: center;
          padding: 2rem;
          background: #e8f5e9;
          border-radius: 10px;
          margin-top: 2rem;
        }
        
        .helpline h3 {
          color: #2c3e50;
          margin-top: 0;
          margin-bottom: 1rem;
        }
        
        .helpline p {
          margin: 0.5rem 0;
          color: #2e7d32;
        }
        
        .helpline a {
          color: #27ae60;
          text-decoration: none;
          font-weight: 500;
        }
        
        .helpline a:hover {
          text-decoration: underline;
        }
        
        @media (max-width: 768px) {
          .schemes-grid {
            grid-template-columns: 1fr;
          }
          
          .search-container {
            flex-direction: column;
            box-shadow: none;
            gap: 0.5rem;
          }
          
          .search-input {
            border: 1px solid #ddd;
            border-radius: 6px;
          }
          
          .search-button {
            border-radius: 6px;
            padding: 0.75rem;
          }
          
          .detail-item {
            flex-direction: column;
            gap: 0.25rem;
          }
          
          .detail-label {
            min-width: auto;
          }
        }
      `}</style>
    </div>
  );
}

export default Schemes;
