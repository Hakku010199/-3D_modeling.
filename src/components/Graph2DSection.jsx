import React from 'react';
import './Graph2DSection.css';

export default function Graph2DSection({ input }) {
  return (
    <section className="graph-section fade-in">
      <h2>2D Graph Preview</h2>
      <div className="graph-placeholder">[2D Graph for: {input}]</div>
      <div className="graph-analysis">
        <h3>Graph Analysis:</h3>
        <ul>
          <li>Function Type: </li>
          <li>Symmetry: </li>
          
        </ul>
      </div>
    </section>
  );
}