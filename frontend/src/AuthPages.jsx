import { useState, useEffect } from 'react';
import { Mail, Lock, CheckCircle, AlertCircle, ArrowLeft } from 'lucide-react';
import { API_URL } from './config';
import './AuthPages.css';

// Forgot Password Page
export function ForgotPassword({ onBack }) {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus(null);

    try {
      const response = await fetch(`${API_URL}/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();
      setStatus({ type: 'success', message: data.message || 'Check your email for reset instructions.' });
    } catch (error) {
      setStatus({ type: 'error', message: 'Failed to send reset email. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <button className="back-btn" onClick={onBack}>
          <ArrowLeft size={18} />
          Back to Login
        </button>
        
        <div className="auth-header">
          <Mail size={32} className="auth-icon" />
          <h2>Forgot Password</h2>
          <p>Enter your email and we'll send you a reset link</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              placeholder="your@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
            />
          </div>

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Sending...' : 'Send Reset Link'}
          </button>
        </form>

        {status && (
          <div className={`status-message ${status.type}`}>
            {status.type === 'success' ? <CheckCircle size={18} /> : <AlertCircle size={18} />}
            {status.message}
          </div>
        )}
      </div>
    </div>
  );
}

// Reset Password Page (accessed via email link)
export function ResetPassword({ token, onSuccess }) {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (password !== confirmPassword) {
      setStatus({ type: 'error', message: 'Passwords do not match' });
      return;
    }

    if (password.length < 8) {
      setStatus({ type: 'error', message: 'Password must be at least 8 characters' });
      return;
    }

    setLoading(true);
    setStatus(null);

    try {
      const response = await fetch(`${API_URL}/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password: password }),
      });

      if (response.ok) {
        setStatus({ type: 'success', message: 'Password reset successfully! You can now login.' });
        setTimeout(() => onSuccess?.(), 2000);
      } else {
        const data = await response.json();
        setStatus({ type: 'error', message: data.detail || 'Reset failed. Link may be expired.' });
      }
    } catch (error) {
      setStatus({ type: 'error', message: 'Failed to reset password. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-header">
          <Lock size={32} className="auth-icon" />
          <h2>Reset Password</h2>
          <p>Enter your new password</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="password">New Password</label>
            <input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
              minLength={8}
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirm-password">Confirm Password</label>
            <input
              id="confirm-password"
              type="password"
              placeholder="••••••••"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              disabled={loading}
            />
          </div>

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Resetting...' : 'Reset Password'}
          </button>
        </form>

        {status && (
          <div className={`status-message ${status.type}`}>
            {status.type === 'success' ? <CheckCircle size={18} /> : <AlertCircle size={18} />}
            {status.message}
          </div>
        )}
      </div>
    </div>
  );
}

// Email Verification Page (accessed via email link)
export function VerifyEmail({ token }) {
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState(null);

  useEffect(() => {
    verifyEmail();
  }, [token]);

  const verifyEmail = async () => {
    try {
      const response = await fetch(`${API_URL}/auth/verify-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token }),
      });

      if (response.ok) {
        setStatus({ type: 'success', message: 'Email verified successfully! You can now use all features.' });
      } else {
        const data = await response.json();
        setStatus({ type: 'error', message: data.detail || 'Verification failed. Link may be expired.' });
      }
    } catch (error) {
      setStatus({ type: 'error', message: 'Verification failed. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-header">
          {loading ? (
            <>
              <div className="loading-spinner"></div>
              <h2>Verifying Email...</h2>
              <p>Please wait while we verify your email address</p>
            </>
          ) : status?.type === 'success' ? (
            <>
              <CheckCircle size={48} className="auth-icon success" />
              <h2>Email Verified!</h2>
              <p>{status.message}</p>
              <a href="/" className="submit-btn" style={{ marginTop: '1rem', display: 'inline-block', textDecoration: 'none' }}>
                Go to Dashboard
              </a>
            </>
          ) : (
            <>
              <AlertCircle size={48} className="auth-icon error" />
              <h2>Verification Failed</h2>
              <p>{status?.message}</p>
              <a href="/" className="submit-btn secondary" style={{ marginTop: '1rem', display: 'inline-block', textDecoration: 'none' }}>
                Back to Home
              </a>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// Email Verification Banner (shown when logged in but not verified)
export function VerificationBanner({ email, onResend }) {
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const handleResend = async () => {
    setLoading(true);
    try {
      await onResend();
      setSent(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="verification-banner">
      <AlertCircle size={18} />
      <span>Please verify your email ({email}) to unlock all features.</span>
      {sent ? (
        <span className="sent-text">Email sent!</span>
      ) : (
        <button onClick={handleResend} disabled={loading}>
          {loading ? 'Sending...' : 'Resend Email'}
        </button>
      )}
    </div>
  );
}

export default { ForgotPassword, ResetPassword, VerifyEmail, VerificationBanner };
