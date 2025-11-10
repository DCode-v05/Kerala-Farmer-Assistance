import React, { useState, useEffect } from 'react';

const TranslationWidget = ({ onTranslate, isVisible = true, position = 'topbar' }) => {
  const [showTranslateMenu, setShowTranslateMenu] = useState(false);
  const [currentLanguage, setCurrentLanguage] = useState(() => {
    return localStorage.getItem('preferred_language') || 'en';
  });
  const [isTranslating, setIsTranslating] = useState(false);

  const languages = [
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'ml', name: 'മലയാളം', flag: '🇮🇳' },
    { code: 'hi', name: 'हिंदी', flag: '🇮🇳' },
    { code: 'ta', name: 'தமിழ்', flag: '🇮🇳' }
  ];

  const handleLanguageChange = async (languageCode) => {
    if (languageCode === currentLanguage) {
      setShowTranslateMenu(false);
      return;
    }

    setIsTranslating(true);
    setCurrentLanguage(languageCode);
    
    try {
      // Store language preference
      localStorage.setItem('preferred_language', languageCode);
      
      if (languageCode === 'en') {
        // Restore original English content
        window.location.reload();
      } else {
        // Translate entire webpage content
        await translatePageContent(languageCode);
      }
      
      // Call the parent handler if provided
      if (onTranslate) {
        await onTranslate(languageCode);
      }
      
      // Show success message
      const message = languageCode === 'ml' ? 
        'ഭാഷ മാറ്റി' : 
        languageCode === 'hi' ? 
        'भाषा बदली गई' : 
        languageCode === 'ta' ? 
        'மொழி மாற்றப்பட்டது' : 
        'Language changed';
        
      // Use a brief toast instead of alert for better UX
      showToast(message);
      
    } catch (error) {
      console.error('Translation failed:', error);
      showToast('Translation service temporarily unavailable');
    } finally {
      setIsTranslating(false);
      setShowTranslateMenu(false);
    }
  };

  const translatePageContent = async (targetLanguage) => {
    // Get all text nodes that need translation
    const textNodes = getTextNodes(document.body);
    const textsToTranslate = textNodes
      .map(node => node.textContent.trim())
      .filter(text => text.length > 0 && !text.match(/^[0-9\s.,;:\-_!@#$%^&*()+={}[\]|\\/"'<>?~`]*$/));

    if (textsToTranslate.length === 0) return;

    try {
      // Batch translate texts
      const response = await fetch('http://localhost:5000/api/translate-batch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          texts: textsToTranslate,
          target_language: targetLanguage
        })
      });

      const data = await response.json();
      
      if (data.success && data.translations) {
        // Apply translations to the DOM
        let translationIndex = 0;
        textNodes.forEach(node => {
          const originalText = node.textContent.trim();
          if (originalText.length > 0 && !originalText.match(/^[0-9\s.,;:\-_!@#$%^&*()+={}[\]|\\/"'<>?~`]*$/)) {
            if (translationIndex < data.translations.length) {
              node.textContent = data.translations[translationIndex];
              translationIndex++;
            }
          }
        });
      }
    } catch (error) {
      console.error('Batch translation failed:', error);
      throw error;
    }
  };

  const getTextNodes = (element) => {
    const textNodes = [];
    const walker = document.createTreeWalker(
      element,
      NodeFilter.SHOW_TEXT,
      {
        acceptNode: (node) => {
          // Skip script, style, and other non-visible elements
          const parent = node.parentElement;
          if (!parent) return NodeFilter.FILTER_REJECT;
          
          const tagName = parent.tagName.toLowerCase();
          if (['script', 'style', 'noscript', 'meta', 'title'].includes(tagName)) {
            return NodeFilter.FILTER_REJECT;
          }
          
          // Skip empty or whitespace-only text nodes
          if (!node.textContent.trim()) {
            return NodeFilter.FILTER_REJECT;
          }
          
          return NodeFilter.FILTER_ACCEPT;
        }
      }
    );

    let node;
    while ((node = walker.nextNode())) {
      textNodes.push(node);
    }
    
    return textNodes;
  };

  const showToast = (message) => {
    // Create a simple toast notification
    const toast = document.createElement('div');
    toast.className = 'translation-toast';
    toast.textContent = message;
    toast.style.cssText = `
      position: fixed;
      top: 80px;
      right: 20px;
      background: #4CAF50;
      color: white;
      padding: 12px 20px;
      border-radius: 4px;
      z-index: 10000;
      font-size: 14px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
      animation: slideIn 0.3s ease-out;
    `;

    // Add animation styles
    const style = document.createElement('style');
    style.textContent = `
      @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
      }
      @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
      }
    `;
    if (!document.querySelector('#toast-styles')) {
      style.id = 'toast-styles';
      document.head.appendChild(style);
    }

    document.body.appendChild(toast);

    // Remove toast after 3 seconds
    setTimeout(() => {
      toast.style.animation = 'slideOut 0.3s ease-out';
      setTimeout(() => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast);
        }
      }, 300);
    }, 3000);
  };

  // Restore language preference on component mount
  useEffect(() => {
    const savedLanguage = localStorage.getItem('preferred_language');
    if (savedLanguage && savedLanguage !== 'en' && savedLanguage !== currentLanguage) {
      // Auto-translate if page was previously in a non-English language
      handleLanguageChange(savedLanguage);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run on mount

  const getCurrentLanguageInfo = () => {
    return languages.find(lang => lang.code === currentLanguage) || languages[0];
  };

  if (!isVisible) return null;

  return (
    <div className={`translation-widget ${position}`}>
      <button 
        className="translate-button"
        onClick={() => setShowTranslateMenu(!showTranslateMenu)}
        disabled={isTranslating}
        aria-label="Translation options"
      >
        <span className="translate-icon">🌐</span>
        <span className="translate-text">
          {isTranslating ? 'Translating...' : getCurrentLanguageInfo().flag}
        </span>
        <span className="dropdown-arrow">▼</span>
      </button>

      {showTranslateMenu && (
        <>
          <div className="translate-menu">
            <div className="menu-header">
              <span className="menu-title">Select Language</span>
            </div>
            <div className="language-options">
              {languages.map((language) => (
                <button
                  key={language.code}
                  className={`language-option ${currentLanguage === language.code ? 'active' : ''}`}
                  onClick={() => handleLanguageChange(language.code)}
                  disabled={isTranslating}
                >
                  <span className="language-flag">{language.flag}</span>
                  <span className="language-name">{language.name}</span>
                  {currentLanguage === language.code && (
                    <span className="checkmark">✓</span>
                  )}
                </button>
              ))}
            </div>
          </div>
          <div 
            className="translate-overlay" 
            onClick={() => setShowTranslateMenu(false)}
          />
        </>
      )}

      <style jsx>{`
        .translation-widget {
          position: relative;
          display: inline-block;
        }

        .translate-button {
          display: flex;
          align-items: center;
          gap: 6px;
          background: rgba(255, 255, 255, 0.15);
          border: 1px solid rgba(255, 255, 255, 0.3);
          border-radius: 20px;
          padding: 8px 12px;
          cursor: pointer;
          transition: all 0.2s;
          color: white;
          font-size: 0.85rem;
          font-weight: 500;
          min-width: 100px;
        }
        
        .translate-button:hover:not(:disabled) {
          background: rgba(255, 255, 255, 0.25);
          border-color: rgba(255, 255, 255, 0.5);
          transform: translateY(-1px);
        }

        .translate-button:disabled {
          opacity: 0.7;
          cursor: not-allowed;
          transform: none;
        }
        
        .translate-icon {
          font-size: 1rem;
        }
        
        .translate-text {
          font-size: 0.85rem;
        }

        .dropdown-arrow {
          font-size: 0.7rem;
          transition: transform 0.2s;
        }

        .translate-button[aria-expanded="true"] .dropdown-arrow {
          transform: rotate(180deg);
        }

        .translate-menu {
          position: absolute;
          top: calc(100% + 8px);
          right: 0;
          background: white;
          border-radius: 12px;
          box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
          border: 1px solid #e0e0e0;
          min-width: 200px;
          z-index: 1000;
          overflow: hidden;
          animation: slideDown 0.2s ease-out;
        }

        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .translate-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          z-index: 999;
        }

        .menu-header {
          padding: 12px 16px;
          border-bottom: 1px solid #f0f0f0;
          background: #f8f9fa;
        }

        .menu-title {
          font-size: 0.9rem;
          font-weight: 600;
          color: #333;
        }

        .language-options {
          padding: 8px 0;
        }

        .language-option {
          width: 100%;
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 10px 16px;
          background: none;
          border: none;
          cursor: pointer;
          transition: background-color 0.2s;
          font-size: 0.9rem;
        }

        .language-option:hover:not(:disabled) {
          background: #f0f8ff;
        }

        .language-option.active {
          background: #e3f2fd;
          color: #1976d2;
        }

        .language-option:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .language-flag {
          font-size: 1.2rem;
        }

        .language-name {
          flex: 1;
          text-align: left;
          font-weight: 500;
        }

        .checkmark {
          color: #4CAF50;
          font-weight: bold;
        }

        /* Position variants */
        .translation-widget.floating {
          position: fixed;
          bottom: 20px;
          right: 20px;
          z-index: 1000;
        }

        .translation-widget.floating .translate-button {
          background: #4CAF50;
          border-color: #4CAF50;
          box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
        }

        .translation-widget.floating .translate-button:hover:not(:disabled) {
          background: #45a049;
          border-color: #45a049;
        }

        @media (max-width: 768px) {
          .translate-menu {
            right: -50px;
            min-width: 180px;
          }
          
          .translate-button {
            font-size: 0.8rem;
            padding: 6px 10px;
            min-width: 80px;
          }
        }
      `}</style>
    </div>
  );
};

export default TranslationWidget;