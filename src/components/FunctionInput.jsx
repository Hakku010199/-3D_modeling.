import React from 'react';
import './FunctionInput.css';

export default function FunctionInput({ functionInput, setFunctionInput, onGenerate2D, onRender3D }) {
  return (
    <div className="input-section">
      <textarea
        value={functionInput}
        onChange={(e) => setFunctionInput(e.target.value)}
        placeholder="Enter a polar (e.g., r = sin(2θ)) or parametric function (e.g., x = sin(t), y = cos(t))..."
        className="function-input"
      />
      <div className="button-group">
        <button className="action-button" onClick={onGenerate2D}>Generate 2D Graph</button>
        <button className="action-button" onClick={onRender3D}>Render in 3D</button>
      </div>
    </div>
  );
}