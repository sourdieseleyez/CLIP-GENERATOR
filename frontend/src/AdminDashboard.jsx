import { useState, useEffect } from 'react';
import { 
  Users, 
  CreditCard, 
  Video, 
  DollarSign, 
  Clock,
  CheckCircle,
  XCircle,
  Search,
  RefreshCw,
  Shield
} from 'lucide-react';
import { API_URL } from './config';
import './AdminDashboard.css';

function AdminDashboard({ token }) {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [payouts, setPayouts] = useState([]);
  const [recentActivity, setRecentActivity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const headers = { 'Authorization': `Bearer ${token}` };
      
      // Fetch stats
      const statsRes = await fetch(`${API_URL}/admin/stats`, { headers });
      if (statsRes.status === 403) {
        setError('Admin access required');
        setLoading(false);
        return;
      }
      if (statsRes.ok) {
        setStats(await statsRes.json());
      }
      
      // Fetch users
      const usersRes = await fetch(`${API_URL}/admin/users?limit=50`, { headers });
      if (usersRes.ok) {
        setUsers(await usersRes.json());
      }
      
      // Fetch payouts
      const payoutsRes = await fetch(`${API_URL}/admin/payouts?limit=20`, { headers });
      if (payoutsRes.ok) {
        setPayouts(await payoutsRes.json());
      }
      
      // Fetch recent activity
      const activityRes = await fetch(`${API_URL}/admin/recent-activity?days=7`, { headers });
      if (activityRes.ok) {
        setRecentActivity(await activityRes.json());
      }
    } catch (err) {
      setError('Failed to load admin data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddCredits = async (userId, amount) => {
    try {
      const response = await fetch(`${API_URL}/admin/users/${userId}/add-credits?amount=${amount}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        fetchData(); // Refresh
        alert(`Added ${amount} credits successfully`);
      }
    } catch (err) {
      alert('Failed to add credits');
    }
  };

  const handleUpdatePayout = async (payoutId, status) => {
    try {
      const response = await fetch(`${API_URL}/admin/payouts/${payoutId}?status=${status}`, {
        method: 'PATCH',
        headers: { 
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        fetchData(); // Refresh
        alert(`Payout ${status}`);
      }
    } catch (err) {
      alert('Failed to update payout');
    }
  };

  const filteredUsers = users.filter(u => 
    u.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return (
      <div className="admin-dashboard">
        <div className="admin-loading">Loading admin dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="admin-dashboard">
        <div className="admin-error">
          <Shield size={48} />
          <h2>{error}</h2>
          <p>You don't have permission to access this page.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <h1>
          <Shield size={24} />
          Admin Dashboard
        </h1>
        <button className="refresh-btn" onClick={fetchData}>
          <RefreshCw size={18} />
          Refresh
        </button>
      </div>

      {/* Stats Cards */}
      <div className="admin-stats">
        <div className="stat-card">
          <Users size={24} />
          <div className="stat-info">
            <span className="stat-value">{stats?.total_users || 0}</span>
            <span className="stat-label">Total Users</span>
          </div>
        </div>
        <div className="stat-card">
          <CheckCircle size={24} />
          <div className="stat-info">
            <span className="stat-value">{stats?.verified_users || 0}</span>
            <span className="stat-label">Verified</span>
          </div>
        </div>
        <div className="stat-card">
          <Video size={24} />
          <div className="stat-info">
            <span className="stat-value">{stats?.completed_jobs || 0}</span>
            <span className="stat-label">Jobs Done</span>
          </div>
        </div>
        <div className="stat-card">
          <CreditCard size={24} />
          <div className="stat-info">
            <span className="stat-value">{stats?.pending_payouts || 0}</span>
            <span className="stat-label">Pending Payouts</span>
          </div>
        </div>
        <div className="stat-card highlight">
          <DollarSign size={24} />
          <div className="stat-info">
            <span className="stat-value">${(stats?.pending_payout_amount || 0).toFixed(2)}</span>
            <span className="stat-label">Payout Queue</span>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      {recentActivity && (
        <div className="activity-summary">
          <h3>Last 7 Days</h3>
          <div className="activity-items">
            <span>{recentActivity.new_users} new users</span>
            <span>{recentActivity.completed_jobs} jobs completed</span>
            <span>{recentActivity.new_clips} clips generated</span>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="admin-tabs">
        <button 
          className={activeTab === 'overview' ? 'active' : ''}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={activeTab === 'users' ? 'active' : ''}
          onClick={() => setActiveTab('users')}
        >
          Users ({users.length})
        </button>
        <button 
          className={activeTab === 'payouts' ? 'active' : ''}
          onClick={() => setActiveTab('payouts')}
        >
          Payouts ({payouts.length})
        </button>
      </div>

      {/* Users Tab */}
      {activeTab === 'users' && (
        <div className="admin-section">
          <div className="section-header">
            <h2>User Management</h2>
            <div className="search-box">
              <Search size={18} />
              <input
                type="text"
                placeholder="Search by email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
          
          <div className="users-table">
            <table>
              <thead>
                <tr>
                  <th>Email</th>
                  <th>Credits</th>
                  <th>Tier</th>
                  <th>Verified</th>
                  <th>Clips</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map(user => (
                  <tr key={user.id}>
                    <td>
                      {user.email}
                      {user.is_admin && <span className="admin-badge">Admin</span>}
                    </td>
                    <td>{user.credits}</td>
                    <td><span className={`tier-badge ${user.tier}`}>{user.tier}</span></td>
                    <td>
                      {user.email_verified ? 
                        <CheckCircle size={16} className="verified" /> : 
                        <XCircle size={16} className="unverified" />
                      }
                    </td>
                    <td>{user.total_clips}</td>
                    <td>
                      <button 
                        className="action-btn"
                        onClick={() => {
                          const amount = prompt('Credits to add:');
                          if (amount && !isNaN(amount)) {
                            handleAddCredits(user.id, parseInt(amount));
                          }
                        }}
                      >
                        +Credits
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Payouts Tab */}
      {activeTab === 'payouts' && (
        <div className="admin-section">
          <h2>Payout Requests</h2>
          
          {payouts.length === 0 ? (
            <div className="empty-state">No payout requests</div>
          ) : (
            <div className="payouts-table">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>User</th>
                    <th>Amount</th>
                    <th>Status</th>
                    <th>Requested</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {payouts.map(payout => (
                    <tr key={payout.id}>
                      <td>#{payout.id}</td>
                      <td>{payout.clipper_email}</td>
                      <td>${payout.amount.toFixed(2)}</td>
                      <td>
                        <span className={`status-badge ${payout.status}`}>
                          {payout.status}
                        </span>
                      </td>
                      <td>{new Date(payout.requested_at).toLocaleDateString()}</td>
                      <td>
                        {payout.status === 'pending' && (
                          <>
                            <button 
                              className="action-btn approve"
                              onClick={() => handleUpdatePayout(payout.id, 'completed')}
                            >
                              Approve
                            </button>
                            <button 
                              className="action-btn reject"
                              onClick={() => handleUpdatePayout(payout.id, 'failed')}
                            >
                              Reject
                            </button>
                          </>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="admin-section">
          <h2>System Overview</h2>
          <div className="overview-grid">
            <div className="overview-card">
              <h3>Total Clips Generated</h3>
              <span className="big-number">{stats?.total_clips || 0}</span>
            </div>
            <div className="overview-card">
              <h3>Total Revenue Tracked</h3>
              <span className="big-number">${(stats?.total_revenue || 0).toFixed(2)}</span>
            </div>
            <div className="overview-card">
              <h3>Jobs Completed</h3>
              <span className="big-number">{stats?.completed_jobs || 0} / {stats?.total_jobs || 0}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminDashboard;
