/**
 * @author Huy Le (hl9082)
 * @brief This component is the main application component. It handles the UI
 *        and the communication with the backend services for transcription.
 * @importance It is of high importance as it is the root component of the application.
 */
import React, { useState, useEffect } from 'react';

// Define the base URL of the backend API
const API_BASE_URL = 'http://127.0.0.1:8000';

const App: React.FC = () => {
  const [aslSubtitle, setAslSubtitle] = useState<string>('ASL service is off.');
  const [speechSubtitle, setSpeechSubtitle] = useState<string>('Speech service is off.');
  const [activeService, setActiveService] = useState<'asl' | 'speech' | 'none'>('none');

  useEffect(() => {
    // Establish a connection to the backend's SSE stream
    const eventSource = new EventSource(`${API_BASE_URL}/stream`);

    // Handle incoming messages from the stream
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.service === 'asl') {
          setAslSubtitle(data.text);
        } else if (data.service === 'speech') {
          setSpeechSubtitle(data.text);
        }
      } catch (error) {
        console.error('Failed to parse SSE message:', error);
      }
    };

    // Handle any errors with the connection
    eventSource.onerror = (error) => {
      console.error('EventSource failed:', error);
      setAslSubtitle('Connection to server lost.');
      setSpeechSubtitle('Connection to server lost.');
      eventSource.close();
    };

    // Clean up the connection when the component unmounts
    return () => {
      eventSource.close();
    };
  }, []); // The empty dependency array ensures this effect runs only once

  const handleServiceClick = async (service: 'asl' | 'speech') => {
    try {
      // If the clicked service is already active, stop it. Otherwise, start the new one.
      if (activeService === service) {
        await fetch(`${API_BASE_URL}/stop`);
        setActiveService('none');
      } else {
        await fetch(`${API_BASE_URL}/start/${service}`);
        setActiveService(service);
      }
    } catch (error) {
      console.error(`Failed to toggle service ${service}:`, error);
      setAslSubtitle('Failed to communicate with server.');
      setSpeechSubtitle('Failed to communicate with server.');
    }
  };

  return (
    <div style={{ textAlign: 'center', fontFamily: 'sans-serif', color: '#333' }}>
      <header style={{ backgroundColor: '#f4f4f4', padding: '20px', borderBottom: '1px solid #ddd' }}>
        <h1>Real-Time Subtitles</h1>
      </header>
      <main style={{ margin: '40px auto', maxWidth: '800px' }}>
        <div style={{ marginBottom: '40px' }}>
          <button
            onClick={() => handleServiceClick('asl')}
            style={getButtonStyle(activeService === 'asl')}
          >
            {activeService === 'asl' ? 'Stop ASL-to-Subtitle' : 'Start ASL-to-Subtitle'}
          </button>
          <button
            onClick={() => handleServiceClick('speech')}
            style={getButtonStyle(activeService === 'speech')}
          >
            {activeService === 'speech' ? 'Stop Speech-to-Subtitle' : 'Start Speech-to-Subtitle'}
          </button>
        </div>
        <div style={subtitleContainerStyle}>
          <div style={subtitleBoxStyle}>
            <h2>ASL Subtitles</h2>
            <p style={subtitleTextStyle}>{aslSubtitle}</p>
          </div>
          <div style={subtitleBoxStyle}>
            <h2>Speech Subtitles</h2>
            <p style={subtitleTextStyle}>{speechSubtitle}</p>
          </div>
        </div>
      </main>
    </div>
  );
};

// --- Styling ---

const getButtonStyle = (isActive: boolean): React.CSSProperties => ({
  margin: '0 10px',
  padding: '12px 25px',
  fontSize: '16px',
  cursor: 'pointer',
  border: '2px solid',
  borderColor: isActive ? '#d9534f' : '#5cb85c',
  backgroundColor: isActive ? '#d9534f' : '#5cb85c',
  color: 'white',
  borderRadius: '5px',
  transition: 'background-color 0.3s, border-color 0.3s',
});

const subtitleContainerStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-around',
  marginTop: '30px',
};

const subtitleBoxStyle: React.CSSProperties = {
  width: '45%',
  padding: '20px',
  border: '1px solid #ccc',
  borderRadius: '8px',
  backgroundColor: '#f9f9f9',
  minHeight: '100px',
};

const subtitleTextStyle: React.CSSProperties = {
  fontSize: '18px',
  color: '#555',
  whiteSpace: 'pre-wrap', // Ensures text wraps and respects newlines
};

export default App;
