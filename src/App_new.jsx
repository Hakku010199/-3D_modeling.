import React, { useState, useRef } from 'react';
import axios from 'axios';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Header from './components/Header';
import FunctionInput from './components/FunctionInput';
import Graph2DSection from './components/Graph2DSection';
import Graph3DSection from './components/Graph3DSection';
import AuthModal from './components/Auth/AuthModal';
import './App.css';

function AppContent() {
  const [show2D, setShow2D] = useState(false);
  const [show3D, setShow3D] = useState(false);
  const [functionInput, setFunctionInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [graphData2D, setGraphData2D] = useState(null);
  const [graphData3D, setGraphData3D] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const graph2DRef = useRef(null);
  const graph3DRef = useRef(null);
  
  const { isAuthenticated, user, logout, saveGraph } = useAuth();

  const handleSaveGraph = async (title, graphType, graphData) => {
    if (!isAuthenticated) {
      setShowAuthModal(true);
      return { success: false, error: 'Please sign in to save graphs' };
    }
    
    return await saveGraph(title, functionInput, graphType);
  };

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
      setError('Error generating graph');
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
      setError('Error generating graph');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <Header 
        user={user}
        isAuthenticated={isAuthenticated}
        onShowAuth={() => setShowAuthModal(true)}
        onLogout={logout}
      />
      
      <FunctionInput 
        functionInput={functionInput} 
        setFunctionInput={setFunctionInput} 
        onGenerate2D={handleGenerate2D} 
        onRender3D={handleRender3D}
        loading={loading}
        isAuthenticated={isAuthenticated}
      />
      
      {error && <div className="error-message">{error}</div>}
      
      {show2D && (
        <div ref={graph2DRef}>
          <Graph2DSection 
            input={functionInput} 
            graphData={graphData2D} 
            onSave={(title) => handleSaveGraph(title, '2D', graphData2D)}
            canSave={isAuthenticated}
          />
        </div>
      )}
      
      {show3D && (
        <div ref={graph3DRef}>
          <Graph3DSection 
            input={functionInput} 
            graphData={graphData3D} 
            onSave={(title) => handleSaveGraph(title, '3D', graphData3D)}
            canSave={isAuthenticated}
          />
        </div>
      )}
      
      <AuthModal 
        isOpen={showAuthModal} 
        onClose={() => setShowAuthModal(false)} 
      />
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
