import { useState, useEffect, useMemo } from 'react';
import { 
  BarChart3, TrendingUp, TrendingDown, DollarSign, Video, Eye, 
  Zap, Target, Award, Clock, ArrowUpRight, ArrowDownRight,
  Play, Flame, Crown, Star, Activity, PieChart, Calendar, AlertCircle,
  Coins, Upload, Plus, Briefcase, HardDrive, Sparkles, ChevronRight,
  CheckCircle, XCircle, Loader, RefreshCw, ArrowRight
} from 'lucide-react';
import './Dashboard.css';
import { API_URL, formatFileSize } from './config';

// Mini sparkline component
function Sparkline({ data, color = 'var(--accent-primary)', height = 32 }) {
  if (!data || data.length < 2) return null;
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  const points = data.map((val, i) => {
    const x = (i / (data.length - 1)) * 100;
    const y = 100 - ((val - min) / range) * 100;
    return `${x},${y}`;
  }).join(' ');
  
  return (
    <svg viewBox="0 0 100 100" preserveAspectRatio="none" style={{ width: '100%', height }}>
      <polyline points={points} fill="none" stroke={color} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

// Progress ring component
function ProgressRing({ progress, size = 60, strokeWidth = 6, color = 'var(--accent-primary)' }) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (progress / 100) * circumference;
  
  return (
    <svg width={size} height={size} className="progress-ring">
      <circle stroke="var(--border-primary)" fill="transparent" strokeWidth={strokeWidth} r={radius} cx={size / 2} cy={size / 2} />
      <circle stroke={color} fill="transparent" strokeWidth={strokeWidth} strokeLinecap="round"
        strokeDasharray={circumference} strokeDashoffset={offset} r={radius} cx={size / 2} cy={size / 2}
        style={{ transform: 'rotate(-90deg)', transformOrigin: '50% 50%', transition: 'stroke-dashoffset 0.5s ease' }} />
    </svg>
  );
}

// Job status badge component
function JobStatusBadge({ status }) {
  const config = {
    queued: { icon: Clock, color: 'var(--warning)', bg: 'var(--warning-bg)', label: 'Queued' },
    processing: { icon: Loader, color: 'var(--info)', bg: 'var(--info-bg)', label: 'Processing' },
    completed: { icon: CheckCircle, color: 'var(--success)', bg: 'var(--success-bg)', label: 'Completed' },
    failed: { icon: XCircle, color: 'var(--error)', bg: 'var(--error-bg)', label: 'Failed' }
  };
  const { icon: Icon, color, bg, label } = config[status] || config.queued;
  
  return (
    <span className="job-status-badge" style={{ background: bg, color }}>
      <Icon size={12} className={status === 'processing' ? 'spin' : ''} />
      {label}
    </span>
  );
}

function Dashboard({ token, onNavigate }) {
  const [analytics, setAnalytics] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const [userLimits, setUserLimits] = useState(null);
  const [recentJobs, setRecentJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('30d');

  useEffect(() => {
    fetchAllData();
  }, [token, timeRange]);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      
      // Fetch all data in parallel
      const [analyticsRes, profileRes, limitsRes, jobsRes] = await Promise.all([
        fetch(`${API_URL}/analytics/dashboard`, { headers: { 'Authorization': `Bearer ${token}` } }),
        fetch(`${API_URL}/user/profile`, { headers: { 'Authorization': `Bearer ${token}` } }),
        fetch(`${API_URL}/user/limits`, { headers: { 'Authorization': `Bearer ${token}` } }),
        fetch(`${API_URL}/clips?limit=50`, { headers: { 'Authorization': `Bearer ${token}` } }).catch(() => ({ ok: false }))
      ]);

      if (analyticsRes.ok) setAnalytics(await analyticsRes.json());
      if (profileRes.ok) setUserProfile(await profileRes.json());
      if (limitsRes.ok) setUserLimits(await limitsRes.json());
      
      // Extract recent jobs from clips or use empty array
      if (jobsRes.ok) {
        const clipsData = await jobsRes.json();
        // Group by job_id to get unique jobs
        const jobMap = new Map();
        (clipsData.clips || []).forEach(clip => {
          if (clip.job_id && !jobMap.has(clip.job_id)) {
            jobMap.set(clip.job_id, {
              job_id: clip.job_id,
              created_at: clip.created_at,
              clips_count: 1,
              status: 'completed'
            });
          } else if (clip.job_id) {
            jobMap.get(clip.job_id).clips_count++;
          }
        });
        setRecentJobs(Array.from(jobMap.values()).slice(0, 5));
      }
      
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Calculate derived metrics
  const metrics = useMemo(() => {
    if (!analytics) return null;
    const { summary, recent_activity } = analytics;
    const engagementRate = summary.total_clips > 0 ? (summary.total_views / summary.total_clips / 1000).toFixed(1) : 0;
    const rpm = summary.total_views > 0 ? ((summary.total_revenue / summary.total_views) * 1000).toFixed(2) : 0;
    const viewsGrowth = recent_activity.views_gained > 0 ? 12.5 : 0;
    const revenueGrowth = recent_activity.revenue_earned > 0 ? 8.3 : 0;
    return { engagementRate, rpm, viewsGrowth, revenueGrowth };
  }, [analytics]);

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"><Activity size={32} className="spin" /></div>
        <p className="loading-text">Loading your stats...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <div className="error-icon"><AlertCircle size={32} /></div>
        <h3>Failed to load dashboard</h3>
        <p>{error}</p>
        <button onClick={fetchAllData} className="retry-btn"><RefreshCw size={16} /> Retry</button>
      </div>
    );
  }

  const { summary, platform_stats, category_stats, top_clips, recent_activity } = analytics || {
    summary: { total_clips: 0, total_views: 0, total_revenue: 0, avg_views_per_clip: 0, avg_revenue_per_clip: 0 },
    platform_stats: {}, category_stats: {}, top_clips: [], recent_activity: { clips_created: 0, views_gained: 0, revenue_earned: 0 }
  };

  const isPaidUser = userProfile?.subscription_plan && userProfile.subscription_plan !== 'free';

  return (
    <div className="dashboard">
      {/* Top Bar - Account Summary + Quick Actions */}
      <div className="dashboard-top-bar">
        {/* Account Card */}
        <div className="account-card">
          <div className="account-info">
            <div className="account-avatar">
              {userProfile?.email?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="account-details">
              <span className="account-email">{userProfile?.email || 'User'}</span>
              <span className={`plan-badge ${userProfile?.subscription_plan || 'free'}`}>
                {(userProfile?.subscription_plan || 'free').toUpperCase()}
              </span>
            </div>
          </div>
          <div className="account-stats">
            <div className="account-stat">
              <Coins size={16} />
              <span className="stat-num">{userProfile?.credits || 0}</span>
              <span className="stat-label">Credits</span>
            </div>
            <div className="account-stat">
              <HardDrive size={16} />
              <span className="stat-num">{userLimits?.max_file_size_display || '500MB'}</span>
              <span className="stat-label">Upload Limit</span>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="quick-actions">
          <button className="quick-action-btn primary" onClick={() => onNavigate?.('generate')}>
            <Plus size={18} />
            <span>New Clip Job</span>
          </button>
          <button className="quick-action-btn" onClick={() => onNavigate?.('clips')}>
            <Video size={18} />
            <span>Clips Library</span>
          </button>
          <button className="quick-action-btn" onClick={() => onNavigate?.('marketplace')}>
            <Briefcase size={18} />
            <span>Marketplace</span>
          </button>
        </div>

        {/* Upgrade CTA for free users */}
        {!isPaidUser && (
          <div className="upgrade-cta">
            <div className="upgrade-content">
              <Sparkles size={20} />
              <div className="upgrade-text">
                <span className="upgrade-title">Upgrade to Pro</span>
                <span className="upgrade-desc">5GB uploads • Unlimited clips</span>
              </div>
            </div>
            <button className="upgrade-btn" onClick={() => onNavigate?.('pricing')}>
              Upgrade <ArrowRight size={14} />
            </button>
          </div>
        )}
      </div>

      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <div className="header-title">
            <h1><Zap size={28} className="header-icon" /> Dashboard</h1>
            <p className="header-subtitle">Track your clip empire</p>
          </div>
          <div className="header-actions">
            <div className="time-selector">
              {['7d', '30d', '90d', 'all'].map((range) => (
                <button key={range} className={`time-btn ${timeRange === range ? 'active' : ''}`}
                  onClick={() => setTimeRange(range)}>
                  {range === 'all' ? 'All Time' : range}
                </button>
              ))}
            </div>
            <button className="refresh-btn" onClick={fetchAllData} title="Refresh data">
              <RefreshCw size={16} />
            </button>
          </div>
        </div>
      </header>

      {/* Main Stats Grid */}
      <section className="stats-section">
        <div className="stats-grid">
          {/* Total Clips */}
          <div className="stat-card stat-clips">
            <div className="stat-header">
              <div className="stat-icon-wrapper clips"><Video size={20} /></div>
              <span className="stat-label">Total Clips</span>
            </div>
            <div className="stat-body">
              <div className="stat-value">{summary.total_clips.toLocaleString()}</div>
              <div className="stat-trend positive">
                <ArrowUpRight size={14} />
                <span>+{recent_activity.clips_created} this month</span>
              </div>
            </div>
            <div className="stat-sparkline">
              <Sparkline data={[12, 19, 15, 25, 22, 30, 28]} color="var(--accent-secondary)" />
            </div>
          </div>

          {/* Total Views */}
          <div className="stat-card stat-views">
            <div className="stat-header">
              <div className="stat-icon-wrapper views"><Eye size={20} /></div>
              <span className="stat-label">Total Views</span>
            </div>
            <div className="stat-body">
              <div className="stat-value">
                {summary.total_views >= 1000000 ? `${(summary.total_views / 1000000).toFixed(1)}M`
                  : summary.total_views >= 1000 ? `${(summary.total_views / 1000).toFixed(1)}K`
                  : summary.total_views.toLocaleString()}
              </div>
              <div className={`stat-trend ${metrics?.viewsGrowth >= 0 ? 'positive' : 'negative'}`}>
                {metrics?.viewsGrowth >= 0 ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                <span>{metrics?.viewsGrowth >= 0 ? '+' : ''}{metrics?.viewsGrowth}% vs last period</span>
              </div>
            </div>
            <div className="stat-sparkline">
              <Sparkline data={[45, 52, 38, 65, 72, 58, 85]} color="var(--accent-tertiary)" />
            </div>
          </div>

          {/* Total Revenue */}
          <div className="stat-card stat-revenue featured">
            <div className="stat-header">
              <div className="stat-icon-wrapper revenue"><DollarSign size={20} /></div>
              <span className="stat-label">Total Revenue</span>
            </div>
            <div className="stat-body">
              <div className="stat-value">${summary.total_revenue.toLocaleString()}</div>
              <div className={`stat-trend ${metrics?.revenueGrowth >= 0 ? 'positive' : 'negative'}`}>
                {metrics?.revenueGrowth >= 0 ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                <span>${recent_activity.revenue_earned} this month</span>
              </div>
            </div>
            <div className="stat-sparkline">
              <Sparkline data={[20, 35, 28, 45, 42, 55, 68]} color="var(--accent-primary)" />
            </div>
          </div>

          {/* RPM */}
          <div className="stat-card stat-rpm">
            <div className="stat-header">
              <div className="stat-icon-wrapper rpm"><Target size={20} /></div>
              <span className="stat-label">RPM</span>
            </div>
            <div className="stat-body">
              <div className="stat-value">${metrics?.rpm}</div>
              <div className="stat-meta">Revenue per 1K views</div>
            </div>
            <div className="stat-progress">
              <ProgressRing progress={Math.min((metrics?.rpm / 10) * 100, 100)} color="var(--warning)" />
            </div>
          </div>
        </div>
      </section>

      {/* Secondary Stats Row */}
      <section className="secondary-stats">
        <div className="mini-stat">
          <div className="mini-stat-icon"><TrendingUp size={18} /></div>
          <div className="mini-stat-content">
            <span className="mini-stat-value">{summary.avg_views_per_clip.toLocaleString()}</span>
            <span className="mini-stat-label">Avg Views/Clip</span>
          </div>
        </div>
        <div className="mini-stat">
          <div className="mini-stat-icon"><DollarSign size={18} /></div>
          <div className="mini-stat-content">
            <span className="mini-stat-value">${summary.avg_revenue_per_clip.toFixed(2)}</span>
            <span className="mini-stat-label">Avg Revenue/Clip</span>
          </div>
        </div>
        <div className="mini-stat">
          <div className="mini-stat-icon"><Flame size={18} /></div>
          <div className="mini-stat-content">
            <span className="mini-stat-value">{metrics?.engagementRate}K</span>
            <span className="mini-stat-label">Engagement Rate</span>
          </div>
        </div>
        <div className="mini-stat">
          <div className="mini-stat-icon"><Calendar size={18} /></div>
          <div className="mini-stat-content">
            <span className="mini-stat-value">{recent_activity.clips_created}</span>
            <span className="mini-stat-label">Clips This Month</span>
          </div>
        </div>
      </section>

      {/* Recent Jobs Panel */}
      {recentJobs.length > 0 && (
        <section className="panel recent-jobs-panel">
          <div className="panel-header">
            <h2><Clock size={20} /> Recent Jobs</h2>
            <button className="panel-link" onClick={() => onNavigate?.('clips')}>
              View All <ChevronRight size={14} />
            </button>
          </div>
          <div className="jobs-list">
            {recentJobs.map((job) => (
              <div key={job.job_id} className="job-item">
                <div className="job-icon"><Video size={18} /></div>
                <div className="job-info">
                  <span className="job-id">Job #{job.job_id.slice(0, 8)}</span>
                  <span className="job-meta">{job.clips_count} clips generated</span>
                </div>
                <JobStatusBadge status={job.status} />
                <span className="job-date">
                  {job.created_at ? new Date(job.created_at).toLocaleDateString() : 'Recent'}
                </span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Platform Performance */}
      {Object.keys(platform_stats).length > 0 && (
        <section className="panel platform-panel">
          <div className="panel-header">
            <h2><BarChart3 size={20} /> Platform Performance</h2>
            <span className="panel-badge">{Object.keys(platform_stats).length} platforms</span>
          </div>
          <div className="platform-grid">
            {Object.entries(platform_stats).map(([platform, stats]) => {
              const platformColors = {
                youtube: { bg: 'rgba(255, 0, 0, 0.1)', color: '#ff0000', icon: 'YT' },
                tiktok: { bg: 'rgba(255, 0, 80, 0.1)', color: '#ff0050', icon: 'TT' },
                instagram: { bg: 'rgba(225, 48, 108, 0.1)', color: '#e1306c', icon: 'IG' },
                twitch: { bg: 'rgba(145, 70, 255, 0.1)', color: '#9146ff', icon: 'TW' },
                kick: { bg: 'rgba(83, 252, 24, 0.1)', color: '#53fc18', icon: 'KK' }
              };
              const platformStyle = platformColors[platform.toLowerCase()] || { bg: 'var(--bg-elevated)', color: 'var(--text-secondary)', icon: '📺' };
              const viewsPercent = summary.total_views > 0 ? ((stats.views / summary.total_views) * 100).toFixed(0) : 0;
              
              return (
                <div key={platform} className="platform-card" style={{ '--platform-color': platformStyle.color, '--platform-bg': platformStyle.bg }}>
                  <div className="platform-header">
                    <span className="platform-icon">{platformStyle.icon}</span>
                    <span className="platform-name">{platform}</span>
                    <span className="platform-percent">{viewsPercent}%</span>
                  </div>
                  <div className="platform-stats">
                    <div className="platform-stat"><Video size={14} /><span className="value">{stats.clips}</span><span className="label">clips</span></div>
                    <div className="platform-stat"><Eye size={14} /><span className="value">{stats.views >= 1000 ? `${(stats.views / 1000).toFixed(1)}K` : stats.views}</span><span className="label">views</span></div>
                    <div className="platform-stat"><DollarSign size={14} /><span className="value">${stats.revenue.toFixed(0)}</span><span className="label">earned</span></div>
                  </div>
                  <div className="platform-bar"><div className="platform-bar-fill" style={{ width: `${viewsPercent}%` }} /></div>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* Two Column Layout */}
      <div className="dashboard-columns">
        {/* Top Performing Clips */}
        {top_clips.length > 0 && (
          <section className="panel top-clips-panel">
            <div className="panel-header">
              <h2><Crown size={20} /> Top Performers</h2>
              <span className="panel-badge hot"><Flame size={12} /> Hot</span>
            </div>
            <div className="top-clips-list">
              {top_clips.map((clip, index) => (
                <div key={clip.id} className="top-clip-item">
                  <div className="clip-rank">#{index + 1}</div>
                  <div className="clip-content">
                    <div className="clip-hook">{clip.hook || 'Untitled clip'}</div>
                    <div className="clip-meta">
                      <span className={`platform-tag ${clip.platform || 'none'}`}>{clip.platform || 'Not posted'}</span>
                      {clip.virality_score && (
                        <span className="virality-tag"><Zap size={12} />{clip.virality_score}/10</span>
                      )}
                    </div>
                  </div>
                  <div className="clip-stats">
                    <div className="clip-stat views"><Eye size={14} /><span>{clip.views >= 1000 ? `${(clip.views / 1000).toFixed(1)}K` : clip.views}</span></div>
                    <div className="clip-stat revenue"><DollarSign size={14} /><span>${clip.revenue.toFixed(2)}</span></div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Category Breakdown */}
        {Object.keys(category_stats).length > 0 && (
          <section className="panel categories-panel">
            <div className="panel-header">
              <h2><PieChart size={20} /> Content Categories</h2>
            </div>
            <div className="categories-list">
              {Object.entries(category_stats).map(([category, stats]) => {
                const categoryIcons = { humor: '😂', educational: '📚', controversial: '🔥', emotional: '💔', surprising: '😱', gaming: '🎮', music: '🎵' };
                const icon = categoryIcons[category.toLowerCase()] || '📺';
                const clipsPercent = summary.total_clips > 0 ? ((stats.clips / summary.total_clips) * 100).toFixed(0) : 0;
                
                return (
                  <div key={category} className="category-item">
                    <div className="category-icon">{icon}</div>
                    <div className="category-info">
                      <div className="category-name">{category}</div>
                      <div className="category-meta">
                        <span>{stats.clips} clips</span><span>•</span>
                        <span>{stats.views >= 1000 ? `${(stats.views / 1000).toFixed(1)}K views` : `${stats.views} views`}</span>
                      </div>
                    </div>
                    <div className="category-score">
                      {stats.avg_virality > 0 && (
                        <div className="virality-score"><Star size={14} /><span>{stats.avg_virality.toFixed(1)}</span></div>
                      )}
                      <div className="category-percent">{clipsPercent}%</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        )}
      </div>

      {/* Recent Activity */}
      <section className="panel activity-panel">
        <div className="panel-header">
          <h2><Activity size={20} /> Last 30 Days Summary</h2>
        </div>
        <div className="activity-grid">
          <div className="activity-stat">
            <div className="activity-icon clips"><Video size={24} /></div>
            <div className="activity-content">
              <span className="activity-value">{recent_activity.clips_created}</span>
              <span className="activity-label">New Clips</span>
            </div>
          </div>
          <div className="activity-stat">
            <div className="activity-icon views"><Eye size={24} /></div>
            <div className="activity-content">
              <span className="activity-value">{recent_activity.views_gained >= 1000 ? `${(recent_activity.views_gained / 1000).toFixed(1)}K` : recent_activity.views_gained.toLocaleString()}</span>
              <span className="activity-label">Views Gained</span>
            </div>
          </div>
          <div className="activity-stat">
            <div className="activity-icon revenue"><DollarSign size={24} /></div>
            <div className="activity-content">
              <span className="activity-value">${recent_activity.revenue_earned}</span>
              <span className="activity-label">Revenue Earned</span>
            </div>
          </div>
          <div className="activity-stat">
            <div className="activity-icon growth"><TrendingUp size={24} /></div>
            <div className="activity-content">
              <span className="activity-value">{recent_activity.clips_created > 0 ? `${(recent_activity.views_gained / recent_activity.clips_created / 1000).toFixed(1)}K` : '0'}</span>
              <span className="activity-label">Avg Views/New Clip</span>
            </div>
          </div>
        </div>
      </section>

      {/* Empty State for new users */}
      {summary.total_clips === 0 && (
        <section className="empty-state">
          <div className="empty-icon"><Sparkles size={48} /></div>
          <h3>Ready to create your first clips?</h3>
          <p>Upload a video or paste a YouTube URL to get started with AI-powered clip generation.</p>
          <button className="empty-cta" onClick={() => onNavigate?.('generate')}>
            <Plus size={18} /> Create Your First Clip
          </button>
        </section>
      )}
    </div>
  );
}

export default Dashboard;
