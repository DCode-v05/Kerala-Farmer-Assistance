import React, { useState, useRef } from 'react';

function PestDetection() {
  const [image, setImage] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const fileInputRef = useRef(null);

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImage(reader.result);
        setResult(null);
      };
      reader.readAsDataURL(file);
    }
  };

  const analyzeImage = async () => {
    if (!image) return;
    
    setIsAnalyzing(true);
    
    try {
      // Convert base64 image back to file for API call
      const response = await fetch(image);
      const blob = await response.blob();
      
      const formData = new FormData();
      formData.append('image', blob, 'plant_image.jpg');
      
      const apiResponse = await fetch('http://localhost:5000/api/detect-plant-disease', {
        method: 'POST',
        credentials: 'include',
        body: formData
      });
      
      const data = await apiResponse.json();
      
      if (data.success) {
        setResult({
          pest: data.results.primary_detection,
          allResults: data.results.all_results,
          recommendations: data.results.recommendations
        });
      } else {
        // Fallback to mock data if API fails
        const mockResults = [
          { name: 'Disease Detection Unavailable', confidence: 0, description: 'Unable to connect to disease detection service.' }
        ];
        
        setResult({
          pest: mockResults[0],
          allResults: mockResults,
          recommendations: [
            'Please check your internet connection',
            'Consult with local agricultural officer',
            'Take a clear photo in good lighting',
            'Try again later'
          ]
        });
      }
    } catch (error) {
      console.error('Plant disease detection error:', error);
      // Fallback to mock data
      const mockResults = [
        { name: 'Connection Error', confidence: 0, description: 'Unable to analyze image at this time.' }
      ];
      
      setResult({
        pest: mockResults[0],
        allResults: mockResults,
        recommendations: [
          'Check your internet connection',
          'Ensure you\'re logged in',
          'Try uploading a different image',
          'Contact support if problem persists'
        ]
      });
    }
    
    setIsAnalyzing(false);
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="pest-detection">
      <h1>Pest Detection</h1>
      <p className="subtitle">Upload an image to identify pests and get treatment recommendations</p>
      
      <div className="upload-section">
        <div 
          className={`upload-area ${!image ? 'empty' : ''}`}
          onClick={triggerFileInput}
        >
          {image ? (
            <img src={image} alt="Uploaded plant" className="preview-image" />
          ) : (
            <div className="upload-prompt">
              <div className="upload-icon">📷</div>
              <p>Click to upload an image of the affected plant</p>
              <p className="hint">Supported formats: JPG, PNG (Max 5MB)</p>
            </div>
          )}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleImageUpload}
            accept="image/*"
            style={{ display: 'none' }}
          />
        </div>
        
        <div className="action-buttons">
          <button 
            className="analyze-button"
            onClick={analyzeImage}
            disabled={!image || isAnalyzing}
          >
            {isAnalyzing ? 'Analyzing...' : 'Detect Pests'}
          </button>
          {image && (
            <button 
              className="clear-button"
              onClick={() => {
                setImage(null);
                setResult(null);
              }}
            >
              Clear
            </button>
          )}
        </div>
      </div>
      
      {isAnalyzing && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Analyzing your image for pests...</p>
        </div>
      )}
      
      {result && (
        <div className="results">
          <div className="main-result">
            <h2>Detected Pest: {result.pest.name}</h2>
            <div className="confidence">
              Confidence: {result.pest.confidence}%
              <div className="confidence-bar">
                <div 
                  className="confidence-level"
                  style={{ width: `${result.pest.confidence}%` }}
                ></div>
              </div>
            </div>
            <p className="pest-description">{result.pest.description}</p>
            
            <div className="recommendations">
              <h3>Recommended Actions</h3>
              <ul>
                {(result.recommendations || []).map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>
          </div>
          
          <div className="other-results">
            <h3>Other Possible Matches</h3>
            <div className="pest-list">
              {(result.allResults || []).slice(1).map((pest, index) => (
                <div key={index} className="pest-item">
                  <div className="pest-name">{pest.name}</div>
                  <div className="pest-confidence">
                    {pest.confidence}%
                    <div className="confidence-bar small">
                      <div 
                        className="confidence-level"
                        style={{ width: `${pest.confidence}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="prevention-tips">
            <h3>Prevention Tips</h3>
            <ul>
              <li>Regularly inspect plants for early signs of pests</li>
              <li>Maintain proper plant spacing for good air circulation</li>
              <li>Remove weeds that can harbor pests</li>
              <li>Use row covers to protect plants from flying insects</li>
              <li>Rotate crops to prevent pest buildup in soil</li>
            </ul>
          </div>
        </div>
      )}
      
      <style jsx>{`
        .pest-detection {
          max-width: 1000px;
          margin: 0 auto;
          padding: 2rem 1rem;
        }
        
        h1 {
          color: #2c3e50;
          margin-bottom: 0.5rem;
          text-align: center;
        }
        
        .subtitle {
          color: #555;
          text-align: center;
          margin-bottom: 2rem;
          font-size: 1.1rem;
        }
        
        .upload-section {
          margin-bottom: 2rem;
        }
        
        .upload-area {
          border: 2px dashed #ccc;
          border-radius: 10px;
          padding: 2rem;
          text-align: center;
          cursor: pointer;
          transition: all 0.3s;
          margin-bottom: 1.5rem;
          background: #f9f9f9;
          min-height: 300px;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .upload-area:hover {
          border-color: #27ae60;
          background: #f0f9f0;
        }
        
        .upload-area.empty {
          padding: 3rem 2rem;
        }
        
        .upload-prompt {
          color: #666;
        }
        
        .upload-icon {
          font-size: 3rem;
          margin-bottom: 1rem;
        }
        
        .hint {
          font-size: 0.9rem;
          color: #999;
          margin-top: 0.5rem;
        }
        
        .preview-image {
          max-width: 100%;
          max-height: 400px;
          border-radius: 8px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .action-buttons {
          display: flex;
          gap: 1rem;
          justify-content: center;
        }
        
        .analyze-button, .clear-button {
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 6px;
          font-size: 1rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }
        
        .analyze-button {
          background: #27ae60;
          color: white;
        }
        
        .analyze-button:hover:not(:disabled) {
          background: #219653;
        }
        
        .analyze-button:disabled {
          background: #a5d6a7;
          cursor: not-allowed;
        }
        
        .clear-button {
          background: #f1f1f1;
          color: #555;
        }
        
        .clear-button:hover {
          background: #e0e0e0;
        }
        
        .loading {
          text-align: center;
          padding: 2rem;
          color: #555;
        }
        
        .spinner {
          width: 40px;
          height: 40px;
          margin: 0 auto 1rem;
          border: 4px solid #f3f3f3;
          border-top: 4px solid #27ae60;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        .results {
          margin-top: 2rem;
          animation: fadeIn 0.5s ease-in;
        }
        
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        .main-result {
          background: white;
          border-radius: 10px;
          padding: 1.5rem;
          box-shadow: 0 2px 10px rgba(0,0,0,0.05);
          margin-bottom: 1.5rem;
        }
        
        .confidence {
          margin: 1rem 0;
          color: #555;
        }
        
        .confidence-bar {
          height: 8px;
          background: #eee;
          border-radius: 4px;
          margin-top: 0.5rem;
          overflow: hidden;
        }
        
        .confidence-level {
          height: 100%;
          background: #27ae60;
          border-radius: 4px;
        }
        
        .pest-description {
          color: #444;
          line-height: 1.6;
        }
        
        .recommendations {
          margin-top: 1.5rem;
          padding-top: 1.5rem;
          border-top: 1px solid #eee;
        }
        
        .recommendations h3 {
          color: #2c3e50;
          margin-bottom: 1rem;
          text-align: left;
        }
        
        .recommendations ul {
          padding-left: 1.25rem;
          margin: 0;
        }
        
        .recommendations li {
          margin-bottom: 0.5rem;
          color: #444;
        }
        
        .other-results {
          background: #f9f9f9;
          border-radius: 10px;
          padding: 1.5rem;
          margin-bottom: 1.5rem;
        }
        
        .other-results h3 {
          color: #2c3e50;
          margin-top: 0;
          margin-bottom: 1rem;
          text-align: left;
        }
        
        .pest-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        
        .pest-item {
          background: white;
          padding: 1rem;
          border-radius: 6px;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .pest-name {
          font-weight: 500;
          margin-bottom: 0.5rem;
        }
        
        .pest-confidence {
          font-size: 0.9rem;
          color: #666;
        }
        
        .confidence-bar.small {
          height: 4px;
          margin-top: 0.25rem;
        }
        
        .prevention-tips {
          background: #e8f5e9;
          border-radius: 10px;
          padding: 1.5rem;
        }
        
        .prevention-tips h3 {
          color: #2c3e50;
          margin-top: 0;
          margin-bottom: 1rem;
          text-align: left;
        }
        
        .prevention-tips ul {
          padding-left: 1.25rem;
          margin: 0;
        }
        
        .prevention-tips li {
          margin-bottom: 0.5rem;
          color: #2e7d32;
        }
        
        @media (max-width: 768px) {
          .upload-area {
            min-height: 250px;
            padding: 1.5rem;
          }
          
          .action-buttons {
            flex-direction: column;
          }
          
          .analyze-button, .clear-button {
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
}

export default PestDetection;
