import React from 'react';

function SimpleApp() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>3D Graph Visualization Test</h1>
      <p>If you can see this, React is working correctly!</p>
      <button onClick={() => alert('React is working!')}>
        Test Button
      </button>
    </div>
  );
}

export default SimpleApp;
