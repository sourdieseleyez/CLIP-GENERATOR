import { useState } from 'react';
import { Mail, Lock, User, ArrowRight, Video, Sparkles, Eye, EyeOff } from 'lucide-react';
import { API_URL } from './config';
import './AuthPage.css';

// Streaming setup image for the left panel
const STREAMING_IMAGE = 'https://images.unsplash.com/photo-1598550476439-6847785fcea6?w=1200&q=80';

function AuthPage({ onAuthSuccess, initialMode = 'login', onNavigate }) {
  const [mode, setMode] = useState(initialMode);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleEmailAuth = async (e) => {
    e.preventDefault();
    
    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }

    if (mode === 'register' && password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      if (mode === 'register') {
        const response = await fetch(`${API_URL}/users/register?password=${encodeURIComponent(password)}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, name: name || email.split('@')[0] }),
        });

        const data = await response.json();

        if (response.ok) {
          setSuccess('Account created! Signing you in...');
          // Auto-login after registration
          await handleLogin(email, password);
        } else {
          setError(data.detail || 'Registration failed');
        }
      } else {
        await handleLogin(email, password);
      }
    } catch (err) {
      setError('Connection error. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (loginEmail, loginPassword) => {
    const params = new URLSearchParams();
    params.append('username', loginEmail);
    params.append('password', loginPassword);

    const response = await fetch(`${API_URL}/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: params.toString(),
    });

    const data = await response.json();

    if (response.ok) {
      onAuthSuccess(data.access_token, loginEmail);
    } else {
      throw new Error(data.detail || 'Login failed');
    }
  };

  const handleGoogleAuth = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Redirect to backend Google OAuth endpoint
      window.location.href = `${API_URL}/auth/google`;
    } catch (err) {
      setError('Google sign-in failed. Please try again.');
      setLoading(false);
    }
  };

  const handleGitHubAuth = async () => {
    setLoading(true);
    setError(null);
    
    try {
      window.location.href = `${API_URL}/auth/github`;
    } catch (err) {
      setError('GitHub sign-in failed. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      {/* Left Panel - Image */}
      <div className="auth-image-panel">
        <div 
          className="auth-image" 
          style={{ backgroundImage: `url(${STREAMING_IMAGE})` }}
        />
        <div className="auth-image-overlay" />
        <div className="auth-image-content">
          <div className="auth-brand">
            <Video size={32} />
            <span>ClipGen</span>
          </div>
          <h1>Transform Your Content</h1>
          <p>AI-powered clip generation for creators, streamers, and marketers.</p>
          <div className="auth-features">
            <div className="auth-feature">
              <Sparkles size={18} />
              <span>AI-Powered Analysis</span>
            </div>
            <div className="auth-feature">
              <Sparkles size={18} />
              <span>Auto-Generated Captions</span>
            </div>
            <div className="auth-feature">
              <Sparkles size={18} />
              <span>Multi-Platform Export</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel - Auth Form */}
      <div className="auth-form-panel">
        <div className="auth-form-container">
          <div className="auth-form-header">
            <h2>{mode === 'login' ? 'Welcome back' : 'Create your account'}</h2>
            <p>
              {mode === 'login' 
                ? 'Sign in to continue to ClipGen' 
                : 'Start generating viral clips today'}
            </p>
          </div>

          {/* Social Auth Buttons */}
          <div className="social-auth-buttons">
            <button 
              className="social-btn google-btn" 
              onClick={handleGoogleAuth}
              disabled={loading}
            >
              <svg viewBox="0 0 24 24" width="20" height="20">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              <span>Continue with Google</span>
            </button>

            <button 
              className="social-btn github-btn" 
              onClick={handleGitHubAuth}
              disabled={loading}
            >
              <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
              <span>Continue with GitHub</span>
            </button>
          </div>

          <div className="auth-divider">
            <span>or continue with email</span>
          </div>

          {/* Email/Password Form */}
          <form onSubmit={handleEmailAuth} className="auth-form">
            {mode === 'register' && (
              <div className="form-field">
                <label htmlFor="name">
                  <User size={16} />
                  Name
                </label>
                <input
                  id="name"
                  type="text"
                  placeholder="Your name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  disabled={loading}
                />
              </div>
            )}

            <div className="form-field">
              <label htmlFor="email">
                <Mail size={16} />
                Email
              </label>
              <input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
                required
              />
            </div>

            <div className="form-field">
              <label htmlFor="password">
                <Lock size={16} />
                Password
              </label>
              <div className="password-input-wrapper">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={loading}
                  required
                  minLength={8}
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {mode === 'register' && (
                <span className="field-hint">Must be at least 8 characters</span>
              )}
            </div>

            {mode === 'login' && (
              <div className="forgot-password">
                <a href="#forgot">Forgot password?</a>
              </div>
            )}

            {error && (
              <div className="auth-message error">
                {error}
              </div>
            )}

            {success && (
              <div className="auth-message success">
                {success}
              </div>
            )}

            <button 
              type="submit" 
              className="auth-submit-btn"
              disabled={loading}
            >
              {loading ? (
                <span className="loading-spinner" />
              ) : (
                <>
                  {mode === 'login' ? 'Sign In' : 'Create Account'}
                  <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>

          <div className="auth-switch">
            {mode === 'login' ? (
              <p>
                Don't have an account?{' '}
                <button onClick={() => { setMode('register'); setError(null); }}>
                  Sign up
                </button>
              </p>
            ) : (
              <p>
                Already have an account?{' '}
                <button onClick={() => { setMode('login'); setError(null); }}>
                  Sign in
                </button>
              </p>
            )}
          </div>

          <div className="auth-terms">
            <p>
              By continuing, you agree to our{' '}
              <button type="button" onClick={() => onNavigate?.('terms')} className="auth-link">Terms of Service</button> and{' '}
              <button type="button" onClick={() => onNavigate?.('privacy')} className="auth-link">Privacy Policy</button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AuthPage;
