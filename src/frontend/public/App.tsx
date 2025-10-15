
// authors: [your name]
// This component is the main application component.
// It is of high importance as it is the root component of the application.

import React from 'react';

function App() {
  return (
    <div style={{ textAlign: 'center', fontFamily: 'sans-serif' }}>
      <header>
        <h1>ASR-to-subtitle</h1>
      </header>
      <main style={{ margin: '50px' }}>
        <button style={{ marginRight: '20px', padding: '10px 20px', fontSize: '16px' }}>
          ASL-to-subtitle
        </button>
        <button style={{ padding: '10px 20px', fontSize: '16px' }}>
          Speech-to-subtitle
        </button>
      </main>
    </div>
  );
}

export default App;
