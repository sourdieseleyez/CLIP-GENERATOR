import { useState, useEffect } from 'react';
import { 
  Bell, Check, CheckCheck, Trash2, X, DollarSign, Video, 
  Briefcase, AlertCircle, Info, Zap, Clock, Filter
} from 'lucide-react';
import './Notifications.css';
import { API_URL } from './config';

function Notifications({ token, isOpen, onClose }) {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, unread, jobs, payouts

  useEffect(() => {
    if (isOpen) {
      loadNotifications();
    }
  }, [isOpen, token]);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      // Mock notifications - in real app, fetch from API
      const mockNotifications = [
        {
          id: 1,
          type: 'job_complete',
          title: 'Clip Generation Complete',
          message: 'Your 5 clips from "Epic Gaming Moments" are ready to download.',
          timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
          read: false,
          actionUrl: '/library'
        },
        {
          id: 2,
          type: 'payout',
          title: 'Payout Processed',
          message: 'Your payout of $127.50 has been sent to your PayPal account.',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
          read: false,
          actionUrl: '/earnings'
        },
        {
          id: 3,
          type: 'campaign',
          title: 'New Campaign Available',
          message: 'A new campaign "Summer Gaming Festival" matches your skills. $50 per clip!',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
          read: true,
          actionUrl: '/marketplace'
        },
        {
          id: 4,
          type: 'job_claimed',
          title: 'Job Claimed Successfully',
          message: 'You\'ve claimed a job from "Tech Reviews 2025" campaign. Deadline: 3 days.',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
          read: true,
          actionUrl: '/marketplace'
        },
        {
          id: 5,
          type: 'milestone',
          title: '🎉 Milestone Reached!',
          message: 'Congratulations! Your clips have reached 100,000 total views.',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
          read: true,
          actionUrl: '/dashboard'
        },
        {
          id: 6,
          type: 'warning',
          title: 'Job Deadline Approaching',
          message: 'Your job for "Gaming Highlights" campaign expires in 24 hours.',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 72).toISOString(),
          read: true,
          actionUrl: '/marketplace'
        }
      ];
      
      setNotifications(mockNotifications);
    } catch (err) {
      console.error('Failed to load notifications:', err);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = (id) => {
    setNotifications(notifications.map(n => 
      n.id === id ? { ...n, read: true } : n
    ));
  };

  const markAllAsRead = () => {
    setNotifications(notifications.map(n => ({ ...n, read: true })));
  };

  const deleteNotification = (id) => {
    setNotifications(notifications.filter(n => n.id !== id));
  };

  const clearAll = () => {
    if (confirm('Clear all notifications?')) {
      setNotifications([]);
    }
  };

  const getIcon = (type) => {
    switch (type) {
      case 'job_complete':
        return <Video size={18} />;
      case 'payout':
        return <DollarSign size={18} />;
      case 'campaign':
        return <Briefcase size={18} />;
      case 'job_claimed':
        return <Check size={18} />;
      case 'milestone':
        return <Zap size={18} />;
      case 'warning':
        return <AlertCircle size={18} />;
      default:
        return <Info size={18} />;
    }
  };

  const getIconClass = (type) => {
    switch (type) {
      case 'job_complete':
        return 'icon-success';
      case 'payout':
        return 'icon-money';
      case 'campaign':
        return 'icon-info';
      case 'job_claimed':
        return 'icon-success';
      case 'milestone':
        return 'icon-special';
      case 'warning':
        return 'icon-warning';
      default:
        return 'icon-default';
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 1000 * 60) return 'Just now';
    if (diff < 1000 * 60 * 60) return `${Math.floor(diff / (1000 * 60))}m ago`;
    if (diff < 1000 * 60 * 60 * 24) return `${Math.floor(diff / (1000 * 60 * 60))}h ago`;
    if (diff < 1000 * 60 * 60 * 24 * 7) return `${Math.floor(diff / (1000 * 60 * 60 * 24))}d ago`;
    return date.toLocaleDateString();
  };

  const filteredNotifications = notifications.filter(n => {
    if (filter === 'all') return true;
    if (filter === 'unread') return !n.read;
    if (filter === 'jobs') return ['job_complete', 'job_claimed'].includes(n.type);
    if (filter === 'payouts') return n.type === 'payout';
    return true;
  });

  const unreadCount = notifications.filter(n => !n.read).length;

  if (!isOpen) return null;

  return (
    <div className="notifications-overlay" onClick={onClose}>
      <div className="notifications-panel" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="notifications-header">
          <div className="header-title">
            <Bell size={20} />
            <h2>Notifications</h2>
            {unreadCount > 0 && (
              <span className="unread-badge">{unreadCount}</span>
            )}
          </div>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {/* Actions Bar */}
        <div className="notifications-actions">
          <div className="filter-tabs">
            {[
              { id: 'all', label: 'All' },
              { id: 'unread', label: 'Unread' },
              { id: 'jobs', label: 'Jobs' },
              { id: 'payouts', label: 'Payouts' }
            ].map(tab => (
              <button
                key={tab.id}
                className={`filter-tab ${filter === tab.id ? 'active' : ''}`}
                onClick={() => setFilter(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </div>
          
          <div className="bulk-actions">
            {unreadCount > 0 && (
              <button className="action-btn" onClick={markAllAsRead}>
                <CheckCheck size={16} />
                Mark all read
              </button>
            )}
            {notifications.length > 0 && (
              <button className="action-btn danger" onClick={clearAll}>
                <Trash2 size={16} />
                Clear all
              </button>
            )}
          </div>
        </div>

        {/* Notifications List */}
        <div className="notifications-list">
          {loading ? (
            <div className="notifications-loading">
              <div className="loading-spinner"></div>
              <p>Loading notifications...</p>
            </div>
          ) : filteredNotifications.length === 0 ? (
            <div className="notifications-empty">
              <Bell size={48} />
              <h3>No notifications</h3>
              <p>You're all caught up!</p>
            </div>
          ) : (
            filteredNotifications.map(notification => (
              <div 
                key={notification.id} 
                className={`notification-item ${!notification.read ? 'unread' : ''}`}
                onClick={() => markAsRead(notification.id)}
              >
                <div className={`notification-icon ${getIconClass(notification.type)}`}>
                  {getIcon(notification.type)}
                </div>
                
                <div className="notification-content">
                  <div className="notification-title">{notification.title}</div>
                  <div className="notification-message">{notification.message}</div>
                  <div className="notification-time">
                    <Clock size={12} />
                    {formatTime(notification.timestamp)}
                  </div>
                </div>

                <div className="notification-actions">
                  {!notification.read && (
                    <button 
                      className="mark-read-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        markAsRead(notification.id);
                      }}
                      title="Mark as read"
                    >
                      <Check size={14} />
                    </button>
                  )}
                  <button 
                    className="delete-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteNotification(notification.id);
                    }}
                    title="Delete"
                  >
                    <X size={14} />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

// Notification Bell Button Component
export function NotificationBell({ token, onClick }) {
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    // Mock unread count - in real app, fetch from API
    setUnreadCount(2);
  }, [token]);

  return (
    <button className="notification-bell" onClick={onClick}>
      <Bell size={20} />
      {unreadCount > 0 && (
        <span className="notification-badge">{unreadCount > 9 ? '9+' : unreadCount}</span>
      )}
    </button>
  );
}

export default Notifications;
