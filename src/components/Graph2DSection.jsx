import React from 'react';
import './Graph2DSection.css';

export default function Graph2DSection({ input, graphData }) {
  const saveAsPNG = () => {
    if (graphData && graphData.image) {
      const link = document.createElement('a');
      link.href = graphData.image;
      const cleanInput = input.replace(/[^a-zA-Z0-9]/g, '_');
      const timestamp = Date.now();
      link.download = `2D_graph_${cleanInput}_${timestamp}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const saveAsJPEG = () => {
    if (graphData && graphData.image) {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const img = new Image();
      
      img.onload = () => {
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);
        
        const dataURL = canvas.toDataURL('image/jpeg', 0.9);
        const link = document.createElement('a');
        link.href = dataURL;
        const cleanInput = input.replace(/[^a-zA-Z0-9]/g, '_');
        const timestamp = Date.now();
        link.download = `2D_graph_${cleanInput}_${timestamp}.jpg`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      };
      
      img.src = graphData.image;
    }
  };

  const printAsPDF = () => {
    if (graphData && graphData.image) {
      const printWindow = window.open('', '_blank');
      const cleanInput = input.replace(/[^a-zA-Z0-9]/g, ' ');
      
      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>2D Graph - ${cleanInput}</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { text-align: center; margin-bottom: 20px; }
            .graph-image { max-width: 100%; height: auto; }
            @media print { body { margin: 0; } }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>2D Mathematical Graph</h1>
            <p>Expression: ${graphData.expression || input}</p>
            <p>Generated: ${new Date().toLocaleDateString()}</p>
          </div>
          <div style="text-align: center;">
            <img src="${graphData.image}" alt="2D Graph" class="graph-image" />
          </div>
        </body>
        </html>
      `);
      
      printWindow.document.close();
      setTimeout(() => {
        printWindow.print();
        setTimeout(() => printWindow.close(), 1000);
      }, 500);
    }
  };
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
          <div className="graph-actions">
            <button onClick={saveAsPNG} className="save-button" title="Save as PNG">
              📄 PNG
            </button>
            <button onClick={saveAsJPEG} className="save-button" title="Save as JPEG">
              📷 JPEG
            </button>
            <button onClick={printAsPDF} className="save-button" title="Print as PDF">
              📄 PDF
            </button>
          </div>
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
            <li><strong>Backend Status:</strong> Connected</li>
          </ul>
        ) : (
          <ul>
            <li>Function Type: {input ? 'Mathematical Expression' : 'Pending'}</li>
            <li>Symmetry: Analysis pending backend connection</li>
            <li>Domain: Real numbers (default)</li>
            <li>Backend Status: {graphData ? 'Processing...' : 'Disconnected - showing preview mode'}</li>
          </ul>
        )}
      </div>
    </section>
  );
}