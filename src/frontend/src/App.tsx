/**
@author Huy Le (hl9082), Joshua Elliot (jae4950)
@brief This component is the main application component.
@importance It is of high importance as it is the root component of the application.
**/

import React, { useState, useEffect } from "react";

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [speechText, setSpeechText] = useState("Waiting on speech...");
  const [isRunning, setIsRunning] = useState(false);

  // Poll backend every 400 ms while service is running
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isRunning) {
      interval = setInterval(async () => {
        try {
          const response = await fetch(`${API_BASE}/speech-to-text`);
          const data = await response.json();
          setSpeechText(data.text);
        } catch (error) {
          console.error("Error fetching speech text:", error);
        }
      }, 400);
    }
    return () => clearInterval(interval);
  }, [isRunning]);

  const startSpeechService = async () => {
    try {
      const response = await fetch(`${API_BASE}/start/speech`);
      const data = await response.json();
      console.log(data.message);
      setIsRunning(true);
    } catch (error) {
      console.error("Error starting speech service:", error);
    }
  };

  const stopService = async () => {
    try {
      const response = await fetch(`${API_BASE}/stop`);
      const data = await response.json();
      console.log(data.message);
      setIsRunning(false);
      setSpeechText("Waiting on speech...");
    } catch (error) {
      console.error("Error stopping service:", error);
    }
  };

  return (
    <div style={{ textAlign: "center", fontFamily: "sans-serif" }}>
      <header>
        <h1>ASR-to-subtitle</h1>
      </header>

      <main style={{ margin: "50px" }}>
        {/* ASL button (not functional yet) */}
        <button
          style={{
            marginRight: "20px",
            padding: "10px 20px",
            fontSize: "16px",
          }}
        >
          ASL-to-subtitle
        </button>

        {/* Speech button */}
        <button
          onClick={startSpeechService}
          style={{
            padding: "10px 20px",
            fontSize: "16px",
          }}
          disabled={isRunning}
        >
          Speech-to-subtitle
        </button>

        {/* Show only when transcription is running */}
        {isRunning && (
          <div style={{ marginTop: "40px" }}>
            <button
              onClick={stopService}
              style={{
                marginTop: "20px",
                padding: "10px 20px",
                fontSize: "16px",
                backgroundColor: "#fb2a2aff",
                color: "white",
                border: "none",
                borderRadius: "5px",
                cursor: "pointer",
                transition: "background-color 0.3s",
              }}
              onMouseEnter={(e) =>
                (e.currentTarget.style.backgroundColor = "#ca0d0dff")
              }
              onMouseLeave={(e) =>
                (e.currentTarget.style.backgroundColor = "#fb2a2aff")
              }
            >
              Stop
            </button>
            <div
              style={{
                marginTop: "40px",
                border: "1px solid #ccc",
                borderRadius: "10px",
                padding: "20px",
                width: "400px",
                margin: "40px auto",
                background: "#fafafa",
              }}
            >
              <h3>Live Transcription:</h3>
              <p style={{ fontSize: "18px" }}>{speechText}</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
