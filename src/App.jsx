import React, { useState, useRef } from 'react';
import axios from 'axios';  // Add this import
import Header from './components/Header';
import FunctionInput from './components/FunctionInput';
import Graph2DSection from './components/Graph2DSection';
import Graph3DSection from './components/Graph3DSection';
import './App.css';

export default function App() {
  const [show2D, setShow2D] = useState(false);
  const [show3D, setShow3D] = useState(false);
  const [functionInput, setFunctionInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [graphData2D, setGraphData2D] = useState(null);
  const [graphData3D, setGraphData3D] = useState(null);
  const graph2DRef = useRef(null);
  const graph3DRef = useRef(null);

  const handleGenerate2D = async () => {
    setLoading(true);
    setError(null);
    setGraphData2D(null);
    try {
      const response = await axios.post('http://localhost:5000/api/generate', {
        functionType: '2D',
        expression: functionInput
      });
      
      console.log('Server response:', response.data);
      if (response.data.status === 'success') {
        setGraphData2D(response.data.data);
        setShow2D(true);
        setTimeout(() => graph2DRef.current.scrollIntoView({ behavior: 'smooth' }), 300);
      }
    } catch (err) {
      console.error('Error:', err);
      setError('Backend not available - showing preview mode');
      // Show the graph section even without backend
      setShow2D(true);
      setTimeout(() => graph2DRef.current.scrollIntoView({ behavior: 'smooth' }), 300);
    } finally {
      setLoading(false);
    }
  };

  const handleRender3D = async () => {
    setLoading(true);
    setError(null);
    setGraphData3D(null);
    try {
      const response = await axios.post('http://localhost:5000/api/generate', {
        functionType: '3D',
        expression: functionInput
      });
      
      console.log('Server response:', response.data);
      if (response.data.status === 'success') {
        setGraphData3D(response.data.data);
        setShow3D(true);
        setTimeout(() => graph3DRef.current.scrollIntoView({ behavior: 'smooth' }), 300);
      }
    } catch (err) {
      console.error('Error:', err);
      setError('Backend not available - showing preview mode');
      // Show the graph section even without backend
      setShow3D(true);
      setTimeout(() => graph3DRef.current.scrollIntoView({ behavior: 'smooth' }), 300);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <Header />
      <FunctionInput 
        functionInput={functionInput} 
        setFunctionInput={setFunctionInput} 
        onGenerate2D={handleGenerate2D} 
        onRender3D={handleRender3D}
        loading={loading}
      />
      {error && <div className="error-message">{error}</div>}
      {show2D && <div ref={graph2DRef}><Graph2DSection input={functionInput} graphData={graphData2D} /></div>}
      {show3D && <div ref={graph3DRef}><Graph3DSection input={functionInput} graphData={graphData3D} /></div>}
    </div>
  );
}