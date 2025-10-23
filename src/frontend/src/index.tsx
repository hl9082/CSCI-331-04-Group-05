
// Authors: Huy Le (hl9082)
// This is the entry point of the React application.
// It is of high importance as it renders the root component.

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
