import React, { useState } from 'react';
import './FunctionInput.css';

export default function FunctionInput({ functionInput, setFunctionInput, onGenerate2D, onRender3D }) {
  const [nlpInput, setNlpInput] = useState('');
  const [nlpLoading, setNlpLoading] = useState(false);
  const [nlpSuggestions, setNlpSuggestions] = useState([]);

  const handleNaturalLanguageInput = async () => {
    if (!nlpInput.trim()) return;
    
    setNlpLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/parse-language', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          input: nlpInput
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Auto-fill the mathematical expression
        setFunctionInput(data.equation);
        // Show interpretation message
        alert(`✅ ${data.interpretation}`);
        setNlpSuggestions([]);
      } else {
        // Show suggestions
        setNlpSuggestions(data.suggestions || []);
        alert(`❌ ${data.error}`);
      }
    } catch (error) {
      console.error('NLP parsing error:', error);
      alert('Error processing natural language input');
    } finally {
      setNlpLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setNlpInput(suggestion);
    setNlpSuggestions([]);
  };

  return (
    <div className="input-section">
      {/* Natural Language Input */}
      <div className="nlp-section">
        <h3>🗣️ Natural Language Input (NEW!)</h3>
        <div className="nlp-input-group">
          <input
            type="text"
            value={nlpInput}
            onChange={(e) => setNlpInput(e.target.value)}
            placeholder='Try: "draw rose with 4 petals" or "create a heart shape"'
            className="nlp-input"
            onKeyPress={(e) => e.key === 'Enter' && handleNaturalLanguageInput()}
          />
          <button 
            className="nlp-button" 
            onClick={handleNaturalLanguageInput}
            disabled={nlpLoading}
          >
            {nlpLoading ? '🔄' : '🧠'} Parse
          </button>
        </div>
        
        {/* Suggestions */}
        {nlpSuggestions.length > 0 && (
          <div className="nlp-suggestions">
            <p>💡 Try these examples:</p>
            {nlpSuggestions.map((suggestion, index) => (
              <button 
                key={index}
                className="suggestion-button"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}
      </div>
      
      <div className="divider">OR</div>
      
      {/* Original Mathematical Input */}
      <div className="math-section">
        <h3>📐 Mathematical Expression</h3>
        <textarea
          value={functionInput}
          onChange={(e) => setFunctionInput(e.target.value)}
          placeholder="Enter mathematical expression (e.g., r = cos(2*theta), sin(x))..."
          className="function-input"
        />
      </div>
      
      <div className="button-group">
        <button className="action-button" onClick={onGenerate2D}>Generate 2D Graph</button>
        <button className="action-button" onClick={onRender3D}>Render in 3D</button>
      </div>
    </div>
  );
}