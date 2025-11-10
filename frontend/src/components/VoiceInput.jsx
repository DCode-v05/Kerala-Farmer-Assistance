import React, { useState, useRef, useEffect } from 'react';

const VoiceInput = ({ onVoiceMessage, isProcessing = false }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [isSupported, setIsSupported] = useState(true);
  
  const mediaRecorderRef = useRef(null);
  const audioRef = useRef(null);
  const intervalRef = useRef(null);
  const streamRef = useRef(null);

  useEffect(() => {
    // Check if browser supports required APIs
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setIsSupported(false);
    }
    
    return () => {
      // Cleanup on unmount
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 16000
        } 
      });
      
      streamRef.current = stream;
      
      // Create MediaRecorder with webm format for better compatibility
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      const audioChunks = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        const blob = new Blob(audioChunks, { type: 'audio/webm' });
        setAudioBlob(blob);
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      
      setIsRecording(true);
      setRecordingTime(0);
      
      // Start timer
      intervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('മൈക്രോഫോൺ ആക്സസ് ചെയ്യാൻ കഴിഞ്ഞില്ല. ബ്രൗസർ സെറ്റിംഗുകൾ പരിശോധിക്കുക.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    }
  };

  const sendVoiceMessage = async () => {
    if (!audioBlob) return;
    
    const formData = new FormData();
    formData.append('audio', audioBlob, 'voice_message.webm');
    
    try {
      // Call the complete voice pipeline
      await onVoiceMessage(formData);
      
      // Clear the recorded audio after sending
      setAudioBlob(null);
      setRecordingTime(0);
      
    } catch (error) {
      console.error('Error sending voice message:', error);
      alert('വോയ്സ് മെസേജ് അയയ്ക്കുന്നതിൽ പിശക്. വീണ്ടും ശ്രമിക്കുക.');
    }
  };

  const playRecordedAudio = () => {
    if (audioBlob) {
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      
      audio.onplay = () => setIsPlaying(true);
      audio.onended = () => {
        setIsPlaying(false);
        URL.revokeObjectURL(audioUrl);
      };
      
      audio.play();
    }
  };



  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!isSupported) {
    return (
      <div className="voice-input-container">
        <div className="voice-error">
          <p>വോയ്സ് റെക്കോർഡിംഗ് പിന്തുണയ്ക്കുന്നില്ല</p>
          <small>ആധുനിക ബ്രൗസർ ഉപയോഗിക്കുക</small>
        </div>
      </div>
    );
  }

  return (
    <div className="voice-input-container">
      <div className="voice-controls">
        {!isRecording ? (
          <button
            className="voice-button record-button"
            onClick={startRecording}
            disabled={isProcessing}
            title="വോയ്സ് റെക്കോർഡിംഗ് ആരംഭിക്കുക"
          >
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 1c-1.66 0-3 1.34-3 3v8c0 1.66 1.34 3 3 3s3-1.34 3-3V4c0-1.66-1.34-3-3-3zm0 16c-2.76 0-5-2.24-5-5v-1c0-.55-.45-1-1-1s-1 .45-1 1v1c0 3.53 2.61 6.43 6 6.92V21h-2c-.55 0-1 .45-1 1s.45 1 1 1h6c.55 0 1-.45 1-1s-.45-1-1-1h-2v-3.08c3.39-.49 6-3.39 6-6.92v-1c0-.55-.45-1-1-1s-1 .45-1 1v1c0 2.76-2.24 5-5 5z"/>
            </svg>
            {isProcessing ? 'പ്രോസസ്സിംഗ്...' : 'റെക്കോർഡ് ചെയ്യുക'}
          </button>
        ) : (
          <button
            className="voice-button stop-button"
            onClick={stopRecording}
            title="റെക്കോർഡിംഗ് നിർത്തുക"
          >
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M8 8h8v8H8V8z"/>
            </svg>
            {formatTime(recordingTime)}
          </button>
        )}

        {audioBlob && !isRecording && (
          <div className="recorded-controls">
            <button
              className="voice-button play-button"
              onClick={playRecordedAudio}
              disabled={isPlaying}
              title="റെക്കോർഡ് ചെയ്ത ഓഡിയോ പ്ലേ ചെയ്യുക"
            >
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z"/>
              </svg>
            </button>
            
            <button
              className="voice-button send-button"
              onClick={sendVoiceMessage}
              disabled={isProcessing}
              title="വോയ്സ് മെസേജ് അയയ്ക്കുക"
            >
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
              </svg>
              അയയ്ക്കുക
            </button>
          </div>
        )}
      </div>

      {/* Hidden audio element for playing responses */}
      <audio
        ref={audioRef}
        onPlay={() => setIsPlaying(true)}
        onEnded={() => setIsPlaying(false)}
        style={{ display: 'none' }}
      />

      <style jsx>{`
        .voice-input-container {
          margin: 10px 0;
          padding: 15px;
          background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%);
          border-radius: 12px;
          border: 1px solid #d4edda;
        }

        .voice-controls {
          display: flex;
          gap: 10px;
          align-items: center;
          flex-wrap: wrap;
        }

        .recorded-controls {
          display: flex;
          gap: 8px;
          align-items: center;
        }

        .voice-button {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 12px;
          border: none;
          border-radius: 20px;
          font-size: 12px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s ease;
          min-height: 36px;
        }

        .voice-button svg {
          width: 16px;
          height: 16px;
        }

        .record-button {
          background: #28a745;
          color: white;
        }

        .record-button:hover:not(:disabled) {
          background: #218838;
          transform: translateY(-1px);
        }

        .stop-button {
          background: #dc3545;
          color: white;
          animation: pulse 1.5s infinite;
        }

        .play-button {
          background: #007bff;
          color: white;
        }

        .play-button:hover:not(:disabled) {
          background: #0056b3;
        }

        .send-button {
          background: #6f42c1;
          color: white;
        }

        .send-button:hover:not(:disabled) {
          background: #5a32a3;
        }

        .voice-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
          transform: none;
        }

        .voice-error {
          text-align: center;
          color: #721c24;
          background: #f8d7da;
          padding: 15px;
          border-radius: 8px;
          border: 1px solid #f5c6cb;
        }

        .voice-error small {
          display: block;
          margin-top: 5px;
          font-size: 11px;
          opacity: 0.8;
        }

        @keyframes pulse {
          0% { transform: scale(1); }
          50% { transform: scale(1.05); }
          100% { transform: scale(1); }
        }

        @media (max-width: 480px) {
          .voice-controls {
            flex-direction: column;
            align-items: stretch;
          }
          
          .recorded-controls {
            justify-content: center;
          }
          
          .voice-button {
            justify-content: center;
          }
        }
      `}</style>
    </div>
  );
};

export default VoiceInput;