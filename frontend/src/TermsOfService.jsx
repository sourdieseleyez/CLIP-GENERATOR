import DocLayout from './DocLayout';
import { FileText, Users, CreditCard, AlertTriangle, Scale, Ban, RefreshCw, Gavel, Video, Mail } from 'lucide-react';

const sections = [
  { id: 'acceptance', title: 'Acceptance of Terms' },
  { id: 'service-description', title: 'Service Description' },
  { id: 'accounts', title: 'User Accounts' },
  { id: 'acceptable-use', title: 'Acceptable Use' },
  { id: 'content-rights', title: 'Content & Rights' },
  { id: 'payments', title: 'Payments & Billing' },
  { id: 'termination', title: 'Termination' },
  { id: 'disclaimers', title: 'Disclaimers' },
  { id: 'liability', title: 'Limitation of Liability' },
  { id: 'disputes', title: 'Dispute Resolution' },
  { id: 'changes', title: 'Changes to Terms' },
  { id: 'contact', title: 'Contact' }
];

const TermsOfService = ({ onBack }) => {
  return (
    <DocLayout title="Terms of Service" sections={sections} onBack={onBack}>
      {(registerRef) => (
        <>
          <p className="doc-meta">Last updated: January 12, 2026</p>

          <section className="doc-section" id="acceptance" ref={registerRef('acceptance')}>
            <h2><FileText size={20} /> Acceptance of Terms</h2>
            <p>
              Welcome to ClipGen. These Terms of Service ("Terms") govern your access to and use of 
              ClipGen's website, applications, and services (collectively, the "Service"). By accessing 
              or using the Service, you agree to be bound by these Terms.
            </p>
            <div className="doc-highlight warning">
              <p>
                <strong>Important:</strong> If you do not agree to these Terms, you may not access or 
                use the Service. Please read these Terms carefully before using ClipGen.
              </p>
            </div>
            <p>
              These Terms constitute a legally binding agreement between you and ClipGen Technologies 
              ("ClipGen", "we", "us", or "our"). You must be at least 18 years old or have parental 
              consent to use this Service.
            </p>
          </section>

          <section className="doc-section" id="service-description" ref={registerRef('service-description')}>
            <h2><Video size={20} /> Service Description</h2>
            <p>ClipGen provides an AI-powered video clipping and editing platform that:</p>
            <ul>
              <li>Analyzes video content to identify engaging moments</li>
              <li>Automatically generates short-form clips from longer videos</li>
              <li>Creates captions and subtitles using speech recognition</li>
              <li>Enables direct publishing to social media platforms</li>
              <li>Provides a marketplace for content creators and editors</li>
            </ul>
            <p>
              We reserve the right to modify, suspend, or discontinue any aspect of the Service at 
              any time without prior notice.
            </p>
          </section>

          <section className="doc-section" id="accounts" ref={registerRef('accounts')}>
            <h2><Users size={20} /> User Accounts</h2>
            
            <h3>Account Creation</h3>
            <p>
              To use certain features of the Service, you must create an account. You agree to:
            </p>
            <ul>
              <li>Provide accurate and complete registration information</li>
              <li>Maintain the security of your account credentials</li>
              <li>Promptly update any changes to your information</li>
              <li>Accept responsibility for all activities under your account</li>
            </ul>

            <h3>Account Security</h3>
            <p>
              You are responsible for safeguarding your password and for any activities or actions 
              under your account. Notify us immediately of any unauthorized access or security breach.
            </p>

            <h3>Account Types</h3>
            <table className="doc-table">
              <thead>
                <tr>
                  <th>Plan</th>
                  <th>Features</th>
                  <th>Limitations</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Free (Starter)</td>
                  <td>Basic AI clipping, 720p output</td>
                  <td>3 clips/month, watermarked</td>
                </tr>
                <tr>
                  <td>Pro Streamer</td>
                  <td>Unlimited clips, 1080p, auto-posting</td>
                  <td>Single channel</td>
                </tr>
                <tr>
                  <td>Agency</td>
                  <td>Multi-channel, API access, custom branding</td>
                  <td>As per agreement</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section className="doc-section" id="acceptable-use" ref={registerRef('acceptable-use')}>
            <h2><Ban size={20} /> Acceptable Use Policy</h2>
            <p>You agree NOT to use the Service to:</p>
            <ul>
              <li>Upload content you don't have rights to use</li>
              <li>Create or distribute illegal, harmful, or offensive content</li>
              <li>Infringe on intellectual property rights of others</li>
              <li>Harass, abuse, or harm other users</li>
              <li>Attempt to gain unauthorized access to our systems</li>
              <li>Use automated tools to scrape or extract data</li>
              <li>Circumvent usage limits or security measures</li>
              <li>Resell or redistribute the Service without authorization</li>
              <li>Upload malware, viruses, or malicious code</li>
            </ul>
            <div className="doc-highlight">
              <p>
                Violation of these policies may result in immediate account suspension or termination 
                without refund.
              </p>
            </div>
          </section>

          <section className="doc-section" id="content-rights" ref={registerRef('content-rights')}>
            <h2><Scale size={20} /> Content & Intellectual Property</h2>
            
            <h3>Your Content</h3>
            <p>
              You retain ownership of all content you upload to ClipGen ("User Content"). By uploading 
              content, you grant us a limited license to:
            </p>
            <ul>
              <li>Process and analyze your videos using our AI systems</li>
              <li>Store your content on our servers</li>
              <li>Generate clips and derivatives as requested</li>
              <li>Display content within your account dashboard</li>
            </ul>

            <h3>Content Responsibility</h3>
            <p>
              You represent and warrant that you have all necessary rights to upload and process 
              your content, and that your content does not violate any third-party rights or 
              applicable laws.
            </p>

            <h3>Our Intellectual Property</h3>
            <p>
              The Service, including its design, features, and underlying technology, is owned by 
              ClipGen and protected by intellectual property laws. You may not copy, modify, or 
              reverse engineer any part of the Service.
            </p>

            <h3>DMCA Policy</h3>
            <p>
              We respect intellectual property rights and respond to valid DMCA takedown notices. 
              To report copyright infringement, contact <a href="mailto:dmca@clipgen.io">dmca@clipgen.io</a>.
            </p>
          </section>

          <section className="doc-section" id="payments" ref={registerRef('payments')}>
            <h2><CreditCard size={20} /> Payments & Billing</h2>
            
            <h3>Subscription Plans</h3>
            <p>
              Paid subscriptions are billed in advance on a monthly or annual basis. All fees are 
              non-refundable except as required by law or as explicitly stated in these Terms.
            </p>

            <h3>Price Changes</h3>
            <p>
              We may change subscription prices with 30 days' notice. Price changes will take effect 
              at the start of your next billing cycle.
            </p>

            <h3>Cancellation</h3>
            <p>
              You may cancel your subscription at any time through your account settings. Cancellation 
              takes effect at the end of your current billing period. You will retain access to paid 
              features until then.
            </p>

            <h3>Refunds</h3>
            <p>
              We offer a 7-day money-back guarantee for first-time Pro subscribers. After this period, 
              refunds are provided at our discretion for service issues.
            </p>

            <h3>Marketplace Transactions</h3>
            <p>
              For marketplace transactions between creators and editors:
            </p>
            <ul>
              <li>ClipGen charges a 15% platform fee on completed jobs</li>
              <li>Payments are held in escrow until work is approved</li>
              <li>Disputes are handled through our resolution process</li>
            </ul>
          </section>

          <section className="doc-section" id="termination" ref={registerRef('termination')}>
            <h2><RefreshCw size={20} /> Termination</h2>
            
            <h3>Termination by You</h3>
            <p>
              You may terminate your account at any time by contacting support or using the account 
              deletion feature in settings.
            </p>

            <h3>Termination by Us</h3>
            <p>
              We may suspend or terminate your account if you:
            </p>
            <ul>
              <li>Violate these Terms or our Acceptable Use Policy</li>
              <li>Engage in fraudulent or illegal activity</li>
              <li>Fail to pay applicable fees</li>
              <li>Create risk or legal exposure for ClipGen</li>
            </ul>

            <h3>Effect of Termination</h3>
            <p>
              Upon termination, your right to use the Service ceases immediately. We may delete your 
              account data after 30 days, though some information may be retained as required by law.
            </p>
          </section>

          <section className="doc-section" id="disclaimers" ref={registerRef('disclaimers')}>
            <h2><AlertTriangle size={20} /> Disclaimers</h2>
            <div className="doc-highlight warning">
              <p>
                THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, 
                EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO IMPLIED WARRANTIES OF 
                MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.
              </p>
            </div>
            <p>We do not warrant that:</p>
            <ul>
              <li>The Service will be uninterrupted or error-free</li>
              <li>AI-generated content will be accurate or suitable for your needs</li>
              <li>The Service will meet your specific requirements</li>
              <li>Any defects will be corrected</li>
            </ul>
          </section>

          <section className="doc-section" id="liability" ref={registerRef('liability')}>
            <h2><Scale size={20} /> Limitation of Liability</h2>
            <p>
              TO THE MAXIMUM EXTENT PERMITTED BY LAW, CLIPGEN SHALL NOT BE LIABLE FOR ANY INDIRECT, 
              INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING BUT NOT LIMITED TO:
            </p>
            <ul>
              <li>Loss of profits, revenue, or data</li>
              <li>Business interruption</li>
              <li>Cost of substitute services</li>
              <li>Any damages arising from your use of the Service</li>
            </ul>
            <p>
              Our total liability for any claims arising from these Terms or your use of the Service 
              shall not exceed the amount you paid us in the 12 months preceding the claim.
            </p>
          </section>

          <section className="doc-section" id="disputes" ref={registerRef('disputes')}>
            <h2><Gavel size={20} /> Dispute Resolution</h2>
            
            <h3>Informal Resolution</h3>
            <p>
              Before filing a formal dispute, you agree to contact us at <a href="mailto:legal@clipgen.io">legal@clipgen.io</a> 
              to attempt informal resolution.
            </p>

            <h3>Arbitration</h3>
            <p>
              Any disputes not resolved informally shall be resolved through binding arbitration 
              administered by JAMS under its Streamlined Arbitration Rules. The arbitration will 
              be conducted in San Francisco, California.
            </p>

            <h3>Class Action Waiver</h3>
            <p>
              You agree to resolve disputes with us on an individual basis and waive any right to 
              participate in class action lawsuits or class-wide arbitration.
            </p>

            <h3>Governing Law</h3>
            <p>
              These Terms are governed by the laws of the State of California, without regard to 
              conflict of law principles.
            </p>
          </section>

          <section className="doc-section" id="changes" ref={registerRef('changes')}>
            <h2><RefreshCw size={20} /> Changes to Terms</h2>
            <p>
              We may modify these Terms at any time. Material changes will be communicated via:
            </p>
            <ul>
              <li>Email notification to your registered address</li>
              <li>Prominent notice on our website</li>
              <li>In-app notification</li>
            </ul>
            <p>
              Continued use of the Service after changes take effect constitutes acceptance of the 
              modified Terms.
            </p>
          </section>

          <section className="doc-section" id="contact" ref={registerRef('contact')}>
            <h2><Mail size={20} /> Contact</h2>
            <p>For questions about these Terms, please contact us:</p>
            <div className="contact-cards">
              <div className="contact-card">
                <h4>Legal Inquiries</h4>
                <p><a href="mailto:legal@clipgen.io">legal@clipgen.io</a></p>
              </div>
              <div className="contact-card">
                <h4>General Support</h4>
                <p><a href="mailto:support@clipgen.io">support@clipgen.io</a></p>
              </div>
              <div className="contact-card">
                <h4>Mailing Address</h4>
                <p>ClipGen Technologies<br />123 Tech Street, Suite 100<br />San Francisco, CA 94105</p>
              </div>
            </div>
          </section>
        </>
      )}
    </DocLayout>
  );
};

export default TermsOfService;
