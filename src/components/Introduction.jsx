import React, { useState } from 'react';
import './Introduction.css';

export default function PolarCoordinatesIntroduction() {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="introduction-section">
      <div className="intro-header" onClick={() => setIsExpanded(!isExpanded)}>
        <h2>📊 Understanding Polar Coordinates</h2>
        <span className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>▼</span>
      </div>
      
      {isExpanded && (
        <div className="intro-content">
          <div className="intro-text">
            <h3>🎯 Understanding Polar Coordinates</h3>
            <p>
              Start with a point <strong>O</strong> in the plane called the <strong>pole</strong> (we will always identify this point with the origin). 
              From the pole, draw a ray, called the <strong>initial ray</strong> (we will always draw this ray horizontally, identifying it with the positive x-axis). 
            </p>
            
            <p>
              A point <strong>P</strong> in the plane is determined by the distance <strong>r</strong> that <strong>P</strong> is from <strong>O</strong>, 
              and the angle <strong>θ</strong> formed between the initial ray and the segment <strong>OP</strong> (measured counter-clockwise). 
              We record the distance and angle as an ordered pair <strong>(r,θ)</strong>. This concept is illustrated through 
              interactive examples in our graph visualizer below.
            </p>

            <div className="coordinate-explanation">
              <h4>🔵 Key Components of Polar Coordinates:</h4>
              <ul>
                <li>
                  <strong>Pole (O):</strong> The reference point in the plane, equivalent to the origin in rectangular coordinates
                </li>
                <li>
                  <strong>Initial Ray:</strong> The reference direction, drawn horizontally and identified with the positive x-axis
                </li>
                <li>
                  <strong>Distance (r):</strong> How far point P is from the pole O
                </li>
                <li>
                  <strong>Angle (θ):</strong> The angle formed between the initial ray and segment OP, measured counter-clockwise
                </li>
              </ul>
            </div>

            <div className="notation-box">
              <h4>📝 Notation:</h4>
              <p>
                We record the distance and angle as an ordered pair <strong>(r, θ)</strong>. 
                To avoid confusion with rectangular coordinates, we will denote polar coordinates with the letter <strong>P</strong>, 
                as in <strong>P(r, θ)</strong>.
              </p>
              <p>
                <em>This notation helps distinguish polar coordinates from rectangular coordinates (x, y)</em>
              </p>
            </div>

            <div className="examples-section">
              <h4>🌹 Try These Polar Examples:</h4>
              <div className="example-grid">
                <div className="example-card">
                  <h5>Rose Curve (4 petals)</h5>
                  <code>r = cos(2*theta)</code>
                  <p>Creates a beautiful 4-petal rose pattern</p>
                </div>
                <div className="example-card">
                  <h5>Circle</h5>
                  <code>r = 3</code>
                  <p>A circle with radius 3 centered at origin</p>
                </div>
                <div className="example-card">
                  <h5>Spiral</h5>
                  <code>r = theta</code>
                  <p>An Archimedean spiral expanding outward</p>
                </div>
                <div className="example-card">
                  <h5>Cardioid (Heart)</h5>
                  <code>r = 1 + cos(theta)</code>
                  <p>Heart-shaped curve using polar coordinates</p>
                </div>
              </div>
            </div>

            <div className="conversion-info">
              <h4>🔄 Conversion Between Coordinate Systems:</h4>
              <div className="conversion-formulas">
                <div className="formula-group">
                  <h5>Polar to Rectangular:</h5>
                  <p><code>x = r × cos(θ)</code></p>
                  <p><code>y = r × sin(θ)</code></p>
                </div>
                <div className="formula-group">
                  <h5>Rectangular to Polar:</h5>
                  <p><code>r = √(x² + y²)</code></p>
                  <p><code>θ = arctan(y/x)</code></p>
                </div>
              </div>
            </div>

            <div className="natural-language-hint">
              <h4>🗣️ Natural Language Support:</h4>
              <p>
                Our application supports natural language input! Try phrases like:
              </p>
              <ul>
                <li>"draw rose with 4 petals"</li>
                <li>"create a heart shape"</li>
                <li>"make a spiral"</li>
                <li>"show circle with radius 5"</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
