import { useState } from 'react';
import { Briefcase, DollarSign, Calendar, Video } from 'lucide-react';
import { API_URL } from './config';
import './CreateCampaign.css';

function CreateCampaign({ token, onSuccess }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    video_url: '',
    num_clips_needed: 5,
    clip_duration: 30,
    resolution: 'portrait',
    style_notes: '',
    budget_per_clip: 50,
    deadline: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload = {
        ...formData,
        deadline: formData.deadline ? new Date(formData.deadline).toISOString() : null
      };

      const response = await fetch(`${API_URL}/marketplace/campaigns`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create campaign');
      }

      const data = await response.json();
      alert(`Campaign created! ID: ${data.id}`);
      
      if (onSuccess) onSuccess(data);
      
      // Reset form
      setFormData({
        title: '',
        description: '',
        video_url: '',
        num_clips_needed: 5,
        clip_duration: 30,
        resolution: 'portrait',
        style_notes: '',
        budget_per_clip: 50,
        deadline: ''
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const totalBudget = formData.num_clips_needed * formData.budget_per_clip;

  return (
    <div className="create-campaign-container">
      <div className="campaign-header">
        <h2>
          <Briefcase size={24} />
          Create Campaign
        </h2>
        <p>Post a campaign to hire clippers</p>
      </div>

      <form onSubmit={handleSubmit} className="campaign-form">
        <div className="form-section">
          <h3>Campaign Details</h3>
          
          <div className="form-group">
            <label htmlFor="title">Campaign Title *</label>
            <input
              id="title"
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              placeholder="e.g., Create viral clips from my podcast"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Description *</label>
            <textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              placeholder="Describe what you're looking for..."
              rows={4}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="video_url">
              <Video size={16} />
              Source Video URL *
            </label>
            <input
              id="video_url"
              type="url"
              value={formData.video_url}
              onChange={(e) => setFormData({...formData, video_url: e.target.value})}
              placeholder="https://youtube.com/watch?v=..."
              required
            />
            <small>YouTube, Kick, or direct video URL</small>
          </div>
        </div>

        <div className="form-section">
          <h3>Clip Requirements</h3>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="num_clips">Number of Clips</label>
              <select
                id="num_clips"
                value={formData.num_clips_needed}
                onChange={(e) => setFormData({...formData, num_clips_needed: parseInt(e.target.value)})}
              >
                <option value={3}>3 clips</option>
                <option value={5}>5 clips</option>
                <option value={8}>8 clips</option>
                <option value={10}>10 clips</option>
                <option value={15}>15 clips</option>
                <option value={20}>20 clips</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="clip_duration">Clip Duration</label>
              <select
                id="clip_duration"
                value={formData.clip_duration}
                onChange={(e) => setFormData({...formData, clip_duration: parseInt(e.target.value)})}
              >
                <option value={15}>15 seconds</option>
                <option value={30}>30 seconds</option>
                <option value={45}>45 seconds</option>
                <option value={60}>60 seconds</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="resolution">Format</label>
              <select
                id="resolution"
                value={formData.resolution}
                onChange={(e) => setFormData({...formData, resolution: e.target.value})}
              >
                <option value="portrait">Portrait (9:16)</option>
                <option value="landscape">Landscape (16:9)</option>
                <option value="square">Square (1:1)</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="style_notes">Style Notes (Optional)</label>
            <textarea
              id="style_notes"
              value={formData.style_notes}
              onChange={(e) => setFormData({...formData, style_notes: e.target.value})}
              placeholder="Any specific style preferences, branding guidelines, etc."
              rows={3}
            />
          </div>
        </div>

        <div className="form-section">
          <h3>Budget & Timeline</h3>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="budget_per_clip">
                <DollarSign size={16} />
                Budget per Clip
              </label>
              <input
                id="budget_per_clip"
                type="number"
                min="10"
                step="5"
                value={formData.budget_per_clip}
                onChange={(e) => {
                  const value = parseFloat(e.target.value);
                  if (!isNaN(value) && value >= 10) {
                    setFormData({...formData, budget_per_clip: value});
                  }
                }}
                onBlur={(e) => {
                  // Ensure minimum value on blur
                  const value = parseFloat(e.target.value);
                  if (isNaN(value) || value < 10) {
                    setFormData({...formData, budget_per_clip: 50});
                  }
                }}
                required
              />
              <small>Recommended: $50-100 per clip</small>
            </div>

            <div className="form-group">
              <label htmlFor="deadline">
                <Calendar size={16} />
                Deadline (Optional)
              </label>
              <input
                id="deadline"
                type="date"
                value={formData.deadline}
                onChange={(e) => setFormData({...formData, deadline: e.target.value})}
                min={new Date().toISOString().split('T')[0]}
              />
            </div>
          </div>

          <div className="budget-summary">
            <div className="summary-item">
              <span>Clips Needed:</span>
              <strong>{formData.num_clips_needed}</strong>
            </div>
            <div className="summary-item">
              <span>Price per Clip:</span>
              <strong>${formData.budget_per_clip}</strong>
            </div>
            <div className="summary-item total">
              <span>Total Budget:</span>
              <strong>${totalBudget}</strong>
            </div>
          </div>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <button type="submit" className="submit-btn" disabled={loading}>
          <Briefcase size={18} />
          {loading ? 'Creating Campaign...' : 'Create Campaign'}
        </button>
      </form>
    </div>
  );
}

export default CreateCampaign;
