import React from 'react';
import './Header.css';

export default function Header() {
  const title = "2D Graph Interpretation and 3D Modeling";  // Added proper spacing
  
  return (
    <header className="header">
      <h1>
        {title.split('').map((char, index) => (
          <span 
            key={index} 
            style={{ 
              animationDelay: `${index * 0.05}s`,
              marginLeft: char === ' ' ? '0.3em' : '0'  // Add extra space for word separation
            }}
          >
            {char}
          </span>
        ))}
      </h1>
      <p>
        Polar functions represent mathematical relationships where points on a plane are determined by a radius (r) and an angle (θ) rather than traditional Cartesian coordinates (x, y). These functions are typically expressed in the form r = f(θ), where the distance from the origin (pole) changes as the angle rotates. Polar functions are especially useful for describing circular, spiral, or other rotationally symmetric patterns.
       </p>
       <p>
        Parametric functions describe a set of related quantities using a third variable, often t (the parameter). Rather than expressing y directly in terms of x, parametric equations define both x and y as separate functions of t: x = f(t) and y = g(t). This approach is powerful in modeling motion, paths, or any dynamic systems where each coordinate changes over time or due to another factor. Parametric equations are widely used in physics, animation, and engineering, enabling the modeling of complex curves and real-world trajectories.
      </p>
    </header>
  );
}