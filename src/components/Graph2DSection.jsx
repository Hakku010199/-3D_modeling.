import React from 'react';
import './Graph2DSection.css';

export default function Graph2DSection({ input, graphData }) {
  return (
    <section className="graph-section fade-in">
      <h2>2D Graph Preview</h2>
      
      {graphData && graphData.image ? (
        <div className="graph-container">
          <img 
            src={graphData.image} 
            alt={`Graph of ${graphData.expression || input}`}
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
            <em>{graphData ? 'Loading graph...' : 'Graph visualization will appear here when Flask backend is connected'}</em>
          </div>
        </div>
      )}
      
      <div className="graph-analysis">
        <h3>Graph Analysis:</h3>
        {graphData && graphData.analysis ? (
          <ul>
            <li><strong>Function:</strong> f(x) = {graphData.expression || input}</li>
            <li><strong>Type:</strong> {graphData.analysis.type || 'Mathematical function'}</li>
            <li><strong>Domain:</strong> {graphData.analysis.domain || 'Real numbers'}</li>
            <li><strong>Range:</strong> {graphData.analysis.range || 'Calculating...'}</li>
            {graphData.analysis.properties && graphData.analysis.properties.length > 0 && (
              <li><strong>Properties:</strong> {graphData.analysis.properties.join(', ')}</li>
            )}
            <li><strong>Backend Status:</strong> ✅ Connected</li>
          </ul>
        ) : (
          <ul>
            <li>Function Type: {input ? 'Mathematical Expression' : 'Pending'}</li>
            <li>Symmetry: Analysis pending backend connection</li>
            <li>Domain: Real numbers (default)</li>
            <li>Backend Status: {graphData ? '🔄 Processing...' : '❌ Disconnected - showing preview mode'}</li>
          </ul>
        )}
      </div>
    </section>
  );
}