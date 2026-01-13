import { useState, useEffect } from 'react';
import { Settings as SettingsIcon, User, Key, Bell, Palette, Shield, Save, Eye, EyeOff, Check, X, AlertCircle, Loader2, Link2, Trash2, Plus } from 'lucide-react';
import './Settings.css';

function Settings({ token, userEmail }) {
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null);
  const [showApiKey, setShowApiKey] = useState({});
  const [profile, setProfile] = useState({ displayName: '', bio: '', website: '', timezone: 'UTC' });
  const [apiKeys, setApiKeys] = useState([]);
  const [showNewKeyForm, setShowNewKeyForm] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [connectedAccounts, setConnectedAccounts] = useState({ youtube: null, tiktok: null, instagram: null, twitch: null });
  const [notifications, setNotifications] = useState({ emailJobComplete: true, emailNewPayout: true, pushJobComplete: true, pushNewPayout: true });
  const [appearance, setAppearance] = useState({ theme: 'dark', accentColor: 'red' });

  useEffect(() => { loadSettings(); }, [token]);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const savedProfile = localStorage.getItem('clipgen_profile');
      if (savedProfile) setProfile(JSON.parse(savedProfile));
      setApiKeys([
        { id: 1, name: 'Production Key', key: 'sk_live_abc123def456', created: '2025-01-01', lastUsed: '2025-01-12' },
        { id: 2, name: 'Development Key', key: 'sk_test_xyz789abc123', created: '2025-01-05', lastUsed: '2025-01-10' }
      ]);
    } catch (err) { console.error('Failed to load settings:', err); }
    finally { setLoading(false); }
  };

  const saveSettings = async (section) => {
    setLoading(true);
    setSaveStatus(null);
    try {
      if (section === 'profile') localStorage.setItem('clipgen_profile', JSON.stringify(profile));
      setSaveStatus({ type: 'success', message: 'Settings saved!' });
      setTimeout(() => setSaveStatus(null), 3000);
    } catch (err) { setSaveStatus({ type: 'error', message: 'Failed to save' }); }
    finally { setLoading(false); }
  };

  const createApiKey = () => {
    if (!newKeyName.trim()) return;
    setApiKeys([...apiKeys, { id: Date.now(), name: newKeyName, key: `sk_live_${Math.random().toString(36).substring(2, 15)}`, created: new Date().toISOString().split('T')[0], lastUsed: 'Never' }]);
    setNewKeyName('');
    setShowNewKeyForm(false);
  };

  const deleteApiKey = (keyId) => { if (window.confirm('Delete this API key?')) setApiKeys(apiKeys.filter(k => k.id !== keyId)); };
  const toggleKeyVisibility = (keyId) => { setShowApiKey({ ...showApiKey, [keyId]: !showApiKey[keyId] }); };
  const maskKey = (key) => key.substring(0, 8) + '...' + key.substring(key.length - 4);

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'api-keys', label: 'API Keys', icon: Key },
    { id: 'connections', label: 'Connections', icon: Link2 },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'appearance', label: 'Appearance', icon: Palette },
    { id: 'security', label: 'Security', icon: Shield }
  ];

  const platforms = [
    { id: 'youtube', name: 'YouTube', icon: 'YT', color: '#ff0000' },
    { id: 'tiktok', name: 'TikTok', icon: 'TT', color: '#ff0050' },
    { id: 'instagram', name: 'Instagram', icon: 'IG', color: '#e1306c' },
    { id: 'twitch', name: 'Twitch', icon: 'TW', color: '#9146ff' }
  ];

  const accentColors = [
    { id: 'red', color: '#ef4444' }, { id: 'purple', color: '#8b5cf6' },
    { id: 'cyan', color: '#06b6d4' }, { id: 'green', color: '#22c55e' }
  ];

  return (
    <div className="settings">
      <header className="settings-header">
        <div className="header-title">
          <h1><SettingsIcon size={28} className="header-icon" /> Settings</h1>
          <p className="header-subtitle">Manage your account and preferences</p>
        </div>
      </header>
      {saveStatus && <div className={`save-toast ${saveStatus.type}`}>{saveStatus.type === 'success' ? <Check size={16} /> : <AlertCircle size={16} />}{saveStatus.message}</div>}
      <div className="settings-layout">
        <nav className="settings-tabs">
          {tabs.map(tab => (<button key={tab.id} className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`} onClick={() => setActiveTab(tab.id)}><tab.icon size={18} /><span>{tab.label}</span></button>))}
        </nav>
        <div className="settings-content">
          {activeTab === 'profile' && (
            <section className="settings-section">
              <div className="section-header"><h2>Profile Settings</h2><p>Manage your public profile</p></div>
              <div className="form-grid">
                <div className="form-group"><label>Email</label><input type="email" value={userEmail || ''} disabled className="disabled" /><span className="form-hint">Email cannot be changed</span></div>
                <div className="form-group"><label>Display Name</label><input type="text" value={profile.displayName} onChange={(e) => setProfile({ ...profile, displayName: e.target.value })} placeholder="Your display name" /></div>
                <div className="form-group full-width"><label>Bio</label><textarea value={profile.bio} onChange={(e) => setProfile({ ...profile, bio: e.target.value })} placeholder="Tell us about yourself..." rows={3} /></div>
                <div className="form-group"><label>Website</label><input type="url" value={profile.website} onChange={(e) => setProfile({ ...profile, website: e.target.value })} placeholder="https://yourwebsite.com" /></div>
              </div>
              <div className="section-actions"><button className="save-btn" onClick={() => saveSettings('profile')} disabled={loading}>{loading ? <Loader2 size={16} className="spin" /> : <Save size={16} />} Save Changes</button></div>
            </section>
          )}
          {activeTab === 'api-keys' && (
            <section className="settings-section">
              <div className="section-header"><h2>API Keys</h2><p>Manage your API keys</p></div>
              <div className="api-keys-list">
                {apiKeys.map(key => (<div key={key.id} className="api-key-item"><div className="key-info"><div className="key-name">{key.name}</div><div className="key-value"><code>{showApiKey[key.id] ? key.key : maskKey(key.key)}</code><button className="toggle-visibility" onClick={() => toggleKeyVisibility(key.id)}>{showApiKey[key.id] ? <EyeOff size={14} /> : <Eye size={14} />}</button></div><div className="key-meta">Created: {key.created}</div></div><button className="delete-key-btn" onClick={() => deleteApiKey(key.id)}><Trash2 size={16} /></button></div>))}
                {showNewKeyForm ? (<div className="new-key-form"><input type="text" value={newKeyName} onChange={(e) => setNewKeyName(e.target.value)} placeholder="Key name" autoFocus /><div className="form-actions"><button className="save-btn" onClick={createApiKey}><Plus size={16} /> Create</button><button className="cancel-btn" onClick={() => setShowNewKeyForm(false)}><X size={16} /> Cancel</button></div></div>) : (<button className="add-key-btn" onClick={() => setShowNewKeyForm(true)}><Plus size={18} /> Create New API Key</button>)}
              </div>
            </section>
          )}
          {activeTab === 'connections' && (
            <section className="settings-section">
              <div className="section-header"><h2>Connected Accounts</h2><p>Link your social media accounts</p></div>
              <div className="connections-grid">
                {platforms.map(platform => (<div key={platform.id} className="connection-card" style={{ '--platform-color': platform.color }}><div className="platform-icon">{platform.icon}</div><div className="platform-info"><div className="platform-name">{platform.name}</div>{connectedAccounts[platform.id] ? <div className="connected-status"><Check size={14} /> Connected</div> : <div className="disconnected-status">Not connected</div>}</div><button className={connectedAccounts[platform.id] ? 'disconnect-btn' : 'connect-btn'}>{connectedAccounts[platform.id] ? 'Disconnect' : 'Connect'}</button></div>))}
              </div>
            </section>
          )}
          {activeTab === 'notifications' && (
            <section className="settings-section">
              <div className="section-header"><h2>Notification Preferences</h2><p>Choose how you want to be notified</p></div>
              <div className="notifications-grid">
                <div className="notification-group"><h3>Email Notifications</h3><label className="toggle-item"><span>Job completion alerts</span><input type="checkbox" checked={notifications.emailJobComplete} onChange={(e) => setNotifications({ ...notifications, emailJobComplete: e.target.checked })} /><span className="toggle-switch"></span></label><label className="toggle-item"><span>Payout notifications</span><input type="checkbox" checked={notifications.emailNewPayout} onChange={(e) => setNotifications({ ...notifications, emailNewPayout: e.target.checked })} /><span className="toggle-switch"></span></label></div>
                <div className="notification-group"><h3>Push Notifications</h3><label className="toggle-item"><span>Job completion alerts</span><input type="checkbox" checked={notifications.pushJobComplete} onChange={(e) => setNotifications({ ...notifications, pushJobComplete: e.target.checked })} /><span className="toggle-switch"></span></label><label className="toggle-item"><span>Payout notifications</span><input type="checkbox" checked={notifications.pushNewPayout} onChange={(e) => setNotifications({ ...notifications, pushNewPayout: e.target.checked })} /><span className="toggle-switch"></span></label></div>
              </div>
              <div className="section-actions"><button className="save-btn" onClick={() => saveSettings('notifications')} disabled={loading}>{loading ? <Loader2 size={16} className="spin" /> : <Save size={16} />} Save Preferences</button></div>
            </section>
          )}
          {activeTab === 'appearance' && (
            <section className="settings-section">
              <div className="section-header"><h2>Appearance</h2><p>Customize how ClipGen looks</p></div>
              <div className="appearance-options">
                <div className="option-group"><label>Theme</label><div className="theme-selector"><button className={`theme-btn ${appearance.theme === 'dark' ? 'active' : ''}`} onClick={() => setAppearance({ ...appearance, theme: 'dark' })}>Dark</button><button className={`theme-btn ${appearance.theme === 'light' ? 'active' : ''}`} onClick={() => setAppearance({ ...appearance, theme: 'light' })}>Light</button></div></div>
                <div className="option-group"><label>Accent Color</label><div className="color-selector">{accentColors.map(c => (<button key={c.id} className={`color-btn ${appearance.accentColor === c.id ? 'active' : ''}`} style={{ '--color': c.color }} onClick={() => setAppearance({ ...appearance, accentColor: c.id })} />))}</div></div>
              </div>
              <div className="section-actions"><button className="save-btn" onClick={() => saveSettings('appearance')} disabled={loading}>{loading ? <Loader2 size={16} className="spin" /> : <Save size={16} />} Save Appearance</button></div>
            </section>
          )}
          {activeTab === 'security' && (
            <section className="settings-section">
              <div className="section-header"><h2>Security</h2><p>Manage your account security</p></div>
              <div className="security-options">
                <div className="security-item"><div className="security-info"><h3>Change Password</h3><p>Update your password regularly</p></div><button className="secondary-btn">Change Password</button></div>
                <div className="security-item"><div className="security-info"><h3>Two-Factor Authentication</h3><p>Add extra security</p></div><button className="secondary-btn">Enable 2FA</button></div>
                <div className="security-item danger"><div className="security-info"><h3>Delete Account</h3><p>Permanently delete your account</p></div><button className="danger-btn">Delete Account</button></div>
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  );
}

export default Settings;
