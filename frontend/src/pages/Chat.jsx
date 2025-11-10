import React from 'react';
import ChatWidget from '../components/ChatWidget';

function Chat() {
  return (
    <div className="chat-page">
      <h1>Chat with Sakhi</h1>
      <p>Our AI farming assistant is here to help you with all your agricultural queries.</p>
      <ChatWidget />
      
      <style jsx>{`
        .chat-page {
          max-width: 800px;
          margin: 0 auto;
          padding: 2rem 1rem;
          text-align: center;
        }
        
        h1 {
          color: #2c3e50;
          margin-bottom: 1rem;
        }
        
        p {
          color: #555;
          margin-bottom: 2rem;
          font-size: 1.1rem;
        }
        
        @media (max-width: 768px) {
          .chat-page {
            padding: 1rem;
          }
          
          h1 {
            font-size: 1.75rem;
          }
        }
      `}</style>
    </div>
  );
}

export default Chat;
