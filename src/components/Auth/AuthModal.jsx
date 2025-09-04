import React, { useState } from 'react';
import './AuthModal.css';

export default function AuthModal({ isOpen, onClose, onLogin }) {
  const [isSignUp, setIsSignUp] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (error) setError('');
  };

  const validateForm = () => {
    // Check if all required fields are filled
    if (!formData.username.trim()) {
      setError('Username is required');
      return false;
    }

    if (isSignUp && !formData.email.trim()) {
      setError('Email is required');
      return false;
    }

    if (!formData.password.trim()) {
      setError('Password is required');
      return false;
    }

    if (isSignUp && !formData.confirmPassword.trim()) {
      setError('Please confirm your password');
      return false;
    }

    // Validate email format
    if (isSignUp && formData.email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(formData.email)) {
        setError('Please enter a valid email address');
        return false;
      }
    }

    // Check password match for sign up
    if (isSignUp && formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return false;
    }

    // Check password length
    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form before submission
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const endpoint = isSignUp ? '/api/register' : '/api/login';
      const requestBody = isSignUp 
        ? {
            username: formData.username.trim(),
            email: formData.email.trim(),
            password: formData.password
          }
        : {
            username: formData.username.trim(),
            password: formData.password
          };

      console.log('Submitting form:', { endpoint, requestBody });

      const response = await fetch(`http://localhost:5000${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      console.log('Response status:', response.status);

      const data = await response.json();
      console.log('Response data:', data);

      if (response.ok) {
        // Success
        localStorage.setItem('user', JSON.stringify(data.user));
        onLogin(data.user);
        onClose();
        // Reset form
        setFormData({ username: '', email: '', password: '', confirmPassword: '' });
        setError('');
      } else {
        // Error from server
        setError(data.message || `${isSignUp ? 'Registration' : 'Login'} failed`);
      }
    } catch (error) {
      console.error(`${isSignUp ? 'Registration' : 'Login'} error:`, error);
      setError('Network error. Please check your connection and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleMode = () => {
    setIsSignUp(!isSignUp);
    setFormData({ username: '', email: '', password: '', confirmPassword: '' });
    setError('');
  };

  if (!isOpen) return null;

  return (
    <div className="auth-modal-overlay" onClick={onClose}>
      <div className="auth-modal-container" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="auth-header">
          <h1 className="auth-main-title">Let's Sign in or Sign up here!!</h1>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        {/* Split Container */}
        <div className="auth-split-container">
          {/* Left Panel - Form */}
          <div className="auth-left-panel">
            <div className="auth-form-container">
              <h2 className="form-title">
                {isSignUp ? 'Create Account' : 'Welcome Back'}
              </h2>
              <p className="form-subtitle">
                {isSignUp 
                  ? 'Join us to explore mathematical graphs!' 
                  : 'Sign in to continue your mathematical journey'
                }
              </p>

              {error && <div className="error-message">{error}</div>}

              <form onSubmit={handleSubmit} className="auth-form">
                <div className="form-group">
                  <input
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleInputChange}
                    placeholder="Enter your username"
                    className="rounded-input"
                    required
                    disabled={isLoading}
                  />
                </div>

                {isSignUp && (
                  <div className="form-group">
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      placeholder="Enter your email"
                      className="rounded-input"
                      required
                      disabled={isLoading}
                    />
                  </div>
                )}

                <div className="form-group">
                  <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    placeholder="Enter your password"
                    className="rounded-input"
                    required
                    disabled={isLoading}
                  />
                </div>

                {isSignUp && (
                  <div className="form-group">
                    <input
                      type="password"
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleInputChange}
                      placeholder="Confirm your password"
                      className="rounded-input"
                      required
                      disabled={isLoading}
                    />
                  </div>
                )}

                {!isSignUp && (
                  <div className="form-options">
                    <label className="remember-me">
                      <input type="checkbox" />
                      Remember me
                    </label>
                    <a href="#" className="forgot-password">Forgot Password?</a>
                  </div>
                )}

                <button 
                  type="submit" 
                  className="gradient-button primary"
                  disabled={isLoading}
                >
                  {isLoading 
                    ? (isSignUp ? 'Creating Account...' : 'Signing In...') 
                    : (isSignUp ? 'Create Account' : 'Sign In')
                  }
                </button>
              </form>
            </div>
          </div>

          {/* Right Panel - Call to Action */}
          <div className="auth-right-panel">
            <div className="right-panel-content">
              <h2 className="right-panel-title">
                {isSignUp ? 'Already have an account?' : 'New to our platform?'}
              </h2>
              <p className="right-panel-description">
                {isSignUp 
                  ? 'Sign in to access your saved graphs and continue your mathematical exploration!'
                  : 'Join thousands of users exploring the beauty of mathematical visualization!'
                }
              </p>
              <button 
                onClick={toggleMode} 
                className="gradient-button secondary"
                disabled={isLoading}
              >
                {isSignUp ? 'Sign In' : 'Sign Up'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}