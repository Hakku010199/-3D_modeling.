import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './UserHistory.css';

export default function UserHistory({ user, onLoadGraph, isVisible, refreshTrigger }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // all, 2D, 3D, favorites

  console.log('UserHistory component rendered:', { user, isVisible, refreshTrigger });

  useEffect(() => {
    console.log('UserHistory useEffect:', { user, isVisible });
    if (user && isVisible) {
      fetchUserHistory();
    }
  }, [user, isVisible]);

  // Refresh history when component becomes visible or user changes
  useEffect(() => {
    if (user) {
      fetchUserHistory();
    }
  }, [user]);

  // Refresh when refreshTrigger changes (new graph saved)
  useEffect(() => {
    if (user && refreshTrigger > 0) {
      fetchUserHistory();
    }
  }, [refreshTrigger, user]);

  const fetchUserHistory = async () => {
    console.log('Fetching user history...');
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      console.log('Token:', token ? 'Present' : 'Missing');
      const response = await axios.get('http://localhost:5000/api/graphs', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      console.log('History response:', response.data);
      setHistory(response.data.graphs || []);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch history:', err);
      setError('Failed to load history');
    } finally {
      setLoading(false);
    }
  };

  const toggleFavorite = async (graphId, currentStatus) => {
    try {
      const token = localStorage.getItem('token');
      await axios.put(`http://localhost:5000/api/graphs/${graphId}/favorite`, {}, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      // Update local state
      setHistory(prev => prev.map(graph => 
        graph.id === graphId 
          ? { ...graph, is_favorite: !currentStatus }
          : graph
      ));
    } catch (err) {
      console.error('Failed to toggle favorite:', err);
    }
  };

  const deleteGraph = async (graphId) => {
    if (window.confirm('Are you sure you want to delete this graph?')) {
      try {
        const token = localStorage.getItem('token');
        await axios.delete(`http://localhost:5000/api/graphs/${graphId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        setHistory(prev => prev.filter(graph => graph.id !== graphId));
      } catch (err) {
        console.error('Failed to delete graph:', err);
      }
    }
  };

  const filteredHistory = history.filter(graph => {
    if (filter === 'all') return true;
    if (filter === 'favorites') return graph.is_favorite;
    if (filter === '2D') return graph.graph_type === '2D';
    if (filter === '3D') return graph.graph_type === '3D';
    return true;
  });

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
  };

  console.log('UserHistory render check:', { isVisible, user, shouldRender: isVisible && user });

  return (
    <div className="user-history-sidebar">
      <div className="history-header">
        <h3>Your Graph History</h3>
        <button onClick={fetchUserHistory} className="refresh-button" disabled={loading}>
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      <div className="history-stats">
        <div className="stat">
          <span className="stat-number">{history.length}</span>
          <span className="stat-label">Total Graphs</span>
        </div>
        <div className="stat">
          <span className="stat-number">{history.filter(g => g.is_favorite).length}</span>
          <span className="stat-label">Favorites</span>
        </div>
      </div>

      <div className="history-filters">
        <select value={filter} onChange={(e) => setFilter(e.target.value)} className="filter-select">
          <option value="all">All Graphs</option>
          <option value="favorites">Favorites</option>
          <option value="2D">2D Graphs</option>
          <option value="3D">3D Graphs</option>
        </select>
      </div>

      <div className="history-list">
        {loading ? (
          <div className="history-loading">Loading history...</div>
        ) : error ? (
          <div className="history-error">{error}</div>
        ) : filteredHistory.length === 0 ? (
          <div className="history-empty">
            {filter === 'all' ? 'No graphs generated yet' : `No ${filter} graphs found`}
          </div>
        ) : (
          filteredHistory.map((graph) => (
            <div key={graph.id} className="history-item">
              <div className="graph-header">
                <span className={`graph-type type-${graph.graph_type.toLowerCase()}`}>
                  {graph.graph_type}
                </span>
                <button
                  onClick={() => toggleFavorite(graph.id, graph.is_favorite)}
                  className={`favorite-button ${graph.is_favorite ? 'favorited' : ''}`}
                >
                  {graph.is_favorite ? 'Favorited' : 'Favorite'}
                </button>
              </div>

              <div className="graph-title">{graph.title}</div>
              
              <div className="graph-expression">{graph.expression}</div>
              
              <div className="graph-date">{formatDate(graph.created_at)}</div>
              
              <div className="graph-actions">
                <button
                  onClick={() => onLoadGraph(graph.expression)}
                  className="load-button"
                >
                  Load
                </button>
                <button
                  onClick={() => deleteGraph(graph.id)}
                  className="delete-button"
                >
                  Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {history.length > 0 && (
        <div className="history-footer">
          <button onClick={() => setHistory([])} className="clear-button">
            Clear View
          </button>
        </div>
      )}
    </div>
  );
}
