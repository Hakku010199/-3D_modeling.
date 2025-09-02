import React from 'react';
import './Graph3DSection.css';

export default function Graph3DSection({ input, graphData }) {
  const saveAsPNG = () => {
    if (graphData && graphData.image) {
      const link = document.createElement('a');
      link.href = graphData.image;
      const cleanInput = input.replace(/[^a-zA-Z0-9θ]/g, '_');
      const timestamp = Date.now();
      link.download = `3D_graph_${cleanInput}_${timestamp}.png`;
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
        
        const dataURL = canvas.toDataURL('image/jpeg', 0.95);
        const link = document.createElement('a');
        link.href = dataURL;
        const cleanInput = input.replace(/[^a-zA-Z0-9θ]/g, '_');
        const timestamp = Date.now();
        link.download = `3D_graph_${cleanInput}_${timestamp}.jpg`;
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
      const cleanInput = input.replace(/[^a-zA-Z0-9θ]/g, ' ');
      
      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>3D Graph - ${cleanInput}</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { text-align: center; margin-bottom: 20px; }
            .graph-image { max-width: 100%; height: auto; }
            @media print { body { margin: 0; } }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>3D Mathematical Surface</h1>
            <p>Polar Expression: ${graphData.expression || input}</p>
            <p>Generated: ${new Date().toLocaleDateString()}</p>
          </div>
          <div style="text-align: center;">
            <img src="${graphData.image}" alt="3D Graph" class="graph-image" />
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