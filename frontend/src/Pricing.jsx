import { useState, useEffect } from 'react';
import { Check, Sparkles, Zap, Crown, Star } from 'lucide-react';
import { API_URL } from './config';
import './Pricing.css';

function Pricing({ token, onClose }) {
  const [pricing, setPricing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedPackage, setSelectedPackage] = useState(null);

  useEffect(() => {
    fetchPricing();
  }, []);

  const fetchPricing = async () => {
    try {
      const response = await fetch(`${API_URL}/pricing`);
      if (response.ok) {
        const data = await response.json();
        setPricing(data);
      }
    } catch (error) {
      console.error('Failed to fetch pricing:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = (pkg) => {
    setSelectedPackage(pkg);
    // TODO: Integrate with Stripe when ready
    alert(`Stripe integration coming soon!\n\nPackage: ${pkg.credits} credits for $${pkg.price}`);
  };

  if (loading) {
    return (
      <div className="pricing-page">
        <div className="pricing-loading">Loading pricing...</div>
      </div>
    );
  }

  return (
    <div className="pricing-page">
      <div className="pricing-header">
        <h1>
          <Sparkles size={28} />
          Get More Credits
        </h1>
        <p>Each credit = 1 video processed (up to 10 viral clips)</p>
      </div>

      <div className="pricing-grid">
        {pricing?.packages?.map((pkg, index) => (
          <div 
            key={index} 
            className={`pricing-card ${pkg.popular ? 'popular' : ''}`}
          >
            {pkg.popular && (
              <div className="popular-badge">
                <Star size={14} />
                Most Popular
              </div>
            )}
            
            <div className="pricing-credits">
              <span className="credits-number">{pkg.credits}</span>
              <span className="credits-label">credits</span>
            </div>
            
            <div className="pricing-price">
              <span className="price-currency">$</span>
              <span className="price-amount">{pkg.price}</span>
            </div>
            
            <div className="pricing-per-credit">
              ${pkg.per_credit.toFixed(2)} per credit
            </div>
            
            <ul className="pricing-features">
              <li><Check size={16} /> {pkg.credits} video processes</li>
              <li><Check size={16} /> Up to {pkg.credits * 10} clips</li>
              <li><Check size={16} /> AI viral detection</li>
              <li><Check size={16} /> Auto subtitles</li>
              <li><Check size={16} /> All formats (9:16, 16:9, 1:1)</li>
            </ul>
            
            <button 
              className={`pricing-btn ${pkg.popular ? 'primary' : ''}`}
              onClick={() => handlePurchase(pkg)}
            >
              {pkg.popular ? <Zap size={16} /> : null}
              Buy {pkg.credits} Credits
            </button>
          </div>
        ))}
      </div>

      <div className="pricing-footer">
        <div className="pricing-note">
          <Crown size={18} />
          <span>New users get <strong>3 free credits</strong> to try ClipGen!</span>
        </div>
        
        <div className="pricing-faq">
          <h3>FAQ</h3>
          <div className="faq-item">
            <strong>What counts as 1 credit?</strong>
            <p>Processing one video uses 1 credit, regardless of length. You get up to 10 clips per video.</p>
          </div>
          <div className="faq-item">
            <strong>Do credits expire?</strong>
            <p>No! Your credits never expire. Use them whenever you want.</p>
          </div>
          <div className="faq-item">
            <strong>Can I get a refund?</strong>
            <p>Yes, unused credits can be refunded within 30 days of purchase.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Pricing;
