import DocLayout from './DocLayout';
import { Shield, Eye, Database, Lock, Globe, UserCheck, Trash2, Bell, Mail } from 'lucide-react';

const sections = [
  { id: 'overview', title: 'Overview' },
  { id: 'data-collection', title: 'Data We Collect' },
  { id: 'data-usage', title: 'How We Use Data' },
  { id: 'data-storage', title: 'Data Storage' },
  { id: 'third-parties', title: 'Third Parties' },
  { id: 'your-rights', title: 'Your Rights' },
  { id: 'cookies', title: 'Cookies' },
  { id: 'security', title: 'Security' },
  { id: 'changes', title: 'Policy Changes' },
  { id: 'contact', title: 'Contact Us' }
];

const PrivacyPolicy = ({ onBack }) => {
  return (
    <DocLayout title="Privacy Policy" sections={sections} onBack={onBack}>
      {(registerRef) => (
        <>
          <p className="doc-meta">Last updated: January 12, 2026</p>

          <section className="doc-section" id="overview" ref={registerRef('overview')}>
            <h2><Shield size={20} /> Overview</h2>
            <p>
              ClipGen Technologies ("we", "our", or "us") is committed to protecting your privacy. 
              This Privacy Policy explains how we collect, use, disclose, and safeguard your information 
              when you use our AI-powered video clipping service.
            </p>
            <div className="doc-highlight">
              <p>
                By using ClipGen, you agree to the collection and use of information in accordance 
                with this policy. We will not use or share your information with anyone except as 
                described in this Privacy Policy.
              </p>
            </div>
          </section>

          <section className="doc-section" id="data-collection" ref={registerRef('data-collection')}>
            <h2><Database size={20} /> Data We Collect</h2>
            
            <h3>Account Information</h3>
            <ul>
              <li>Email address (required for account creation)</li>
              <li>Password (stored securely using industry-standard hashing)</li>
              <li>Profile information you choose to provide</li>
              <li>Payment information (processed securely via Stripe)</li>
            </ul>

            <h3>Video Content</h3>
            <ul>
              <li>Videos you upload for processing</li>
              <li>Generated clips and captions</li>
              <li>Metadata including timestamps, duration, and format preferences</li>
            </ul>

            <h3>Usage Data</h3>
            <ul>
              <li>Processing history and job status</li>
              <li>Feature usage patterns</li>
              <li>Device information and browser type</li>
              <li>IP address and approximate location</li>
            </ul>

            <h3>Connected Services</h3>
            <p>
              If you connect third-party accounts (Twitch, YouTube, TikTok), we collect:
            </p>
            <ul>
              <li>OAuth tokens for authorized access</li>
              <li>Channel/account identifiers</li>
              <li>Public profile information</li>
            </ul>
          </section>

          <section className="doc-section" id="data-usage" ref={registerRef('data-usage')}>
            <h2><Eye size={20} /> How We Use Your Data</h2>
            <p>We use the information we collect to:</p>
            <ul>
              <li>Provide and maintain our video clipping service</li>
              <li>Process your videos using AI analysis</li>
              <li>Generate clips, captions, and recommendations</li>
              <li>Improve our AI models and service quality</li>
              <li>Send service-related notifications</li>
              <li>Process payments and manage subscriptions</li>
              <li>Respond to support requests</li>
              <li>Detect and prevent fraud or abuse</li>
            </ul>

            <div className="doc-highlight warning">
              <p>
                <strong>AI Training:</strong> We may use anonymized, aggregated data to improve our 
                AI models. Your personal videos are never shared publicly or used to train models 
                without explicit consent.
              </p>
            </div>
          </section>

          <section className="doc-section" id="data-storage" ref={registerRef('data-storage')}>
            <h2><Lock size={20} /> Data Storage & Retention</h2>
            
            <h3>Storage Location</h3>
            <p>
              Your data is stored on secure cloud infrastructure (AWS/Google Cloud) with data centers 
              located in the United States and European Union.
            </p>

            <h3>Retention Periods</h3>
            <table className="doc-table">
              <thead>
                <tr>
                  <th>Data Type</th>
                  <th>Retention Period</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Account information</td>
                  <td>Until account deletion</td>
                </tr>
                <tr>
                  <td>Uploaded videos</td>
                  <td>30 days after processing</td>
                </tr>
                <tr>
                  <td>Generated clips</td>
                  <td>90 days (Free) / 1 year (Pro)</td>
                </tr>
                <tr>
                  <td>Usage logs</td>
                  <td>12 months</td>
                </tr>
                <tr>
                  <td>Payment records</td>
                  <td>7 years (legal requirement)</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section className="doc-section" id="third-parties" ref={registerRef('third-parties')}>
            <h2><Globe size={20} /> Third-Party Services</h2>
            <p>We work with trusted third-party services to provide our platform:</p>
            
            <h3>AI Processing</h3>
            <ul>
              <li><strong>Google Gemini API</strong> - Video analysis and moment detection</li>
              <li><strong>OpenAI</strong> - Caption generation and content optimization</li>
            </ul>

            <h3>Infrastructure</h3>
            <ul>
              <li><strong>AWS/Google Cloud</strong> - Secure cloud hosting and storage</li>
              <li><strong>Cloudflare</strong> - CDN and DDoS protection</li>
            </ul>

            <h3>Payments</h3>
            <ul>
              <li><strong>Stripe</strong> - Payment processing (PCI-DSS compliant)</li>
            </ul>

            <h3>Analytics</h3>
            <ul>
              <li><strong>PostHog</strong> - Privacy-focused product analytics</li>
            </ul>

            <p>
              Each third-party service has its own privacy policy governing their use of your data. 
              We only share the minimum data necessary for each service to function.
            </p>
          </section>

          <section className="doc-section" id="your-rights" ref={registerRef('your-rights')}>
            <h2><UserCheck size={20} /> Your Rights</h2>
            <p>Depending on your location, you may have the following rights:</p>

            <h3>Access & Portability</h3>
            <p>
              Request a copy of your personal data in a machine-readable format.
            </p>

            <h3>Correction</h3>
            <p>
              Request correction of inaccurate or incomplete personal data.
            </p>

            <h3>Deletion</h3>
            <p>
              Request deletion of your personal data (subject to legal retention requirements).
            </p>

            <h3>Restriction</h3>
            <p>
              Request restriction of processing in certain circumstances.
            </p>

            <h3>Objection</h3>
            <p>
              Object to processing based on legitimate interests or for direct marketing.
            </p>

            <div className="doc-highlight success">
              <p>
                To exercise any of these rights, contact us at <a href="mailto:privacy@clipgen.io">privacy@clipgen.io</a> 
                or use the data management tools in your account settings.
              </p>
            </div>
          </section>

          <section className="doc-section" id="cookies" ref={registerRef('cookies')}>
            <h2><Shield size={20} /> Cookies & Tracking</h2>
            <p>We use cookies and similar technologies for:</p>
            <ul>
              <li><strong>Essential cookies</strong> - Required for authentication and security</li>
              <li><strong>Functional cookies</strong> - Remember your preferences</li>
              <li><strong>Analytics cookies</strong> - Understand how you use our service</li>
            </ul>
            <p>
              You can manage cookie preferences in your browser settings. Note that disabling 
              essential cookies may prevent you from using certain features.
            </p>
          </section>

          <section className="doc-section" id="security" ref={registerRef('security')}>
            <h2><Lock size={20} /> Security Measures</h2>
            <p>We implement industry-standard security measures including:</p>
            <ul>
              <li>TLS 1.3 encryption for all data in transit</li>
              <li>AES-256 encryption for data at rest</li>
              <li>Regular security audits and penetration testing</li>
              <li>Multi-factor authentication options</li>
              <li>Automated threat detection and monitoring</li>
              <li>Employee access controls and training</li>
            </ul>
            <div className="doc-highlight warning">
              <p>
                While we strive to protect your data, no method of transmission over the Internet 
                is 100% secure. Please use strong passwords and enable 2FA when available.
              </p>
            </div>
          </section>

          <section className="doc-section" id="changes" ref={registerRef('changes')}>
            <h2><Bell size={20} /> Policy Changes</h2>
            <p>
              We may update this Privacy Policy from time to time. We will notify you of any 
              material changes by:
            </p>
            <ul>
              <li>Posting the new Privacy Policy on this page</li>
              <li>Updating the "Last updated" date</li>
              <li>Sending an email notification for significant changes</li>
            </ul>
            <p>
              We encourage you to review this Privacy Policy periodically for any changes.
            </p>
          </section>

          <section className="doc-section" id="contact" ref={registerRef('contact')}>
            <h2><Mail size={20} /> Contact Us</h2>
            <p>
              If you have questions about this Privacy Policy or our data practices, please contact us:
            </p>
            <div className="contact-cards">
              <div className="contact-card">
                <h4>Email</h4>
                <p><a href="mailto:privacy@clipgen.io">privacy@clipgen.io</a></p>
              </div>
              <div className="contact-card">
                <h4>Address</h4>
                <p>ClipGen Technologies<br />Data Protection Officer<br />123 Tech Street, Suite 100<br />San Francisco, CA 94105</p>
              </div>
            </div>
          </section>
        </>
      )}
    </DocLayout>
  );
};

export default PrivacyPolicy;
