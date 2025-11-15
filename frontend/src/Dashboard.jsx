import { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, DollarSign, Video, Eye } from 'lucide-react';
import './Dashboard.css';
import { API_URL } from './config';

function Dashboard({ token }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalytics();
  }, [token]);

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

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="spinner"></div>
        <p>Loading analytics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <p>Error loading analytics: {error}</p>
        <button onClick={fetchAnalytics}>Retry</button>
      </div>
    );
  }

  if (!analytics) {
    return null;
  }

  const { summary, platform_stats, category_stats, top_clips, recent_activity } = analytics;

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p className="dashboard-subtitle">Track your clip performance and earnings</p>
      </div>

      {/* Summary Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">
            <Video size={20} />
          </div>
          <div className="stat-content">
            <div className="stat-label">Total Clips</div>
            <div className="stat-value">{summary.total_clips.toLocaleString()}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <Eye size={20} />
          </div>
          <div className="stat-content">
            <div className="stat-label">Total Views</div>
            <div className="stat-value">{summary.total_views.toLocaleString()}</div>
            <div className="stat-meta">{summary.avg_views_per_clip.toLocaleString()} avg per clip</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <DollarSign size={20} />
          </div>
          <div className="stat-content">
            <div className="stat-label">Total Revenue</div>
            <div className="stat-value">${summary.total_revenue.toLocaleString()}</div>
            <div className="stat-meta">${summary.avg_revenue_per_clip.toFixed(2)} avg per clip</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <TrendingUp size={20} />
          </div>
          <div className="stat-content">
            <div className="stat-label">Last 30 Days</div>
            <div className="stat-value">{recent_activity.clips_created} clips</div>
            <div className="stat-meta">{recent_activity.views_gained.toLocaleString()} views • ${recent_activity.revenue_earned}</div>
          </div>
        </div>
      </div>

      {/* Platform Breakdown */}
      {Object.keys(platform_stats).length > 0 && (
        <div className="analytics-section">
          <h2>
            <BarChart3 size={18} />
            Platform Performance
          </h2>
          <div className="platform-grid">
            {Object.entries(platform_stats).map(([platform, stats]) => (
              <div key={platform} className="platform-card">
                <div className="platform-name">{platform.toUpperCase()}</div>
                <div className="platform-stats">
                  <div className="platform-stat">
                    <span className="label">Clips</span>
                    <span className="value">{stats.clips}</span>
                  </div>
                  <div className="platform-stat">
                    <span className="label">Views</span>
                    <span className="value">{stats.views.toLocaleString()}</span>
                  </div>
                  <div className="platform-stat">
                    <span className="label">Revenue</span>
                    <span className="value">${stats.revenue.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Top Performing Clips */}
      {top_clips.length > 0 && (
        <div className="analytics-section">
          <h2>Top Performing Clips</h2>
          <div className="top-clips-table">
            <table>
              <thead>
                <tr>
                  <th>Hook</th>
                  <th>Platform</th>
                  <th>Views</th>
                  <th>Revenue</th>
                  <th>Virality</th>
                </tr>
              </thead>
              <tbody>
                {top_clips.map((clip) => (
                  <tr key={clip.id}>
                    <td className="clip-hook">{clip.hook || 'No hook'}</td>
                    <td>
                      <span className={`platform-badge ${clip.platform || 'none'}`}>
                        {clip.platform || 'Not posted'}
                      </span>
                    </td>
                    <td>{clip.views.toLocaleString()}</td>
                    <td>${clip.revenue.toFixed(2)}</td>
                    <td>
                      <span className="virality-score">{clip.virality_score || 'N/A'}/10</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Category Breakdown */}
      {Object.keys(category_stats).length > 0 && (
        <div className="analytics-section">
          <h2>Content Categories</h2>
          <div className="category-grid">
            {Object.entries(category_stats).map(([category, stats]) => (
              <div key={category} className="category-card">
                <div className="category-name">{category}</div>
                <div className="category-stats">
                  <div>{stats.clips} clips</div>
                  <div>{stats.views.toLocaleString()} views</div>
                  {stats.avg_virality > 0 && (
                    <div className="avg-virality">{stats.avg_virality.toFixed(1)}/10 avg</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
