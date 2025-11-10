import React, { useState } from 'react';

function AskOfficer() {
  const [question, setQuestion] = useState('');
  const [category, setCategory] = useState('Crop Management');
  const [contactPhone, setContactPhone] = useState('');
  const [contactEmail, setContactEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;
    
    setIsSubmitting(true);
    setError('');
    
    try {
      const response = await fetch('http://localhost:5000/api/officer/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          topic: category,
          question: question.trim(),
          contact_phone: contactPhone.trim() || null,
          contact_email: contactEmail.trim() || null
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setSubmitted(true);
        setQuestion('');
        setContactPhone('');
        setContactEmail('');
      } else {
        setError(data.error || 'Failed to submit question. Please try again.');
      }
    } catch (error) {
      console.error('Submit question error:', error);
      setError('Failed to submit question. Please check your connection and try again.');
    }
    
    setIsSubmitting(false);
  };

  return (
    <div className="ask-officer">
      <h1>Ask an Agricultural Officer</h1>
      <p>Get expert advice on farming practices, crop management, and more.</p>
      
      {submitted ? (
        <div className="success-message">
          <h3>Question Submitted Successfully!</h3>
          <p>Our agricultural officer will review your question and respond within 24-48 hours.</p>
          <button onClick={() => setSubmitted(false)}>Ask Another Question</button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="question-form">
          {error && (
            <div className="error-message">
              <p>{error}</p>
            </div>
          )}
          
          <div className="form-group">
            <label htmlFor="question">Your Question:</label>
            <textarea
              id="question"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Type your question here..."
              rows="6"
              required
              disabled={isSubmitting}
            ></textarea>
          </div>
          
          <div className="form-group">
            <label htmlFor="category">Category:</label>
            <select 
              id="category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              disabled={isSubmitting}
            >
              <option>Crop Management</option>
              <option>Pest Control</option>
              <option>Soil Health</option>
              <option>Irrigation</option>
              <option>Government Schemes</option>
              <option>Market Prices</option>
              <option>Other</option>
            </select>
          </div>
          
          <div className="form-group">
            <label htmlFor="contactPhone">Phone Number (Optional):</label>
            <input
              type="tel"
              id="contactPhone"
              value={contactPhone}
              onChange={(e) => setContactPhone(e.target.value)}
              placeholder="Your phone number for follow-up"
              disabled={isSubmitting}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="contactEmail">Email (Optional):</label>
            <input
              type="email"
              id="contactEmail"
              value={contactEmail}
              onChange={(e) => setContactEmail(e.target.value)}
              placeholder="Your email for follow-up"
              disabled={isSubmitting}
            />
          </div>
          
          <button type="submit" className="submit-btn" disabled={isSubmitting}>
            {isSubmitting ? 'Submitting...' : 'Submit Question'}
          </button>
        </form>
      )}
      
      <div className="faq-section">
        <h3>Frequently Asked Questions</h3>
        <div className="faq-list">
          <div className="faq-item">
            <h4>How often should I water my rice field?</h4>
            <p>Rice fields typically need to be kept flooded with 2-3 inches of water during the growing season. The exact frequency depends on your soil type and weather conditions.</p>
          </div>
          <div className="faq-item">
            <h4>What's the best time to plant wheat in my region?</h4>
            <p>Wheat is usually planted in October-November in most parts of India, but this can vary based on your specific location and climate conditions.</p>
          </div>
        </div>
      </div>
      
      <style jsx>{`
        .ask-officer {
          max-width: 800px;
          margin: 0 auto;
          padding: 2rem 1rem;
        }
        
        h1 {
          color: #2c3e50;
          margin-bottom: 0.5rem;
        }
        
        p {
          color: #555;
          margin-bottom: 2rem;
        }
        
        .question-form {
          background: white;
          padding: 2rem;
          border-radius: 8px;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
          margin-bottom: 2rem;
        }
        
        .form-group {
          margin-bottom: 1.5rem;
        }
        
        label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 500;
          color: #333;
        }
        
        textarea, select {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 1rem;
        }
        
        textarea {
          resize: vertical;
          min-height: 150px;
        }
        
        .submit-btn {
          background: #27ae60;
          color: white;
          border: none;
          padding: 0.75rem 1.5rem;
          border-radius: 4px;
          font-size: 1rem;
          cursor: pointer;
          transition: background 0.2s;
        }
        
        .submit-btn:hover {
          background: #219653;
        }
        
        .success-message {
          text-align: center;
          background: #e8f5e9;
          padding: 2rem;
          border-radius: 8px;
          margin-bottom: 2rem;
        }
        
        .success-message h3 {
          color: #2e7d32;
          margin-top: 0;
        }
        
        .success-message button {
          background: #2e7d32;
          color: white;
          border: none;
          padding: 0.5rem 1.5rem;
          border-radius: 4px;
          margin-top: 1rem;
          cursor: pointer;
        }
        
        .faq-section {
          background: #f9f9f9;
          padding: 2rem;
          border-radius: 8px;
        }
        
        .faq-section h3 {
          margin-top: 0;
          color: #2c3e50;
          border-bottom: 1px solid #eee;
          padding-bottom: 0.75rem;
          margin-bottom: 1.5rem;
        }
        
        .faq-item {
          margin-bottom: 1.5rem;
          padding-bottom: 1.5rem;
          border-bottom: 1px solid #eee;
        }
        
        .faq-item:last-child {
          border-bottom: none;
          margin-bottom: 0;
          padding-bottom: 0;
        }
        
        .faq-item h4 {
          color: #27ae60;
          margin: 0 0 0.5rem 0;
        }
        
        .faq-item p {
          margin: 0;
          color: #555;
          line-height: 1.6;
        }
      `}</style>
    </div>
  );
}

export default AskOfficer;
