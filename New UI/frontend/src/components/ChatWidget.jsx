import React, { useState, useRef, useEffect } from 'react';
import VoiceInput from './VoiceInput';

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { id: 1, text: 'Hello! I\'m Sakhi, your farming assistant. How can I help you today?', sender: 'ai', time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isProcessingVoice, setIsProcessingVoice] = useState(false);
  const messagesEndRef = useRef(null);
  const chatWindowRef = useRef(null);

  // Close chat when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (chatWindowRef.current && !chatWindowRef.current.contains(event.target)) {
        if (!event.target.closest('.chat-icon')) {
          setIsOpen(false);
        }
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    // Add user message
    const userMessage = { 
      id: messages.length + 1, 
      text: inputValue, 
      sender: 'user',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputValue;
    setInputValue('');

    // Call actual backend API
    try {
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          message: currentInput,
          language: 'en'
        })
      });

      const data = await response.json();
      
      const aiMessage = {
        id: messages.length + 2,
        text: data.success ? data.response.text : 'Sorry, I\'m having trouble responding right now. Please try again.',
        sender: 'ai',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Chat API error:', error);
      const errorMessage = {
        id: messages.length + 2,
        text: 'Sorry, I\'m having trouble connecting. Please check your connection and try again.',
        sender: 'ai',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleVoiceMessage = async (formData) => {
    setIsProcessingVoice(true);
    
    // Add a loading message
    const loadingMessage = {
      id: messages.length + 1,
      text: '🎤 വോയ്സ് മെസേജ് പ്രോസസ്സിംഗ് ചെയ്യുന്നു...',
      sender: 'system',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setMessages(prev => [...prev, loadingMessage]);

    try {
      // Call the complete voice pipeline
      const response = await fetch('http://localhost:5000/api/voice/complete-pipeline', {
        method: 'POST',
        credentials: 'include',
        body: formData
      });

      const data = await response.json();
      
      // Remove loading message
      setMessages(prev => prev.slice(0, -1));
      
      if (data.success) {
        // Add user's transcribed message
        const userMessage = {
          id: messages.length + 1,
          text: `🎤 "${data.farmer_input}"`,
          sender: 'user',
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        
        // Add AI response
        const aiMessage = {
          id: messages.length + 2,
          text: data.gemini_response,
          sender: 'ai',
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          hasAudio: data.audio_response,
          isVoiceResponse: true
        };
        
        setMessages(prev => [...prev, userMessage, aiMessage]);
        
        // If audio response is available, play it
        if (data.audio_response) {
          try {
            // Get the audio file
            const audioResponse = await fetch('http://localhost:5000/api/translate-text-to-speech', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              credentials: 'include',
              body: JSON.stringify({
                text: data.gemini_response
              })
            });
            
            if (audioResponse.ok) {
              const audioBlob = await audioResponse.blob();
              const audioUrl = URL.createObjectURL(audioBlob);
              const audio = new Audio(audioUrl);
              
              audio.onended = () => {
                URL.revokeObjectURL(audioUrl);
              };
              
              // Auto-play the response (if browser allows)
              audio.play().catch(e => {
                console.log('Auto-play blocked by browser:', e);
              });
            }
          } catch (audioError) {
            console.error('Error playing response audio:', audioError);
          }
        }
        
      } else {
        const errorMessage = {
          id: messages.length + 1,
          text: data.error || 'വോയ്സ് മെസേജ് പ്രോസസ്സിംഗിൽ പിശക്. വീണ്ടും ശ്രമിക്കുക.',
          sender: 'ai',
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        
        setMessages(prev => [...prev, errorMessage]);
      }
      
    } catch (error) {
      console.error('Voice message error:', error);
      
      // Remove loading message
      setMessages(prev => prev.slice(0, -1));
      
      const errorMessage = {
        id: messages.length + 1,
        text: 'വോയ്സ് മെസേജ് അയയ്ക്കുന്നതിൽ പിശക്. ഇന്റർനെറ്റ് കണക്ഷൻ പരിശോധിക്കുക.',
        sender: 'ai',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessingVoice(false);
    }
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  // Quick question suggestions
  const quickQuestions = [
    'How to prevent pests in rice fields?',
    'Best fertilizer for wheat crop',
    'How often to water vegetables?',
    'Organic farming techniques'
  ];

  return (
    <>
      {/* Floating Chat Icon */}
      <div className="chat-icon" onClick={toggleChat}>
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" 
                stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </div>

      {/* Chat Window */}
      <div ref={chatWindowRef} className={`chat-container ${isOpen ? 'open' : ''}`}>
        <div className="chat-header">
          <h3>Chat with Sakhi</h3>
          <button className="close-btn" onClick={toggleChat}>&times;</button>
        </div>
        
        <div className="chat-window">
          <div className="messages">
            {messages.map((message) => (
              <div key={message.id} className={`message ${message.sender}`}>
                <div className="message-content">
                  {message.text}
                </div>
                <div className="message-time">
                  {message.time}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
          
          {messages.length === 1 && (
            <div className="suggested-questions">
              <h4>Quick Questions:</h4>
              <div className="question-chips">
                {quickQuestions.map((question, index) => (
                  <button 
                    key={index}
                    onClick={() => setInputValue(question)}
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          )}
          
          {/* Voice Input Component */}
          <VoiceInput 
            onVoiceMessage={handleVoiceMessage} 
            isProcessing={isProcessingVoice} 
          />
          
          <form onSubmit={handleSendMessage} className="message-input">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Type your message..."
              required
            />
            <button type="submit">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22 2L11 13" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </form>
        </div>
      </div>

      <style jsx>{`
        /* Floating Chat Icon */
        .chat-icon {
          position: fixed;
          bottom: 30px;
          right: 30px;
          width: 60px;
          height: 60px;
          background: #27ae60;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
          z-index: 1000;
          transition: all 0.3s ease;
        }

        .chat-icon:hover {
          transform: scale(1.1);
          box-shadow: 0 6px 25px rgba(0, 0, 0, 0.25);
        }

        .chat-icon svg {
          width: 28px;
          height: 28px;
        }

        /* Chat Container */
        .chat-container {
          position: fixed;
          bottom: 100px;
          right: 30px;
          width: 350px;
          height: 500px;
          background: white;
          border-radius: 15px;
          box-shadow: 0 5px 30px rgba(0, 0, 0, 0.2);
          display: flex;
          flex-direction: column;
          overflow: hidden;
          transform: translateY(20px);
          opacity: 0;
          visibility: hidden;
          transition: all 0.3s ease;
          z-index: 999;
        }

        .chat-container.open {
          transform: translateY(0);
          opacity: 1;
          visibility: visible;
        }

        .chat-header {
          background: #27ae60;
          color: white;
          padding: 1rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .chat-header h3 {
          margin: 0;
          font-size: 1rem;
          font-weight: 500;
        }

        .close-btn {
          background: transparent;
          border: none;
          color: white;
          font-size: 1.5rem;
          cursor: pointer;
          padding: 0 0.5rem;
          line-height: 1;
        }

        /* Chat Window */
        .chat-window {
          flex: 1;
          display: flex;
          flex-direction: column;
          background: #f8f9fa;
        }

        /* Messages */
        .messages {
          flex: 1;
          overflow-y: auto;
          padding: 1rem;
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .message {
          max-width: 80%;
          animation: fadeIn 0.3s ease;
        }

        .message.user {
          margin-left: auto;
        }

        .message.ai {
          margin-right: auto;
        }

        .message-content {
          padding: 0.75rem 1rem;
          border-radius: 15px;
          display: inline-block;
          word-wrap: break-word;
          font-size: 0.9rem;
        }

        .user .message-content {
          background: #27ae60;
          color: white;
          border-bottom-right-radius: 5px;
        }

        .ai .message-content {
          background: #f1f1f1;
          color: #333;
          border-bottom-left-radius: 5px;
        }

        .message-time {
          font-size: 0.7rem;
          color: #888;
          margin-top: 0.25rem;
          text-align: right;
        }

        /* Message Input */
        .message-input {
          display: flex;
          padding: 0.75rem;
          border-top: 1px solid #eee;
          background: white;
        }

        .message-input input {
          flex: 1;
          padding: 0.75rem 1rem;
          border: 1px solid #ddd;
          border-radius: 25px;
          font-size: 0.9rem;
          margin-right: 0.5rem;
          outline: none;
        }

        .message-input button {
          background: #27ae60;
          color: white;
          border: none;
          width: 45px;
          height: 45px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: background 0.2s;
        }

        .message-input button:hover {
          background: #219653;
        }

        /* Suggested Questions */
        .suggested-questions {
          padding: 1rem;
          background: white;
          border-top: 1px solid #eee;
        }

        .suggested-questions h4 {
          margin: 0 0 0.75rem 0;
          font-size: 0.85rem;
          color: #555;
        }

        .question-chips {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }

        .question-chips button {
          background: #f0f0f0;
          border: none;
          border-radius: 15px;
          padding: 0.4rem 0.8rem;
          font-size: 0.8rem;
          color: #333;
          cursor: pointer;
          transition: all 0.2s;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          max-width: 100%;
        }

        .question-chips button:hover {
          background: #e0e0e0;
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 480px) {
          .chat-container {
            right: 15px;
            left: 15px;
            width: auto;
            height: 70vh;
            bottom: 20px;
          }
          
          .chat-icon {
            right: 20px;
            bottom: 20px;
          }
          
          .message {
            max-width: 90%;
          }
        }
      `}</style>
    </>
  );
};

export default ChatWidget;
