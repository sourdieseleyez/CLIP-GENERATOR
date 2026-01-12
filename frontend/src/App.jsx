import { useState, useEffect } from 'react';
import { 
  Upload, 
  Link, 
  Video, 
  Play,
  Download,
  LogOut,
  Sparkles,
  Youtube,
  User,
  UserPlus,
  Home,
  Settings,
  BarChart3,
  Library,
  Briefcase,
  CreditCard,
  Shield,
  Coins
} from 'lucide-react';
import './App.css';
import { API_URL, UI_CONFIG, DISABLE_AUTH } from './config';
import CustomSelect from './CustomSelect';
import Dashboard from './Dashboard';
import ClipsLibrary from './ClipsLibrary';
import Marketplace from './Marketplace';
import CreateCampaign from './CreateCampaign';
import SubmitJob from './SubmitJob';
import Pricing from './Pricing';
import AdminDashboard from './AdminDashboard';
import { ForgotPassword, ResetPassword, VerifyEmail, VerificationBanner } from './AuthPages';
import AuthPage from './AuthPage';
import LandingPage from './LandingPage';
import TermsOfService from './TermsOfService';
import PrivacyPolicy from './PrivacyPolicy';
import Contact from './Contact';
import Documentation from './Documentation';

function App() {
  // Check if we're in development mode
  const isDev = import.meta.env.DEV;
  
  // Navigation state - start with landing page for non-logged-in users
  const [currentPage, setCurrentPage] = useState('landing');
  
  // Auth state
  const [authMode, setAuthMode] = useState('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState('');
  const [userEmail, setUserEmail] = useState('');
  const [authStatus, setAuthStatus] = useState(null);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  
  // User profile state
  const [userProfile, setUserProfile] = useState(null);
  const [userCredits, setUserCredits] = useState(null);
  
  // Video input state
  const [inputType, setInputType] = useState('upload');
  const [file, setFile] = useState(null);
  const [videoUrl, setVideoUrl] = useState('');
  
  // Clip options
  const [numClips, setNumClips] = useState(5);
  const [clipDuration, setClipDuration] = useState(30);
  const [resolution, setResolution] = useState('portrait');
  
  // Marketplace job context
  const [activeJob, setActiveJob] = useState(null);
  
  // Processing state
  const [loading, setLoading] = useState(false);
  const [processingStatus, setProcessingStatus] = useState(null);
  const [clips, setClips] = useState([]);
  const [captions, setCaptions] = useState({ srt: null, vtt: null });

  // Auto-login when frontend DISABLE_AUTH is enabled (local dev)
  useEffect(() => {
    if (DISABLE_AUTH) {
      // set a dummy token and user email; backend should accept any token when DISABLE_AUTH is enabled
      setToken('dev-token');
      setUserEmail('dev@localhost');
    }
    
    // Check if user came from landing page signup
    const signupEmail = sessionStorage.getItem('signupEmail');
    if (signupEmail) {
      sessionStorage.removeItem('signupEmail');
      setEmail(signupEmail);
      setAuthMode('register');
      setCurrentPage('auth');
    }
    
    // Check URL for email verification or password reset
    const urlParams = new URLSearchParams(window.location.search);
    const verifyToken = urlParams.get('verify');
    const resetToken = urlParams.get('reset');
    
    if (verifyToken) {
      setCurrentPage('verify-email');
    } else if (resetToken) {
      setCurrentPage('reset-password');
    }
  }, []);
  
  // Fetch user profile when logged in
  useEffect(() => {
    if (token && token !== 'dev-token') {
      fetchUserProfile();
    }
  }, [token]);
  
  const fetchUserProfile = async () => {
    try {
      const response = await fetch(`${API_URL}/user/profile`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setUserProfile(data);
        setUserCredits(data.credits);
      }
    } catch (error) {
      console.error('Failed to fetch profile:', error);
    }
  };
  
  const handleResendVerification = async () => {
    try {
      await fetch(`${API_URL}/auth/resend-verification`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
    } catch (error) {
      console.error('Failed to resend verification:', error);
    }
  };

  // Check if form is ready to submit
  const isFormReady = () => {
    if (!token) return false;
    if (inputType === 'upload' && file) return true;
    if ((inputType === 'youtube' || inputType === 'url') && videoUrl.trim()) return true;
    return false;
  };

  const handleAuth = async () => {
    if (!email || !password) {
      setAuthStatus({ type: 'error', message: 'Please fill in all fields' });
      return;
    }

    setLoading(true);
    setAuthStatus(null);

    try {
      if (authMode === 'register') {
        const response = await fetch(`${API_URL}/users/register?password=${password}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email }),
        });

        const data = await response.json();

        if (response.ok) {
          setAuthStatus({ type: 'success', message: 'Account created! Now login.' });
          setAuthMode('login');
          setPassword('');
        } else {
          setAuthStatus({ type: 'error', message: data.detail || 'Registration failed' });
        }
      } else {
        // OAuth2 expects application/x-www-form-urlencoded
        const params = new URLSearchParams();
        params.append('username', email);
        params.append('password', password);

        const response = await fetch(`${API_URL}/token`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: params.toString(),
        });

        const data = await response.json();

        if (response.ok) {
          setToken(data.access_token);
          setUserEmail(email);
          setAuthStatus({ type: 'success', message: 'Logged in successfully' });
          setEmail('');
          setPassword('');
          setShowAuthModal(false);
        } else {
          setAuthStatus({ type: 'error', message: data.detail || 'Login failed' });
        }
      }
    } catch (error) {
      setAuthStatus({ type: 'error', message: 'Connection error. Is the backend running?' });
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setToken('');
    setUserEmail('');
    setClips([]);
    setAuthStatus(null);
  };

  const handleDevLogin = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/dev/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) {
        throw new Error('Dev login failed');
      }

      const data = await response.json();
      setToken(data.access_token);
      setUserEmail(data.email);
      setAuthStatus({ type: 'success', message: 'Dev mode activated!' });
      setCurrentPage('dashboard');
    } catch (error) {
      setAuthStatus({ type: 'error', message: 'Dev login failed. Make sure backend is running.' });
    } finally {
      setLoading(false);
    }
  };

  const handleSeedData = async () => {
    if (!token) {
      alert('Please login first');
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/dev/seed-data`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to seed data');
      }

      const data = await response.json();
      alert(`✓ Created ${data.clips_created} sample clips! Check Dashboard and Clips Library.`);
      setCurrentPage('dashboard');
    } catch (error) {
      alert('Failed to seed data. Make sure you are logged in and database is configured.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
  };

  const handleProcessVideo = async () => {
    if (!token) {
      setProcessingStatus({ type: 'error', message: 'Please login first' });
      return;
    }

    if (inputType === 'upload' && !file) {
      setProcessingStatus({ type: 'error', message: 'Please select a video file' });
      return;
    }

    if ((inputType === 'youtube' || inputType === 'url') && !videoUrl) {
      setProcessingStatus({ type: 'error', message: 'Please enter a video URL' });
      return;
    }

    setLoading(true);
    setProcessingStatus({ type: 'info', message: 'Uploading and processing video...' });
    setClips([]);

    try {
      let videoId = null;

      // Step 1: Upload file if needed
      if (inputType === 'upload') {
        const formData = new FormData();
        formData.append('file', file);

        const uploadResponse = await fetch(`${API_URL}/videos/upload`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          body: formData,
        });

        if (!uploadResponse.ok) {
          const error = await uploadResponse.json();
          throw new Error(error.detail || 'Upload failed');
        }

        const uploadData = await uploadResponse.json();
        videoId = uploadData.video_id;
        setProcessingStatus({ type: 'info', message: 'Video uploaded. Starting processing...' });
      }

      // Step 2: Start processing
      const processResponse = await fetch(`${API_URL}/videos/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          video_source: inputType,
          video_id: videoId,
          video_url: videoUrl || null,
          num_clips: numClips,
          clip_duration: clipDuration,
          resolution: resolution
        }),
      });

      if (!processResponse.ok) {
        const error = await processResponse.json();
        throw new Error(error.detail || 'Processing failed');
      }

      const processData = await processResponse.json();
      const jobId = processData.job_id;

      // Step 3: Poll for job status
      setProcessingStatus({ type: 'info', message: 'Processing video... This may take a few minutes.' });
      
      const pollInterval = setInterval(async () => {
        try {
          const statusResponse = await fetch(`${API_URL}/jobs/${jobId}`, {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });

          if (!statusResponse.ok) {
            clearInterval(pollInterval);
            throw new Error('Failed to check status');
          }

          const statusData = await statusResponse.json();

          if (statusData.status === 'completed') {
            clearInterval(pollInterval);
            const generatedClips = statusData.result.clips.map((clip, index) => ({
              id: clip.clip_number,
              start: clip.start_time,
              end: clip.end_time,
              text: clip.text,
              reason: clip.reason,
              path: clip.path,
              url: clip.url || null
            }));
            setClips(generatedClips);
            // Captions: prefer presigned URLs returned by backend (srt_url / vtt_url)
            setCaptions({
              srt: statusData.result.srt_url || null,
              vtt: statusData.result.vtt_url || null
            });
            setProcessingStatus({ type: 'success', message: `Generated ${generatedClips.length} clips successfully!` });
            setLoading(false);
          } else if (statusData.status === 'failed') {
            clearInterval(pollInterval);
            throw new Error(statusData.error || 'Processing failed');
          } else {
            setProcessingStatus({ 
              type: 'info', 
              message: `${statusData.message || 'Processing...'} (${statusData.progress}%)` 
            });
          }
        } catch (error) {
          clearInterval(pollInterval);
          setProcessingStatus({ type: 'error', message: error.message });
          setLoading(false);
        }
      }, 3000); // Poll every 3 seconds

    } catch (error) {
      setProcessingStatus({ type: 'error', message: error.message || 'Processing failed. Please try again.' });
      setLoading(false);
    }
  };

  const handleDownloadClip = async (clipId) => {
    try {
      const response = await fetch(`${API_URL}/clips/${clipId}/download`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Download failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `clip_${clipId}.mp4`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      setProcessingStatus({ type: 'error', message: 'Download failed. Please try again.' });
    }
  };



  // Handle navigation from landing page
  const handleLandingNavigate = (page) => {
    setCurrentPage(page);
  };

  // Handle "Get Started" from landing page
  const handleGetStarted = () => {
    setCurrentPage('auth');
    setAuthMode('register');
  };

  // Render landing page and related pages (terms, privacy, contact, docs, auth)
  if (currentPage === 'landing' || currentPage === 'terms' || currentPage === 'privacy' || currentPage === 'contact' || currentPage === 'docs' || currentPage === 'auth') {
    if (currentPage === 'landing') {
      return <LandingPage onGetStarted={handleGetStarted} onNavigate={handleLandingNavigate} />;
    }
    if (currentPage === 'auth') {
      return (
        <AuthPage 
          onAuthSuccess={(accessToken, userEmailAddr) => {
            setToken(accessToken);
            setUserEmail(userEmailAddr);
            setCurrentPage('dashboard');
          }}
          initialMode={authMode}
        />
      );
    }
    if (currentPage === 'terms') {
      return <TermsOfService onBack={() => setCurrentPage('landing')} />;
    }
    if (currentPage === 'privacy') {
      return <PrivacyPolicy onBack={() => setCurrentPage('landing')} />;
    }
    if (currentPage === 'contact') {
      return <Contact onBack={() => setCurrentPage('landing')} />;
    }
    if (currentPage === 'docs') {
      return <Documentation onBack={() => setCurrentPage('landing')} />;
    }
  }

  return (
    <div className="App">
      {/* Dev Mode Banner */}
      {isDev && (
        <div className="dev-banner">
          <Sparkles size={14} />
          <span>Development Mode</span>
        </div>
      )}
      
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand" onClick={() => !token && setCurrentPage('landing')} style={{ cursor: !token ? 'pointer' : 'default' }}>
          <Video size={20} />
          <span>ClipGen</span>
        </div>

        <nav className="sidebar-nav">
          {token ? (
            <>
              <button 
                className={`nav-item ${currentPage === 'dashboard' ? 'active' : ''}`}
                onClick={() => setCurrentPage('dashboard')}
              >
                <BarChart3 size={18} />
                <span>Analytics</span>
              </button>
              
              <button 
                className={`nav-item ${currentPage === 'marketplace' ? 'active' : ''}`}
                onClick={() => setCurrentPage('marketplace')}
              >
                <Briefcase size={18} />
                <span>Marketplace</span>
              </button>
              
              <button 
                className={`nav-item ${currentPage === 'library' ? 'active' : ''}`}
                onClick={() => setCurrentPage('library')}
              >
                <Library size={18} />
                <span>Clips Library</span>
              </button>
              
              <button 
                className={`nav-item ${currentPage === 'generate' ? 'active' : ''}`}
                onClick={() => setCurrentPage('generate')}
              >
                <Sparkles size={18} />
                <span>Generate Clips</span>
              </button>
              
              <button 
                className={`nav-item ${currentPage === 'pricing' ? 'active' : ''}`}
                onClick={() => setCurrentPage('pricing')}
              >
                <CreditCard size={18} />
                <span>Get Credits</span>
              </button>
              
              <div className="nav-divider"></div>
              
              {/* Credits display */}
              <div className="nav-item credits-display">
                <Coins size={18} />
                <span>{userCredits !== null ? `${userCredits} credits` : '...'}</span>
              </div>
              
              <div className="nav-item user-item">
                <User size={18} />
                <span className="user-email-nav">{userEmail}</span>
              </div>
              
              {/* Admin link */}
              {userProfile?.is_admin && (
                <button 
                  className={`nav-item ${currentPage === 'admin' ? 'active' : ''}`}
                  onClick={() => setCurrentPage('admin')}
                >
                  <Shield size={18} />
                  <span>Admin</span>
                </button>
              )}
              
              {isDev && (
                <button className="nav-item dev-seed-btn" onClick={handleSeedData}>
                  <Sparkles size={18} />
                  <span>Seed Sample Data</span>
                </button>
              )}
              
              <button className="nav-item" onClick={handleLogout}>
                <LogOut size={18} />
                <span>Logout</span>
              </button>
            </>
          ) : (
            <>
              <button 
                className={`nav-item ${currentPage === 'generate' ? 'active' : ''}`}
                onClick={() => setCurrentPage('generate')}
              >
                <Home size={18} />
                <span>Home</span>
              </button>
              
              <button className="nav-item" onClick={() => { setAuthMode('login'); setCurrentPage('auth'); }}>
                <User size={18} />
                <span>Login</span>
              </button>
              <button className="nav-item" onClick={() => { setAuthMode('register'); setCurrentPage('auth'); }}>
                <UserPlus size={18} />
                <span>Sign Up</span>
              </button>
              
              {isDev && (
                <>
                  <div className="nav-divider"></div>
                  <button className="nav-item dev-login-btn" onClick={handleDevLogin}>
                    <Sparkles size={18} />
                    <span>Dev Login</span>
                  </button>
                </>
              )}
            </>
          )}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {/* Email verification banner */}
        {token && userProfile && !userProfile.email_verified && !userProfile.is_dev_mode && (
          <VerificationBanner 
            email={userEmail} 
            onResend={handleResendVerification}
          />
        )}
        
        {/* Auth pages (no sidebar needed) */}
        {currentPage === 'verify-email' && (
          <VerifyEmail token={new URLSearchParams(window.location.search).get('verify')} />
        )}
        
        {currentPage === 'reset-password' && (
          <ResetPassword 
            token={new URLSearchParams(window.location.search).get('reset')}
            onSuccess={() => {
              window.history.replaceState({}, '', '/');
              setAuthMode('login');
              setCurrentPage('auth');
            }}
          />
        )}
        
        {currentPage === 'forgot-password' && (
          <ForgotPassword onBack={() => {
            setAuthMode('login');
            setCurrentPage('auth');
          }} />
        )}
        
        {/* Render different pages based on currentPage */}
        {currentPage === 'dashboard' && token && (
          <Dashboard token={token} />
        )}
        
        {currentPage === 'marketplace' && token && (
          <Marketplace 
            token={token} 
            onStartJob={(job, campaign) => {
              setActiveJob({ job, campaign });
              setVideoUrl(campaign.video_url);
              setNumClips(campaign.num_clips_needed);
              setClipDuration(campaign.clip_duration);
              setResolution(campaign.resolution);
              setInputType('url');
              setCurrentPage('generate');
            }}
          />
        )}
        
        {currentPage === 'create-campaign' && token && (
          <CreateCampaign token={token} onSuccess={() => setCurrentPage('marketplace')} />
        )}
        
        {currentPage === 'submit-job' && token && activeJob && (
          <SubmitJob 
            token={token} 
            job={activeJob} 
            clips={clips}
            onSuccess={() => {
              setActiveJob(null);
              setClips([]);
              setCurrentPage('marketplace');
            }}
          />
        )}
        
        {currentPage === 'library' && token && (
          <ClipsLibrary token={token} />
        )}
        
        {currentPage === 'pricing' && token && (
          <Pricing token={token} />
        )}
        
        {currentPage === 'admin' && token && userProfile?.is_admin && (
          <AdminDashboard token={token} />
        )}
        
        {currentPage === 'generate' && (
          <>
        {/* Video Input Section */}
        <section className="video-input-section">
          <h2>
            <Upload size={16} />
            Video Source
          </h2>
          
          <div className="input-type-selector">
            <div
              className={`input-type-btn ${inputType === 'upload' ? 'active' : ''}`}
              onClick={() => setInputType('upload')}
            >
              <div className="icon">
                <Upload size={20} />
              </div>
              <div className="label">Upload File</div>
            </div>
            <div
              className={`input-type-btn ${inputType === 'youtube' ? 'active' : ''}`}
              onClick={() => setInputType('youtube')}
            >
              <div className="icon">
                <Youtube size={20} />
              </div>
              <div className="label">YouTube URL</div>
            </div>
            <div
              className={`input-type-btn ${inputType === 'url' ? 'active' : ''}`}
              onClick={() => setInputType('url')}
            >
              <div className="icon">
                <Link size={20} />
              </div>
              <div className="label">Direct URL</div>
            </div>
          </div>

          {inputType === 'upload' && (
            <div className="file-input-wrapper">
              <input
                id="file-upload"
                type="file"
                accept="video/*"
                onChange={handleFileChange}
                disabled={loading}
              />
              <label htmlFor="file-upload" className="file-input-label">
                <Upload size={18} />
                <span>{file ? file.name : 'Choose Video File'}</span>
              </label>
              {file && (
                <div className="file-name">
                  {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                </div>
              )}
            </div>
          )}

          {(inputType === 'youtube' || inputType === 'url') && (
            <div className="form-group">
              <label htmlFor="video-url">
                {inputType === 'youtube' ? 'YouTube Video URL' : 'Direct Video URL'}
              </label>
              <input
                id="video-url"
                type="url"
                placeholder={inputType === 'youtube' ? 'https://youtube.com/watch?v=...' : 'https://example.com/video.mp4'}
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                disabled={loading}
              />
            </div>
          )}
        </section>

        {/* Clip Options */}
        <section className="clip-options">
          <div className="option-group">
            <label htmlFor="num-clips">Number of Clips</label>
            <CustomSelect
              value={numClips}
              onChange={(e) => setNumClips(Number(e.target.value))}
              disabled={loading}
              options={[
                { value: 3, label: '3 clips' },
                { value: 5, label: '5 clips' },
                { value: 8, label: '8 clips' },
                { value: 10, label: '10 clips' }
              ]}
            />
          </div>

          <div className="option-group">
            <label htmlFor="clip-duration">Clip Duration</label>
            <CustomSelect
              value={clipDuration}
              onChange={(e) => setClipDuration(Number(e.target.value))}
              disabled={loading}
              options={[
                { value: 15, label: '15 seconds' },
                { value: 30, label: '30 seconds' },
                { value: 45, label: '45 seconds' },
                { value: 60, label: '60 seconds' }
              ]}
            />
          </div>

          <div className="option-group">
            <label htmlFor="resolution">Format</label>
            <CustomSelect
              value={resolution}
              onChange={(e) => setResolution(e.target.value)}
              disabled={loading}
              options={[
                { value: 'portrait', label: 'Portrait (9:16)' },
                { value: 'landscape', label: 'Landscape (16:9)' },
                { value: 'square', label: 'Square (1:1)' }
              ]}
            />
          </div>
        </section>

        {/* Process Button */}
        <section className="process-section">
          <button
            className={`process-btn ${isFormReady() ? 'ready' : ''} ${loading ? 'loading' : ''}`}
            onClick={handleProcessVideo}
            disabled={loading || !isFormReady()}
          >
            <Sparkles size={16} className="sparkle-icon" />
            {loading ? 'Processing...' : 'Generate Clips'}
          </button>

          {processingStatus && (
            <div className={`status-message status-${processingStatus.type}`}>
              {processingStatus.message}
            </div>
          )}
        </section>

        {/* Results */}
        {clips.length > 0 && (
          <section className="results-section">
            <div className="results-header">
              <h3>Generated Clips</h3>
              {activeJob && (
                <button 
                  className="submit-job-btn"
                  onClick={() => setCurrentPage('submit-job')}
                >
                  Submit to Campaign
                </button>
              )}
            </div>
            <div className="clips-grid">
              {clips.map((clip) => (
                <div key={clip.id} className="clip-card">
                  <div className="clip-preview">
                        {/* Try to show preview video if available (prefers served URL or backend download endpoint) */}
                        {clip.url ? (
                          <video src={clip.url} controls width={240} />
                        ) : (
                          <video src={`${API_URL}/clips/${clip.id}/download`} controls width={240} />
                        )}
                  </div>
                  <div className="clip-info">
                    Clip #{clip.id} • {clip.start}s - {clip.end}s
                  </div>
                  <div className="clip-text">
                    "{clip.text}"
                  </div>
                  <button className="download-btn" onClick={() => handleDownloadClip(clip.id)}>
                    <Download size={14} />
                    Download Clip
                  </button>
                  <div style={{marginTop: 8}}>
                    {captions.vtt && (
                      <a href={captions.vtt} target="_blank" rel="noreferrer">Download captions (VTT)</a>
                    )}
                    {!captions.vtt && captions.srt && (
                      <a href={captions.srt} target="_blank" rel="noreferrer">Download captions (SRT)</a>
                    )}
                    {!captions.srt && !captions.vtt && (
                      <small style={{display: 'block', marginTop: 6}}>No captions available for this job.</small>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;
