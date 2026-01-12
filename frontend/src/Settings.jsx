import { useState, useEffect } from 'react';
import { Settings as SettingsIcon, User, Key, Bell, Palette, Shield, Save, Eye, EyeOff, Check, X, AlertCircle, Loader2, Link2, Trash2, Plus } from 'lucide-react';
import './Settings.css';

function Settings({ token, userEmail }) {
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null);
  const [profile, setProfile] = useState({ displayName: '', bio: '', website: '' });

  const saveSettings = () => {
    setSaveStatus({ type: 'success', message: 'Settings saved!' });
    setTimeout(() => setSaveStatus(null), 3000);
  };

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'security', label: 'Security', icon: Shield }
  ];

  return (
    <div className="settings">
      <header className="settings-header">
        <h1><SettingsIcon size={28} /> Settings</h1>
      </header>
      {saveStatus && <div className={'save-toast ' + saveStatus.type}><Check size={16} />{saveStatus.message}</div>}
      <div className="settings-layout">
        <nav className="settings-tabs">
          {tabs.map(tab => (
            <button key={tab.id} className={'tab-btn ' + (activeTab === tab.id ? 'active' : '')} onClick={() => setActiveTab(tab.id)}>
              <tab.icon size={18} /><span>{tab.label}</span>
            </button>
          ))}
        </nav>
        <div className="settings-content">
          {activeTab === 'profile' && (
            <section className="settings-section">
              <h2>Profile Settings</h2>
              <div className="form-group">
                <label>Email</label>
                <input type="email" value={userEmail || ''} disabled />
              </div>
              <div className="form-group">
                <label>Display Name</label>
                <input type="text" value={profile.displayName} onChange={(e) => setProfile({ ...profile, displayName: e.target.value })} />
              </div>
              <button className="save-btn" onClick={saveSettings}><Save size={16} /> Save</button>
            </section>
          )}
          {activeTab === 'security' && (
            <section className="settings-section">
              <h2>Security</h2>
              <button className="secondary-btn">Change Password</button>
            </section>
          )}
        </div>
      </div>
    </div>
  );
}

export default Settings;
