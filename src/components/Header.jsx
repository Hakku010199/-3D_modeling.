import React from 'react';
import './Header.css';

export default function Header({ user, isAuthenticated, onShowAuth, onLogout }) {
  const title = "2D Graph Interpretation and 3D Modeling";
  
  return (
    <header className="header">
      <div className="header-content">
        <div className="title-section">
          <h1>
            {title.split('').map((char, index) => (
              <span 
                key={index} 
                style={{ 
                  animationDelay: `${index * 0.05}s`,
                  marginLeft: char === ' ' ? '0.3em' : '0'
                }}
              >
                {char}
              </span>
            ))}
          </h1>
          <div className="description">
            <p>
              <strong>Polar functions</strong> define curves in a polar coordinate system, where a point is located by its distance (r) from the origin (pole) and the angle (θ) from the positive x-axis. These functions, often expressed as r = f(θ), allow for representing curves that are difficult or impossible to express in Cartesian coordinates.
            </p>
            
            <div className="key-concepts">
              <h3>Key Concepts:</h3>
              
              <div className="concept-group">
                <h4>Polar Coordinates:</h4>
                <p>A point is represented as (r, θ), where 'r' is the distance from the pole and 'θ' is the angle from the polar axis.</p>
              </div>

              <div className="concept-group">
                <h4>Polar Equation:</h4>
                <p>An equation that relates 'r' and 'θ', defining a curve in polar coordinates.</p>
              </div>

              <div className="concept-group">
                <h4>Graphing Polar Functions:</h4>
                <p>Plot points (r, θ) where 'r' is the radius and 'θ' is the angle, often requiring adjustments for negative 'r' values.</p>
              </div>

              <div className="concept-group">
                <h4>Conversion between Coordinate Systems:</h4>
                <ul>
                  <li><strong>Polar to Rectangular:</strong> x = r cos(θ), y = r sin(θ)</li>
                  <li><strong>Rectangular to Polar:</strong> r = √(x² + y²), θ = arctan(y/x) (with adjustments for quadrants)</li>
                </ul>
              </div>

              <div className="concept-group">
                <h4>Advantages of Polar Coordinates:</h4>
                <p>Some curves are easier to represent and analyze using polar coordinates, especially those with circular or spiral shapes.</p>
              </div>

              <div className="examples-section">
                <h4>Examples:</h4>
                <div className="examples-grid">
                  <div className="example-item">
                    <strong>Circles:</strong>
                    <span>r = a, r = a cos(θ), r = a sin(θ)</span>
                  </div>
                  <div className="example-item">
                    <strong>Cardioids:</strong>
                    <span>r = a(1 + cos(θ)), r = a(1 + sin(θ))</span>
                  </div>
                  <div className="example-item">
                    <strong>Lemniscates:</strong>
                    <span>r² = a² cos(2θ), r² = a² sin(2θ)</span>
                  </div>
                  <div className="example-item">
                    <strong>Roses:</strong>
                    <span>r = a cos(nθ), r = a sin(nθ)</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="auth-section">
          {isAuthenticated ? (
            <div className="user-menu">
              <div className="user-info">
                <span className="user-welcome">👋 Welcome back!</span>
                <span className="username">{user?.username}</span>
                <span className="user-stats">{user?.total_graphs || 0} graphs saved</span>
              </div>
              <button onClick={onLogout} className="logout-button">
                Sign Out
              </button>
            </div>
          ) : (
            <div className="auth-buttons">
              <button onClick={onShowAuth} className="auth-button login">
                Sign In
              </button>
              <button onClick={onShowAuth} className="auth-button register">
                Sign Up
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}