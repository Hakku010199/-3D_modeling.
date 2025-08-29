import React from 'react';
import './Graph3DSection.css';

export default function Graph3DSection({ input, graphData }) {
  return (
    <section className="graph-section fade-in">
      <h2>🧊 3D Model Rendering</h2>
      
      {graphData && graphData.image ? (
        <div className="graph-container">
          <img 
            src={graphData.image} 
            alt={`3D Surface plot of ${graphData.expression || input}`}
            className="graph-image"
            style={{
              maxWidth: '100%',
              height: 'auto',
              border: '1px solid #ddd',
              borderRadius: '8px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}
          />
        </div>
      ) : (
        <div className="graph-placeholder">
          <div>
            <strong>Function:</strong> {input || 'No function entered'}<br/>
            <em>{graphData ? 'Generating 3D surface...' : '3D visualization will appear here when Flask backend is connected'}</em>
          </div>
        </div>
      )}
      
      <div className="graph-analysis">
        <h3>3D Model Analysis:</h3>
        {graphData ? (
          <ul>
            <li><strong>Function:</strong> f(x,y) = {graphData.expression || input}</li>
            <li><strong>Type:</strong> {graphData.type || '3D Surface Plot'}</li>
            <li><strong>Backend Status:</strong> Connected</li>
          </ul>
        ) : (
          <ul>
            <li>Function: {input || 'Pending'}</li>
            <li>Type: 3D Surface Plot</li>
            <li>Backend Status: Disconnected</li>
          </ul>
        )}
      </div>
    </section>
  );
}