import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import './AuthModal.css';

export default function AuthModal({ isOpen, onClose }) {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const { login, register } = useAuth();

  if (!isOpen) return null;

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (isLogin) {
      const result = await login(formData.username, formData.password);
      if (result.success) {
        onClose();
      } else {
        setError(result.error);
      }
    } else {
      if (formData.password !== formData.confirmPassword) {
        setError('Passwords do not match');
        setLoading(false);
        return;
      }
      if (formData.password.length < 6) {
        setError('Password must be at least 6 characters');
        setLoading(false);
        return;
      }
      const result = await register(formData.username, formData.email, formData.password);
      if (result.success) {
        onClose();
      } else {
        setError(result.error);
      }
    }
    
    setLoading(false);
  };

  const switchMode = () => {
    setIsLogin(!isLogin);
    setError('');
    setFormData({
      username: '',
      email: '',
      password: '',
      confirmPassword: ''
    });
  };

  return (
    <div className="auth-modal-overlay" onClick={onClose}>
      <div className="auth-modal-container" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="auth-header">
          <h1 className="auth-main-title">Sign In And Sign Up Forms</h1>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="auth-split-container">
          {/* Left Side - Sign In */}
          <div className="auth-left-panel">
            <div className="auth-form-container">
              <h2 className="form-title">Welcome Back</h2>
              <p className="form-subtitle">Sign in to your account</p>
              
              <form onSubmit={handleSubmit} className="auth-form">
                <div className="form-group">
                  <input
                    type="text"
                    name="username"
                    placeholder="Username"
                    value={formData.username}
                    onChange={handleChange}
                    className="rounded-input"
                    required
                  />
                </div>
                
                <div className="form-group">
                  <input
                    type="password"
                    name="password"
                    placeholder="Password"
                    value={formData.password}
                    onChange={handleChange}
                    className="rounded-input"
                    required
                  />
                </div>

                {!isLogin && (
                  <>
                    <div className="form-group">
                      <input
                        type="email"
                        name="email"
                        placeholder="Email"
                        value={formData.email}
                        onChange={handleChange}
                        className="rounded-input"
                        required
                      />
                    </div>
                    
                    <div className="form-group">
                      <input
                        type="password"
                        name="confirmPassword"
                        placeholder="Confirm Password"
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        className="rounded-input"
                        required
                      />
                    </div>
                  </>
                )}
                
                {isLogin && (
                  <div className="form-options">
                    <label className="remember-me">
                      <input
                        type="checkbox"
                        checked={rememberMe}
                        onChange={(e) => setRememberMe(e.target.checked)}
                      />
                      <span className="checkmark"></span>
                      Remember me
                    </label>
                    <a href="#" className="forgot-password">Forgot Password?</a>
                  </div>
                )}
                
                {error && <div className="error-message">{error}</div>}
                
                <button 
                  type="submit" 
                  disabled={loading} 
                  className="gradient-button primary"
                >
                  {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Create Account')}
                </button>
              </form>
            </div>
          </div>

          {/* Right Side - Sign Up Promotion */}
          <div className="auth-right-panel">
            <div className="right-panel-content">
              <h2 className="right-panel-title">
                {isLogin ? 'New Here?' : 'Already Have Account?'}
              </h2>
              <p className="right-panel-description">
                {isLogin 
                  ? 'Join our community of graph visualization enthusiasts. Create stunning mathematical visualizations and explore the beauty of mathematics in 2D and 3D.'
                  : 'Welcome back! Sign in to access your saved graphs, view your visualization history, and continue your mathematical journey.'
                }
              </p>
              <button 
                onClick={switchMode} 
                className="gradient-button secondary"
              >
                {isLogin ? 'Sign Up' : 'Sign In'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
