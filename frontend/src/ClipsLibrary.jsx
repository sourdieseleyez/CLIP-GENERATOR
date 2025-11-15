import { useState, useEffect } from 'react';
import { Download, Edit2, Search, Filter, TrendingUp, Eye, DollarSign } from 'lucide-react';
import './ClipsLibrary.css';
import { API_URL } from './config';

function ClipsLibrary({ token }) {
  const [clips, setClips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterPlatform, setFilterPlatform] = useState('');
  const [filterCategory, setFilterCategory] = useState('');
  const [sortBy, setSortBy] = useState('created_at');
  const [editingClip, setEditingClip] = useState(null);
  const [analyticsForm, setAnalyticsForm] = useState({
    views: 0,
    revenue: 0,
    platform: '',
    posted_at: ''
  });

  useEffect(() => {
    fetchClips();
  }, [token, filterPlatform, filterCategory, sortBy]);

  const fetchClips = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filterPlatform) params.append('platform', filterPlatform);
      if (filterCategory) params.append('category', filterCategory);
      params.append('sort_by', sortBy);
      params.append('order', 'desc');

      const response = await fetch(`${API_URL}/clips?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch clips');
      }

      const data = await response.json();
      setClips(data.clips);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadClip = async (clipId) => {
    try {
      const response = await fetch(`${API_URL}/clips/${clipId}/download`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
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
      alert('Download failed. Please try again.');
    }
  };

  const openEditModal = (clip) => {
    setEditingClip(clip);
    setAnalyticsForm({
      views: clip.views || 0,
      revenue: clip.revenue || 0,
      platform: clip.platform || '',
      posted_at: clip.posted_at ? clip.posted_at.split('T')[0] : ''
    });
  };

  const handleUpdateAnalytics = async () => {
    try {
      const response = await fetch(`${API_URL}/clips/${editingClip.id}/analytics`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(analyticsForm)
      });

      if (!response.ok) {
        throw new Error('Update failed');
      }

      // Refresh clips
      await fetchClips();
      setEditingClip(null);
    } catch (error) {
      alert('Update failed. Please try again.');
    }
  };

  const filteredClips = clips.filter(clip => {
    const matchesSearch = !searchTerm || 
      clip.text?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      clip.hook?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  if (loading) {
    return (
      <div className="clips-loading">
        <div className="spinner"></div>
        <p>Loading clips...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="clips-error">
        <p>Error loading clips: {error}</p>
        <button onClick={fetchClips}>Retry</button>
      </div>
    );
  }

  return (
    <div className="clips-library">
      <div className="library-header">
        <div>
          <h1>Clips Library</h1>
          <p className="library-subtitle">{clips.length} total clips</p>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="library-controls">
        <div className="search-box">
          <Search size={18} />
          <input
            type="text"
            placeholder="Search clips..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filters">
          <select 
            value={filterPlatform} 
            onChange={(e) => setFilterPlatform(e.target.value)}
            className="filter-select"
          >
            <option value="">All Platforms</option>
            <option value="tiktok">TikTok</option>
            <option value="youtube">YouTube</option>
            <option value="instagram">Instagram</option>
            <option value="facebook">Facebook</option>
            <option value="twitter">Twitter</option>
          </select>

          <select 
            value={filterCategory} 
            onChange={(e) => setFilterCategory(e.target.value)}
            className="filter-select"
          >
            <option value="">All Categories</option>
            <option value="humor">Humor</option>
            <option value="educational">Educational</option>
            <option value="controversial">Controversial</option>
            <option value="emotional">Emotional</option>
            <option value="surprising">Surprising</option>
          </select>

          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value)}
            className="filter-select"
          >
            <option value="created_at">Latest</option>
            <option value="views">Most Views</option>
            <option value="revenue">Highest Revenue</option>
            <option value="virality_score">Virality Score</option>
          </select>
        </div>
      </div>

      {/* Clips Table */}
      {filteredClips.length === 0 ? (
        <div className="no-clips">
          <p>No clips found. Generate some clips to get started!</p>
        </div>
      ) : (
        <div className="clips-table-wrapper">
          <table className="clips-table">
            <thead>
              <tr>
                <th>Hook</th>
                <th>Category</th>
                <th>Platform</th>
                <th>Views</th>
                <th>Revenue</th>
                <th>Virality</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredClips.map((clip) => (
                <tr key={clip.id}>
                  <td className="clip-hook-cell">
                    <div className="clip-hook">{clip.hook || 'No hook'}</div>
                    <div className="clip-text">{clip.text?.substring(0, 60)}...</div>
                  </td>
                  <td>
                    <span className="category-badge">{clip.category || 'general'}</span>
                  </td>
                  <td>
                    <span className={`platform-badge ${clip.platform || 'none'}`}>
                      {clip.platform || 'Not posted'}
                    </span>
                  </td>
                  <td>
                    <div className="metric-cell">
                      <Eye size={14} />
                      {clip.views.toLocaleString()}
                    </div>
                  </td>
                  <td>
                    <div className="metric-cell">
                      <DollarSign size={14} />
                      {clip.revenue.toFixed(2)}
                    </div>
                  </td>
                  <td>
                    <span className="virality-badge">{clip.virality_score || 'N/A'}/10</span>
                  </td>
                  <td className="date-cell">
                    {new Date(clip.created_at).toLocaleDateString()}
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button 
                        className="action-btn edit-btn"
                        onClick={() => openEditModal(clip)}
                        title="Edit Analytics"
                      >
                        <Edit2 size={14} />
                      </button>
                      <button 
                        className="action-btn download-btn"
                        onClick={() => handleDownloadClip(clip.id)}
                        title="Download"
                      >
                        <Download size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Edit Analytics Modal */}
      {editingClip && (
        <div className="modal-overlay" onClick={() => setEditingClip(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Update Analytics</h2>
              <button className="modal-close" onClick={() => setEditingClip(null)}>×</button>
            </div>

            <div className="analytics-form">
              <div className="form-group">
                <label>Views</label>
                <input
                  type="number"
                  value={analyticsForm.views}
                  onChange={(e) => setAnalyticsForm({...analyticsForm, views: parseInt(e.target.value) || 0})}
                  min="0"
                />
              </div>

              <div className="form-group">
                <label>Revenue ($)</label>
                <input
                  type="number"
                  step="0.01"
                  value={analyticsForm.revenue}
                  onChange={(e) => setAnalyticsForm({...analyticsForm, revenue: parseFloat(e.target.value) || 0})}
                  min="0"
                />
              </div>

              <div className="form-group">
                <label>Platform</label>
                <select
                  value={analyticsForm.platform}
                  onChange={(e) => setAnalyticsForm({...analyticsForm, platform: e.target.value})}
                >
                  <option value="">Not posted</option>
                  <option value="tiktok">TikTok</option>
                  <option value="youtube">YouTube</option>
                  <option value="instagram">Instagram</option>
                  <option value="facebook">Facebook</option>
                  <option value="twitter">Twitter</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div className="form-group">
                <label>Posted Date</label>
                <input
                  type="date"
                  value={analyticsForm.posted_at}
                  onChange={(e) => setAnalyticsForm({...analyticsForm, posted_at: e.target.value})}
                />
              </div>

              <div className="form-actions">
                <button onClick={() => setEditingClip(null)} className="btn-secondary">
                  Cancel
                </button>
                <button onClick={handleUpdateAnalytics} className="btn-primary">
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ClipsLibrary;
