import { useState, useEffect } from 'react';
import { 
  DollarSign, TrendingUp, TrendingDown, ArrowUpRight, ArrowDownRight,
  Clock, CreditCard, Wallet, PiggyBank, Download, Filter, ChevronDown,
  Check, X, AlertCircle, Loader2, Receipt, Calendar, Video, Zap
} from 'lucide-react';
import './Earnings.css';
import { API_URL } from './config';

function Earnings({ token }) {
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30d');
  const [filterType, setFilterType] = useState('all');
  const [showPayoutModal, setShowPayoutModal] = useState(false);
  const [payoutAmount, setPayoutAmount] = useState('');
  const [payoutMethod, setPayoutMethod] = useState('paypal');
  const [processingPayout, setProcessingPayout] = useState(false);
  
  const [earnings, setEarnings] = useState({
    available: 0,
    pending: 0,
    totalPaid: 0,
    lifetimeEarnings: 0,
    thisMonth: 0,
    lastMonth: 0,
    growth: 0
  });
  
  const [transactions, setTransactions] = useState([]);
  const [stats, setStats] = useState({
    avgPerClip: 0,
    topPlatform: '',
    clipsThisMonth: 0,
    viewsThisMonth: 0
  });

  useEffect(() => {
    loadEarnings();
  }, [token, timeRange]);

  const loadEarnings = async () => {
    try {
      setLoading(true);
      
      // Mock data - in real app, fetch from API
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setEarnings({
        available: 247.50,
        pending: 89.25,
        totalPaid: 1523.00,
        lifetimeEarnings: 1859.75,
        thisMonth: 336.75,
        lastMonth: 298.50,
        growth: 12.8
      });
      
      setStats({
        avgPerClip: 4.25,
        topPlatform: 'YouTube',
        clipsThisMonth: 79,
        viewsThisMonth: 245000
      });
      
      setTransactions([
        {
          id: 1,
          type: 'earning',
          description: 'Clip revenue - "Epic Gaming Fails"',
          amount: 45.00,
          platform: 'youtube',
          clips: 3,
          date: '2025-01-12',
          status: 'completed'
        },
        {
          id: 2,
          type: 'payout',
          description: 'PayPal withdrawal',
          amount: -200.00,
          method: 'PayPal',
          date: '2025-01-10',
          status: 'completed'
        },
        {
          id: 3,
          type: 'earning',
          description: 'Campaign bonus - "Tech Reviews 2025"',
          amount: 75.00,
          platform: 'tiktok',
          clips: 5,
          date: '2025-01-08',
          status: 'completed'
        },
        {
          id: 4,
          type: 'earning',
          description: 'Clip revenue - "Funny Moments Compilation"',
          amount: 32.50,
          platform: 'instagram',
          clips: 2,
          date: '2025-01-06',
          status: 'completed'
        },
        {
          id: 5,
          type: 'payout',
          description: 'Bank transfer',
          amount: -150.00,
          method: 'Bank',
          date: '2025-01-01',
          status: 'completed'
        },
        {
          id: 6,
          type: 'bonus',
          description: 'Milestone bonus - 100K views',
          amount: 50.00,
          date: '2024-12-28',
          status: 'completed'
        },
        {
          id: 7,
          type: 'earning',
          description: 'Clip revenue - "Stream Highlights"',
          amount: 89.25,
          platform: 'twitch',
          clips: 7,
          date: '2024-12-25',
          status: 'pending'
        }
      ]);
    } catch (err) {
      console.error('Failed to load earnings:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePayout = async () => {
    if (!payoutAmount || parseFloat(payoutAmount) <= 0) return;
    if (parseFloat(payoutAmount) > earnings.available) {
      alert('Amount exceeds available balance');
      return;
    }
    
    try {
      setProcessingPayout(true);
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      setEarnings({
        ...earnings,
        available: earnings.available - parseFloat(payoutAmount),
        pending: earnings.pending + parseFloat(payoutAmount)
      });
      
      setShowPayoutModal(false);
      setPayoutAmount('');
      alert('Payout request submitted successfully!');
    } catch (err) {
      alert('Failed to process payout');
    } finally {
      setProcessingPayout(false);
    }
  };

  const filteredTransactions = transactions.filter(t => {
    if (filterType === 'all') return true;
    if (filterType === 'earnings') return t.type === 'earning' || t.type === 'bonus';
    if (filterType === 'payouts') return t.type === 'payout';
    return true;
  });

  const getTransactionIcon = (type) => {
    switch (type) {
      case 'earning': return <TrendingUp size={18} />;
      case 'payout': return <CreditCard size={18} />;
      case 'bonus': return <Zap size={18} />;
      default: return <DollarSign size={18} />;
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  if (loading) {
    return (
      <div className="earnings-loading">
        <div className="loading-spinner"></div>
        <p>Loading earnings...</p>
      </div>
    );
  }

  return (
    <div className="earnings">
      {/* Header */}
      <header className="earnings-header">
        <div className="header-content">
          <div className="header-title">
            <h1>
              <DollarSign size={28} className="header-icon" />
              Earnings
            </h1>
            <p className="header-subtitle">Track your revenue and payouts</p>
          </div>
          
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
      </header>

      {/* Balance Cards */}
      <section className="balance-section">
        <div className="balance-grid">
          {/* Available Balance */}
          <div className="balance-card primary">
            <div className="balance-header">
              <div className="balance-icon">
                <Wallet size={22} />
              </div>
              <span className="balance-label">Available Balance</span>
            </div>
            <div className="balance-amount">${earnings.available.toFixed(2)}</div>
            <button 
              className="payout-btn"
              onClick={() => setShowPayoutModal(true)}
              disabled={earnings.available < 25}
            >
              <CreditCard size={16} />
              Request Payout
            </button>
            {earnings.available < 25 && (
              <span className="balance-note">Min. $25 required for payout</span>
            )}
          </div>

          {/* Pending */}
          <div className="balance-card">
            <div className="balance-header">
              <div className="balance-icon pending">
                <Clock size={22} />
              </div>
              <span className="balance-label">Pending</span>
            </div>
            <div className="balance-amount">${earnings.pending.toFixed(2)}</div>
            <span className="balance-note">Processing within 3-5 days</span>
          </div>

          {/* Total Paid */}
          <div className="balance-card">
            <div className="balance-header">
              <div className="balance-icon success">
                <Check size={22} />
              </div>
              <span className="balance-label">Total Paid Out</span>
            </div>
            <div className="balance-amount">${earnings.totalPaid.toFixed(2)}</div>
            <span className="balance-note">Lifetime payouts</span>
          </div>

          {/* This Month */}
          <div className="balance-card">
            <div className="balance-header">
              <div className="balance-icon total">
                <TrendingUp size={22} />
              </div>
              <span className="balance-label">This Month</span>
            </div>
            <div className="balance-amount">${earnings.thisMonth.toFixed(2)}</div>
            <div className={`balance-trend ${earnings.growth >= 0 ? 'positive' : 'negative'}`}>
              {earnings.growth >= 0 ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
              <span>{earnings.growth >= 0 ? '+' : ''}{earnings.growth}% vs last month</span>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Stats */}
      <section className="stats-row">
        <div className="stat-item">
          <div className="stat-icon">
            <DollarSign size={18} />
          </div>
          <div className="stat-content">
            <span className="stat-value">${stats.avgPerClip.toFixed(2)}</span>
            <span className="stat-label">Avg per Clip</span>
          </div>
        </div>
        <div className="stat-item">
          <div className="stat-icon">
            <Video size={18} />
          </div>
          <div className="stat-content">
            <span className="stat-value">{stats.clipsThisMonth}</span>
            <span className="stat-label">Clips This Month</span>
          </div>
        </div>
        <div className="stat-item">
          <div className="stat-icon">
            <TrendingUp size={18} />
          </div>
          <div className="stat-content">
            <span className="stat-value">{stats.topPlatform}</span>
            <span className="stat-label">Top Platform</span>
          </div>
        </div>
        <div className="stat-item">
          <div className="stat-icon">
            <PiggyBank size={18} />
          </div>
          <div className="stat-content">
            <span className="stat-value">${earnings.lifetimeEarnings.toFixed(2)}</span>
            <span className="stat-label">Lifetime Earnings</span>
          </div>
        </div>
      </section>

      {/* Transactions */}
      <section className="transactions-section">
        <div className="section-header">
          <h2>
            <Receipt size={20} />
            Transaction History
          </h2>
          <div className="transaction-filters">
            <div className="filter-dropdown">
              <button className="filter-btn">
                <Filter size={14} />
                {filterType === 'all' ? 'All' : filterType === 'earnings' ? 'Earnings' : 'Payouts'}
                <ChevronDown size={14} />
              </button>
              <div className="filter-menu">
                <button 
                  className={filterType === 'all' ? 'active' : ''}
                  onClick={() => setFilterType('all')}
                >
                  All
                </button>
                <button 
                  className={filterType === 'earnings' ? 'active' : ''}
                  onClick={() => setFilterType('earnings')}
                >
                  Earnings
                </button>
                <button 
                  className={filterType === 'payouts' ? 'active' : ''}
                  onClick={() => setFilterType('payouts')}
                >
                  Payouts
                </button>
              </div>
            </div>
            <button className="export-btn">
              <Download size={14} />
              Export
            </button>
          </div>
        </div>

        <div className="transactions-list">
          {filteredTransactions.length === 0 ? (
            <div className="transactions-empty">
              <Receipt size={48} />
              <h3>No transactions</h3>
              <p>Your transaction history will appear here</p>
            </div>
          ) : (
            filteredTransactions.map(transaction => (
              <div key={transaction.id} className="transaction-item">
                <div className={`transaction-icon ${transaction.type}`}>
                  {getTransactionIcon(transaction.type)}
                </div>
                
                <div className="transaction-info">
                  <div className="transaction-description">{transaction.description}</div>
                  <div className="transaction-meta">
                    <span className="transaction-date">
                      <Calendar size={12} />
                      {formatDate(transaction.date)}
                    </span>
                    {transaction.platform && (
                      <span className={`platform-badge ${transaction.platform}`}>
                        {transaction.platform}
                      </span>
                    )}
                    {transaction.clips && (
                      <span className="clips-count">{transaction.clips} clips</span>
                    )}
                    {transaction.method && (
                      <span className="method-badge">{transaction.method}</span>
                    )}
                  </div>
                </div>

                <div className="transaction-amount-section">
                  <div className={`transaction-amount ${transaction.amount >= 0 ? 'positive' : 'negative'}`}>
                    {transaction.amount >= 0 ? '+' : ''}${Math.abs(transaction.amount).toFixed(2)}
                  </div>
                  <div className={`transaction-status ${transaction.status}`}>
                    {transaction.status === 'completed' && <Check size={12} />}
                    {transaction.status === 'pending' && <Clock size={12} />}
                    {transaction.status}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </section>

      {/* Payout Modal */}
      {showPayoutModal && (
        <div className="modal-overlay" onClick={() => setShowPayoutModal(false)}>
          <div className="payout-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Request Payout</h2>
              <button className="close-btn" onClick={() => setShowPayoutModal(false)}>
                <X size={20} />
              </button>
            </div>
            
            <div className="modal-body">
              <div className="available-info">
                <span>Available Balance</span>
                <span className="available-amount">${earnings.available.toFixed(2)}</span>
              </div>
              
              <div className="form-group">
                <label>Amount</label>
                <div className="amount-input">
                  <span className="currency">$</span>
                  <input
                    type="number"
                    value={payoutAmount}
                    onChange={(e) => setPayoutAmount(e.target.value)}
                    placeholder="0.00"
                    min="25"
                    max={earnings.available}
                    step="0.01"
                  />
                </div>
                <span className="form-hint">Minimum payout: $25.00</span>
              </div>
              
              <div className="form-group">
                <label>Payout Method</label>
                <div className="method-options">
                  <button
                    className={`method-option ${payoutMethod === 'paypal' ? 'active' : ''}`}
                    onClick={() => setPayoutMethod('paypal')}
                  >
                    <span className="method-icon">💳</span>
                    PayPal
                  </button>
                  <button
                    className={`method-option ${payoutMethod === 'bank' ? 'active' : ''}`}
                    onClick={() => setPayoutMethod('bank')}
                  >
                    <span className="method-icon">🏦</span>
                    Bank
                  </button>
                  <button
                    className={`method-option ${payoutMethod === 'crypto' ? 'active' : ''}`}
                    onClick={() => setPayoutMethod('crypto')}
                  >
                    <span className="method-icon">₿</span>
                    Crypto
                  </button>
                </div>
              </div>
              
              {payoutAmount && parseFloat(payoutAmount) >= 25 && (
                <div className="payout-summary">
                  <div className="summary-row">
                    <span>Payout Amount</span>
                    <span>${parseFloat(payoutAmount).toFixed(2)}</span>
                  </div>
                  <div className="summary-row">
                    <span>Processing Fee</span>
                    <span>$0.00</span>
                  </div>
                  <div className="summary-row total">
                    <span>You'll Receive</span>
                    <span>${parseFloat(payoutAmount).toFixed(2)}</span>
                  </div>
                </div>
              )}
            </div>
            
            <div className="modal-footer">
              <button className="cancel-btn" onClick={() => setShowPayoutModal(false)}>
                Cancel
              </button>
              <button 
                className="confirm-btn"
                onClick={handlePayout}
                disabled={!payoutAmount || parseFloat(payoutAmount) < 25 || processingPayout}
              >
                {processingPayout ? (
                  <>
                    <Loader2 size={16} className="spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Check size={16} />
                    Confirm Payout
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Earnings;
