/**
 * @author Huy Le (hl9082)
 * @brief This component is the main application component. It handles the UI
 *        and the communication with the backend services for transcription.
 * @importance It is of high importance as it is the root component of the application.
 */
import React, { useState, useEffect } from 'react';

// Define the base URL of the backend API.
const API_BASE_URL = 'http://127.0.0.1:8000';

const App: React.FC = () => {
  // --- State for Real-Time Speech-to-Text ---
  // Holds the text transcribed from speech.
  const [speechSubtitle, setSpeechSubtitle] = useState<string>('Speech service is off.');
  // Tracks which real-time service is currently active ('speech' or 'none').
  const [activeService, setActiveService] = useState<'speech' | 'none'>('none');

  // --- State for ASL Image Translation ---
  // Holds the image file selected by the user.
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  // Holds the URL for the image preview.
  const [preview, setPreview] = useState<string | null>(null);
  // Holds the predicted letter from the ASL image.
  const [prediction, setPrediction] = useState<string | null>(null);
  // Holds the confidence score of the prediction.
  const [confidence, setConfidence] = useState<number | null>(null);
  // Holds any error messages related to image translation.
  const [error, setError] = useState<string | null>(null);


  // --- Effect for Real-Time Services ---
  // This effect runs once when the component mounts to establish a connection
  // to the backend's Server-Sent Events (SSE) stream.
  useEffect(() => {
    const eventSource = new EventSource(`${API_BASE_URL}/stream`);

    // This handler is called whenever a message is received from the stream.
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        // Update the speech subtitle if the message is from the 'speech' service.
        if (data.service === 'speech') {
          setSpeechSubtitle(data.text);
        }
      } catch (error) {
        console.error('Failed to parse SSE message:', error);
      }
    };

    // This handler is called if there's an error with the SSE connection.
    eventSource.onerror = (error) => {
      console.error('EventSource failed:', error);
      setSpeechSubtitle('Connection to server lost.');
      eventSource.close();
    };

    // The cleanup function is called when the component unmounts.
    // It's important to close the connection to prevent memory leaks.
    return () => {
      eventSource.close();
    };
  }, []); // The empty dependency array ensures this effect runs only once.


  // --- Handlers for Real-Time Speech Service ---
  const handleServiceClick = async (service: 'speech') => {
    try {
      // If the clicked service is already active, stop it.
      if (activeService === service) {
        await fetch(`${API_BASE_URL}/stop`);
        setActiveService('none');
      } else {
        // Otherwise, start the new service.
        await fetch(`${API_BASE_URL}/start/${service}`);
        setActiveService(service);
      }
    } catch (error) {
      console.error(`Failed to toggle service ${service}:`, error);
      setSpeechSubtitle('Failed to communicate with server.');
    }
  };


  // --- Handlers for ASL Image Translation ---
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Set the selected file and create a temporary URL for the preview.
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
      // Reset previous results.
      setPrediction(null);
      setConfidence(null);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select an image first.');
      return;
    }

    // Use FormData to send the file in a POST request.
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`${API_BASE_URL}/predict-asl`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to get prediction from server.');
      }

      // On success, update the state with the prediction results.
      const data = await response.json();
      setPrediction(data.prediction);
      setConfidence(data.confidence);
      setError(null);
    } catch (err: any) {
      setError(err.message);
      setPrediction(null);
      setConfidence(null);
    }
  };

  // --- Render ---
  return (
    <div style={{ textAlign: 'center', fontFamily: 'sans-serif', color: '#333' }}>
      <header style={{ backgroundColor: '#f4f4f4', padding: '20px', borderBottom: '1px solid #ddd' }}>
        <h1>Real-Time Transcription</h1>
      </header>
      <main style={{ margin: '40px auto', maxWidth: '960px' }}>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: '20px' }}>
          {/* Section for ASL Image Translation */}
          <div style={{...sectionStyle, flex: 1}}>
            <h2>ASL Image Translator</h2>
            <p>Upload an image of an ASL letter to translate it.</p>
            <input type="file" accept="image/*" onChange={handleFileChange} style={{ margin: '10px 0' }} />
            
            {preview && (
              <div style={{ margin: '10px 0' }}>
                <img src={preview} alt="Selected ASL sign" style={{ maxWidth: '200px', maxHeight: '200px', border: '1px solid #ddd', borderRadius: '4px' }} />
              </div>
            )}

            <button onClick={handleUpload} style={getButtonStyle(false)}>
              Translate Image
            </button>

            {prediction && confidence !== null && (
              <div style={resultBoxStyle}>
                <p style={resultTextStyle}>Predicted Letter: <strong>{prediction}</strong></p>
                <p style={resultTextStyle}>Confidence: <strong>{(confidence * 100).toFixed(2)}%</strong></p>
              </div>
            )}

            {error && <p style={{ color: 'red', marginTop: '10px' }}>Error: {error}</p>}
          </div>

          {/* Section for Speech-to-Text */}
          <div style={{...sectionStyle, flex: 1}}>
            <h2>Speech-to-Text</h2>
            <p>Start the service to get real-time subtitles from your microphone.</p>
            <button
              onClick={() => handleServiceClick('speech')}
              style={getButtonStyle(activeService === 'speech')}
            >
              {activeService === 'speech' ? 'Stop Speech-to-Subtitle' : 'Start Speech-to-Subtitle'}
            </button>
            <div style={subtitleBoxStyle}>
              <h3>Speech Subtitles</h3>
              <p style={subtitleTextStyle}>{speechSubtitle}</p>
            </div>
          </div>
        </div>

      </main>
    </div>
  );
};

// --- Styling ---

const getButtonStyle = (isActive: boolean): React.CSSProperties => ({
  margin: '10px 0',
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

const sectionStyle: React.CSSProperties = {
  padding: '20px',
  border: '1px solid #ddd',
  borderRadius: '8px',
  backgroundColor: '#fafafa',
  marginBottom: '20px',
};

const resultBoxStyle: React.CSSProperties = {
  marginTop: '20px',
  padding: '10px',
  border: '1px solid #ccc',
  borderRadius: '8px',
  backgroundColor: '#f0f0f0',
};

const resultTextStyle: React.CSSProperties = {
  fontSize: '18px',
  color: '#333',
  margin: '5px 0',
};

const subtitleBoxStyle: React.CSSProperties = {
  marginTop: '20px',
  padding: '20px',
  border: '1px solid #ccc',
  borderRadius: '8px',
  backgroundColor: '#f9f9f9',
  minHeight: '100px',
};

const subtitleTextStyle: React.CSSProperties = {
  fontSize: '18px',
  color: '#555',
  whiteSpace: 'pre-wrap',
};

export default App;