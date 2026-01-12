import { useState } from 'react';
import DocLayout from './DocLayout';
import { Mail, MessageSquare, Clock, MapPin, Send, CheckCircle, Briefcase } from 'lucide-react';

const sections = [
  { id: 'get-in-touch', title: 'Get in Touch' },
  { id: 'contact-form', title: 'Contact Form' },
  { id: 'support', title: 'Support' },
  { id: 'business', title: 'Business Inquiries' },
  { id: 'office', title: 'Office Location' }
];

const Contact = ({ onBack }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [submitted, setSubmitted] = useState(false);
  const [sending, setSending] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setSending(true);
    // Simulate form submission
    setTimeout(() => {
      setSending(false);
      setSubmitted(true);
      setFormData({ name: '', email: '', subject: '', message: '' });
    }, 1500);
  };

  return (
    <DocLayout title="Contact Us" sections={sections} onBack={onBack}>
      {(registerRef) => (
        <>
          <section className="doc-section" id="get-in-touch" ref={registerRef('get-in-touch')}>
            <h2><Mail size={20} /> Get in Touch</h2>
            <p>
              We'd love to hear from you. Whether you have a question about features, pricing, 
              need a demo, or anything else, our team is ready to answer all your questions.
            </p>
            <div className="doc-highlight">
              <p>
                Our support team typically responds within 24 hours during business days. 
                For urgent matters, please indicate "URGENT" in your subject line.
              </p>
            </div>
          </section>

          <section className="doc-section" id="contact-form" ref={registerRef('contact-form')}>
            <h2><MessageSquare size={20} /> Contact Form</h2>
            
            {submitted ? (
              <div className="doc-highlight success">
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <CheckCircle size={24} />
                  <div>
                    <strong>Message Sent!</strong>
                    <p style={{ margin: '4px 0 0 0' }}>
                      Thank you for reaching out. We'll get back to you within 24 hours.
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <form className="contact-form" onSubmit={handleSubmit}>
                <div className="form-row">
                  <div className="form-field">
                    <label htmlFor="name">Your Name</label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      placeholder="John Doe"
                      required
                    />
                  </div>
                  <div className="form-field">
                    <label htmlFor="email">Email Address</label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      placeholder="john@example.com"
                      required
                    />
                  </div>
                </div>
                <div className="form-field">
                  <label htmlFor="subject">Subject</label>
                  <select
                    id="subject"
                    name="subject"
                    value={formData.subject}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select a topic...</option>
                    <option value="general">General Inquiry</option>
                    <option value="support">Technical Support</option>
                    <option value="billing">Billing Question</option>
                    <option value="partnership">Partnership Opportunity</option>
                    <option value="feedback">Feedback</option>
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="message">Message</label>
                  <textarea
                    id="message"
                    name="message"
                    value={formData.message}
                    onChange={handleChange}
                    placeholder="How can we help you?"
                    rows={5}
                    required
                  />
                </div>
                <button type="submit" className="submit-btn" disabled={sending}>
                  {sending ? (
                    'Sending...'
                  ) : (
                    <>
                      <Send size={16} />
                      Send Message
                    </>
                  )}
                </button>
              </form>
            )}
          </section>

          <section className="doc-section" id="support" ref={registerRef('support')}>
            <h2><Clock size={20} /> Support</h2>
            <p>Need help with your account or have technical questions?</p>
            
            <div className="contact-cards">
              <div className="contact-card">
                <h4>General Support</h4>
                <p><a href="mailto:support@clipgen.io">support@clipgen.io</a></p>
                <p className="card-note">Response within 24 hours</p>
              </div>
              <div className="contact-card">
                <h4>Technical Issues</h4>
                <p><a href="mailto:tech@clipgen.io">tech@clipgen.io</a></p>
                <p className="card-note">For bugs and technical problems</p>
              </div>
            </div>
          </section>

          <section className="doc-section" id="business" ref={registerRef('business')}>
            <h2><Briefcase size={20} /> Business Inquiries</h2>
            <p>Interested in partnerships, enterprise solutions, or press inquiries?</p>
            
            <div className="contact-cards">
              <div className="contact-card">
                <h4>Partnerships</h4>
                <p><a href="mailto:partners@clipgen.io">partners@clipgen.io</a></p>
                <p className="card-note">Collaboration opportunities</p>
              </div>
              <div className="contact-card">
                <h4>Enterprise Sales</h4>
                <p><a href="mailto:sales@clipgen.io">sales@clipgen.io</a></p>
                <p className="card-note">Custom plans for agencies</p>
              </div>
              <div className="contact-card">
                <h4>Press & Media</h4>
                <p><a href="mailto:press@clipgen.io">press@clipgen.io</a></p>
                <p className="card-note">Media inquiries only</p>
              </div>
            </div>
          </section>

          <section className="doc-section" id="office" ref={registerRef('office')}>
            <h2><MapPin size={20} /> Office Location</h2>
            <div className="contact-cards">
              <div className="contact-card">
                <h4>Headquarters</h4>
                <p>
                  ClipGen Technologies<br />
                  123 Tech Street, Suite 100<br />
                  San Francisco, CA 94105<br />
                  United States
                </p>
              </div>
              <div className="contact-card">
                <h4>Business Hours</h4>
                <p>
                  Monday - Friday<br />
                  9:00 AM - 6:00 PM PST<br />
                  <br />
                  <em>Closed on weekends and US holidays</em>
                </p>
              </div>
            </div>
          </section>
        </>
      )}
    </DocLayout>
  );
};

export default Contact;
