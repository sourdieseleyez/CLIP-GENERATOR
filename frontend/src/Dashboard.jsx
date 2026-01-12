import { useState, useEffect, useMemo } from 'react';
import { 
  BarChart3, TrendingUp, TrendingDown, DollarSign, Video, Eye, 
  Zap, Target, Award, Clock, ArrowUpRight, ArrowDownRight,
  Play, Flame, Crown, Star, Activity, PieChart, Calendar, AlertCircle
} from 'lucide-react';
import './Dashboard.css';
import { API_URL } from './config';

// Mini sparkline component for trends
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
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
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
      <circle
        stroke="var(--border-primary)"
        fill="transparent"
        strokeWidth={strokeWidth}
        r={radius}
        cx={size / 2}
        cy={size / 2}
      />
      <circle
        stroke={color}
        fill="transparent"
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        r={radius}
        cx={size / 2}
        cy={size / 2}
        style={{ 
          transform: 'rotate(-90deg)', 
          transformOrigin: '50% 50%',
          transition: 'stroke-dashoffset 0.5s ease'
        }}
      />
    </svg>
  );
}

function Dashboard({ token }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('30d');

  useEffect(() => {
    fetchAnalytics();
  }, [token, timeRange]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/analytics/dashboard`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch analytics');
      }

      const data = await response.json();
      setAnalytics(data);
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
    
    const { summary, platform_stats, recent_activity } = analytics;
    
    // Calculate engagement rate (views per clip)
    const engagementRate = summary.total_clips > 0 
      ? (summary.total_views / summary.total_clips / 1000).toFixed(1) 
      : 0;
    
    // Calculate revenue per 1000 views (RPM)
    const rpm = summary.total_views > 0 
      ? ((summary.total_revenue / summary.total_views) * 1000).toFixed(2)
      : 0;
    
    // Growth calculation (mock - would need historical data)
    const viewsGrowth = recent_activity.views_gained > 0 ? 12.5 : 0;
    const revenueGrowth = recent_activity.revenue_earned > 0 ? 8.3 : 0;
    
    return {
      engagementRate,
      rpm,
      viewsGrowth,
      revenueGrowth
    };
  }, [analytics]);

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner">
          <Activity size={32} className="spin" />
        </div>
        <p className="loading-text">Loading your stats...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <div className="error-icon"><AlertCircle size={32} /></div>
        <h3>Failed to load analytics</h3>
        <p>{error}</p>
        <button onClick={fetchAnalytics} className="retry-btn">
          <Activity size={16} />
          Retry
        </button>
      </div>
    );
  }

  if (!analytics) {
    return null;
  }

  const { summary, platform_stats, category_stats, top_clips, recent_activity } = analytics;

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <div className="header-title">
            <h1>
              <Zap size={28} className="header-icon" />
              Dashboard
            </h1>
            <p className="header-subtitle">Track your clip empire</p>
          </div>
          
          <div className="header-actions">
            <div className="time-selector">
              {['7d', '30d', '90d', 'all'].map((range) => (
                <button
                  key={range}
                  className={`time-btn ${timeRange === range ? 'active' : ''}`}
                  onClick={() => setTimeRange(range)}
                >
                  {range === 'all' ? 'All Time' : range}
                </button>
              ))}
            </div>
          </div>
        </div>
      </header>

      {/* Main Stats Grid */}
      <section className="stats-section">
        <div className="stats-grid">
          {/* Total Clips */}
          <div className="stat-card stat-clips">
            <div className="stat-header">
              <div className="stat-icon-wrapper clips">
                <Video size={20} />
              </div>
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
              <div className="stat-icon-wrapper views">
                <Eye size={20} />
              </div>
              <span className="stat-label">Total Views</span>
            </div>
            <div className="stat-body">
              <div className="stat-value">
                {summary.total_views >= 1000000 
                  ? `${(summary.total_views / 1000000).toFixed(1)}M`
                  : summary.total_views >= 1000
                    ? `${(summary.total_views / 1000).toFixed(1)}K`
                    : summary.total_views.toLocaleString()
                }
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
              <div className="stat-icon-wrapper revenue">
                <DollarSign size={20} />
              </div>
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
              <div className="stat-icon-wrapper rpm">
                <Target size={20} />
              </div>
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
          <div className="mini-stat-icon">
            <TrendingUp size={18} />
          </div>
          <div className="mini-stat-content">
            <span className="mini-stat-value">{summary.avg_views_per_clip.toLocaleString()}</span>
            <span className="mini-stat-label">Avg Views/Clip</span>
          </div>
        </div>
        
        <div className="mini-stat">
          <div className="mini-stat-icon">
            <DollarSign size={18} />
          </div>
          <div className="mini-stat-content">
            <span className="mini-stat-value">${summary.avg_revenue_per_clip.toFixed(2)}</span>
            <span className="mini-stat-label">Avg Revenue/Clip</span>
          </div>
        </div>
        
        <div className="mini-stat">
          <div className="mini-stat-icon">
            <Flame size={18} />
          </div>
          <div className="mini-stat-content">
            <span className="mini-stat-value">{metrics?.engagementRate}K</span>
            <span className="mini-stat-label">Engagement Rate</span>
          </div>
        </div>
        
        <div className="mini-stat">
          <div className="mini-stat-icon">
            <Calendar size={18} />
          </div>
          <div className="mini-stat-content">
            <span className="mini-stat-value">{recent_activity.clips_created}</span>
            <span className="mini-stat-label">Clips This Month</span>
          </div>
        </div>
      </section>


      {/* Platform Performance */}
      {Object.keys(platform_stats).length > 0 && (
        <section className="panel platform-panel">
          <div className="panel-header">
            <h2>
              <BarChart3 size={20} />
              Platform Performance
            </h2>
            <span className="panel-badge">{Object.keys(platform_stats).length} platforms</span>
          </div>
          
          <div className="platform-grid">
            {Object.entries(platform_stats).map(([platform, stats]) => {
              const platformColors = {
                youtube: { bg: 'rgba(255, 0, 0, 0.1)', color: '#ff0000', icon: 'YT' },
                tiktok: { bg: 'rgba(255, 0, 80, 0.1)', color: '#ff0050', icon: 'TT' },
                instagram: { bg: 'rgba(225, 48, 108, 0.1)', color: '#e1306c', icon: 'IG' },
                twitch: { bg: 'rgba(145, 70, 255, 0.1)', color: '#9146ff', icon: 'TW' },
                kick: { bg: 'rgba(83, 252, 24, 0.1)', color: '#53fc18', icon: 'KK' },
                facebook: { bg: 'rgba(24, 119, 242, 0.1)', color: '#1877f2', icon: 'FB' },
                twitter: { bg: 'rgba(29, 161, 242, 0.1)', color: '#1da1f2', icon: 'X' }
              };
              
              const platformStyle = platformColors[platform.toLowerCase()] || 
                { bg: 'var(--bg-elevated)', color: 'var(--text-secondary)', icon: '📺' };
              
              const viewsPercent = summary.total_views > 0 
                ? ((stats.views / summary.total_views) * 100).toFixed(0) 
                : 0;
              
              return (
                <div 
                  key={platform} 
                  className="platform-card"
                  style={{ '--platform-color': platformStyle.color, '--platform-bg': platformStyle.bg }}
                >
                  <div className="platform-header">
                    <span className="platform-icon">{platformStyle.icon}</span>
                    <span className="platform-name">{platform}</span>
                    <span className="platform-percent">{viewsPercent}%</span>
                  </div>
                  
                  <div className="platform-stats">
                    <div className="platform-stat">
                      <Video size={14} />
                      <span className="value">{stats.clips}</span>
                      <span className="label">clips</span>
                    </div>
                    <div className="platform-stat">
                      <Eye size={14} />
                      <span className="value">
                        {stats.views >= 1000 
                          ? `${(stats.views / 1000).toFixed(1)}K` 
                          : stats.views}
                      </span>
                      <span className="label">views</span>
                    </div>
                    <div className="platform-stat">
                      <DollarSign size={14} />
                      <span className="value">${stats.revenue.toFixed(0)}</span>
                      <span className="label">earned</span>
                    </div>
                  </div>
                  
                  <div className="platform-bar">
                    <div 
                      className="platform-bar-fill" 
                      style={{ width: `${viewsPercent}%` }}
                    />
                  </div>
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
              <h2>
                <Crown size={20} />
                Top Performers
              </h2>
              <span className="panel-badge hot">
                <Flame size={12} />
                Hot
              </span>
            </div>
            
            <div className="top-clips-list">
              {top_clips.map((clip, index) => (
                <div key={clip.id} className="top-clip-item">
                  <div className="clip-rank">
                    #{index + 1}
                  </div>
                  
                  <div className="clip-content">
                    <div className="clip-hook">{clip.hook || 'Untitled clip'}</div>
                    <div className="clip-meta">
                      <span className={`platform-tag ${clip.platform || 'none'}`}>
                        {clip.platform || 'Not posted'}
                      </span>
                      {clip.virality_score && (
                        <span className="virality-tag">
                          <Zap size={12} />
                          {clip.virality_score}/10
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="clip-stats">
                    <div className="clip-stat views">
                      <Eye size={14} />
                      <span>
                        {clip.views >= 1000 
                          ? `${(clip.views / 1000).toFixed(1)}K` 
                          : clip.views}
                      </span>
                    </div>
                    <div className="clip-stat revenue">
                      <DollarSign size={14} />
                      <span>${clip.revenue.toFixed(2)}</span>
                    </div>
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
              <h2>
                <PieChart size={20} />
                Content Categories
              </h2>
            </div>
            
            <div className="categories-list">
              {Object.entries(category_stats).map(([category, stats]) => {
                const categoryIcons = {
                  humor: 'HU',
                  educational: 'ED',
                  controversial: 'CT',
                  emotional: 'EM',
                  surprising: 'SP',
                  gaming: 'GM',
                  music: 'MU',
                  sports: 'SR',
                  news: 'NW',
                  lifestyle: 'LF'
                };
                
                const icon = categoryIcons[category.toLowerCase()] || '📺';
                const clipsPercent = summary.total_clips > 0 
                  ? ((stats.clips / summary.total_clips) * 100).toFixed(0) 
                  : 0;
                
                return (
                  <div key={category} className="category-item">
                    <div className="category-icon">{icon}</div>
                    <div className="category-info">
                      <div className="category-name">{category}</div>
                      <div className="category-meta">
                        <span>{stats.clips} clips</span>
                        <span>•</span>
                        <span>
                          {stats.views >= 1000 
                            ? `${(stats.views / 1000).toFixed(1)}K views` 
                            : `${stats.views} views`}
                        </span>
                      </div>
                    </div>
                    <div className="category-score">
                      {stats.avg_virality > 0 && (
                        <div className="virality-score">
                          <Star size={14} />
                          <span>{stats.avg_virality.toFixed(1)}</span>
                        </div>
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
          <h2>
            <Activity size={20} />
            Last 30 Days Summary
          </h2>
        </div>
        
        <div className="activity-grid">
          <div className="activity-stat">
            <div className="activity-icon clips">
              <Video size={24} />
            </div>
            <div className="activity-content">
              <span className="activity-value">{recent_activity.clips_created}</span>
              <span className="activity-label">New Clips</span>
            </div>
          </div>
          
          <div className="activity-stat">
            <div className="activity-icon views">
              <Eye size={24} />
            </div>
            <div className="activity-content">
              <span className="activity-value">
                {recent_activity.views_gained >= 1000 
                  ? `${(recent_activity.views_gained / 1000).toFixed(1)}K` 
                  : recent_activity.views_gained.toLocaleString()}
              </span>
              <span className="activity-label">Views Gained</span>
            </div>
          </div>
          
          <div className="activity-stat">
            <div className="activity-icon revenue">
              <DollarSign size={24} />
            </div>
            <div className="activity-content">
              <span className="activity-value">${recent_activity.revenue_earned}</span>
              <span className="activity-label">Revenue Earned</span>
            </div>
          </div>
          
          <div className="activity-stat">
            <div className="activity-icon growth">
              <TrendingUp size={24} />
            </div>
            <div className="activity-content">
              <span className="activity-value">
                {recent_activity.clips_created > 0 
                  ? `${(recent_activity.views_gained / recent_activity.clips_created / 1000).toFixed(1)}K`
                  : '0'}
              </span>
              <span className="activity-label">Avg Views/New Clip</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Dashboard;
