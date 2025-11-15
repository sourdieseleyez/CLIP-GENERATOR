import { useState, useEffect } from 'react';
import { Briefcase, DollarSign, Clock, TrendingUp, CheckCircle, XCircle } from 'lucide-react';
import { API_URL } from './config';
import './Marketplace.css';

function Marketplace({ token, userRole = 'clipper' }) {
  const [campaigns, setCampaigns] = useState([]);
  const [myJobs, setMyJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedCampaign, setSelectedCampaign] = useState(null);

  useEffect(() => {
    if (userRole === 'clipper') {
      loadCampaigns();
      loadMyJobs();
    }
  }, [userRole]);

  const loadCampaigns = async () => {
    try {
      const response = await fetch(`${API_URL}/marketplace/campaigns?status=active`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setCampaigns(data);
      }
    } catch (error) {
      console.error('Failed to load campaigns:', error);
    }
  };

  const loadMyJobs = async () => {
    try {
      const response = await fetch(`${API_URL}/marketplace/jobs/my-jobs`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setMyJobs(data);
      }
    } catch (error) {
      console.error('Failed to load jobs:', error);
    }
  };

  const claimCampaign = async (campaignId) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/marketplace/jobs/claim`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ campaign_id: campaignId })
      });

      if (response.ok) {
        alert('Campaign claimed! Start creating clips.');
        loadCampaigns();
        loadMyJobs();
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to claim campaign');
      }
    } catch (error) {
      alert('Failed to claim campaign');
    } finally {
      setLoading(false);
    }
  };

  const formatMoney = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const getStatusBadge = (status) => {
    const badges = {
      claimed: { color: 'blue', icon: <Clock size={14} /> },
      in_progress: { color: 'yellow', icon: <TrendingUp size={14} /> },
      submitted: { color: 'purple', icon: <Clock size={14} /> },
      approved: { color: 'green', icon: <CheckCircle size={14} /> },
      rejected: { color: 'red', icon: <XCircle size={14} /> },
      paid: { color: 'green', icon: <DollarSign size={14} /> }
    };

    const badge = badges[status] || badges.claimed;
    return (
      <span className={`status-badge status-${badge.color}`}>
        {badge.icon}
        {status.replace('_', ' ')}
      </span>
    );
  };

  return (
    <div className="marketplace-container">
      <div className="marketplace-header">
        <h1>
          <Briefcase size={24} />
          Marketplace
        </h1>
        <p>Find campaigns, create clips, earn money</p>
      </div>

      {/* My Active Jobs */}
      {myJobs.length > 0 && (
        <section className="my-jobs-section">
          <h2>My Active Jobs</h2>
          <div className="jobs-grid">
            {myJobs.map((job) => (
              <div key={job.job_id} className="job-card">
                <div className="job-header">
                  <span className="job-id">Job #{job.job_id}</span>
                  {getStatusBadge(job.status)}
                </div>
                <div className="job-earnings">
                  <DollarSign size={16} />
                  <span className="amount">{formatMoney(job.your_earnings)}</span>
                </div>
                <div className="job-dates">
                  <small>Claimed: {new Date(job.claimed_at).toLocaleDateString()}</small>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Available Campaigns */}
      <section className="campaigns-section">
        <h2>Available Campaigns</h2>
        {campaigns.length === 0 ? (
          <div className="empty-state">
            <Briefcase size={48} />
            <p>No campaigns available right now</p>
            <small>Check back soon for new opportunities</small>
          </div>
        ) : (
          <div className="campaigns-grid">
            {campaigns.map((campaign) => (
              <div key={campaign.id} className="campaign-card">
                <div className="campaign-header">
                  <h3>{campaign.title}</h3>
                  <div className="campaign-budget">
                    {formatMoney(campaign.budget_per_clip)}
                    <small>per clip</small>
                  </div>
                </div>

                <p className="campaign-description">{campaign.description}</p>

                <div className="campaign-details">
                  <div className="detail-item">
                    <span className="label">Clips Needed:</span>
                    <span className="value">{campaign.num_clips_needed}</span>
                  </div>
                  <div className="detail-item">
                    <span className="label">Duration:</span>
                    <span className="value">{campaign.clip_duration}s</span>
                  </div>
                  <div className="detail-item">
                    <span className="label">Format:</span>
                    <span className="value">{campaign.resolution}</span>
                  </div>
                  <div className="detail-item">
                    <span className="label">Progress:</span>
                    <span className="value">
                      {campaign.clips_submitted}/{campaign.num_clips_needed}
                    </span>
                  </div>
                </div>

                {campaign.deadline && (
                  <div className="campaign-deadline">
                    <Clock size={14} />
                    <small>Deadline: {new Date(campaign.deadline).toLocaleDateString()}</small>
                  </div>
                )}

                <button
                  className="claim-btn"
                  onClick={() => claimCampaign(campaign.id)}
                  disabled={loading}
                >
                  <Briefcase size={16} />
                  Claim This Campaign
                </button>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default Marketplace;
