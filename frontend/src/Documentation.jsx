import DocLayout from './DocLayout';
import { BookOpen, Zap, Video, Settings, Upload, Sparkles, Share2, Code, HelpCircle, MessageSquare, Briefcase } from 'lucide-react';

const sections = [
  { id: 'getting-started', title: 'Getting Started' },
  { id: 'uploading', title: 'Uploading Videos' },
  { id: 'ai-analysis', title: 'AI Analysis' },
  { id: 'clip-generation', title: 'Generating Clips' },
  { id: 'captions', title: 'Captions & Subtitles' },
  { id: 'publishing', title: 'Publishing' },
  { id: 'marketplace', title: 'Marketplace' },
  { id: 'api', title: 'API Reference' },
  { id: 'glossary', title: 'Glossary' },
  { id: 'faq', title: 'FAQ' }
];

const Documentation = ({ onBack }) => {
  return (
    <DocLayout title="Documentation" sections={sections} onBack={onBack}>
      {(registerRef) => (
        <>
          <p className="doc-meta">Complete guide to using ClipGen</p>

          <section className="doc-section" id="getting-started" ref={registerRef('getting-started')}>
            <h2><Zap size={20} /> Getting Started</h2>
            <p>
              Welcome to ClipGen! This documentation will help you get the most out of our AI-powered 
              video clipping platform. Whether you're a streamer, content creator, or agency, we've 
              got you covered.
            </p>

            <h3>Quick Start Guide</h3>
            <ol>
              <li><strong>Create an account</strong> - Sign up with your email or connect via Twitch/Google</li>
              <li><strong>Upload a video</strong> - Drop your VOD, stream recording, or paste a YouTube URL</li>
              <li><strong>Configure settings</strong> - Choose clip count, duration, and format</li>
              <li><strong>Generate clips</strong> - Let our AI analyze and create viral-worthy moments</li>
              <li><strong>Download or publish</strong> - Export clips or post directly to social media</li>
            </ol>

            <div className="doc-highlight success">
              <p>
                <strong>Pro Tip:</strong> Start with a 10-30 minute video for best results. Our AI 
                performs optimally with content that has clear audio and varied engagement moments.
              </p>
            </div>

            <h3>System Requirements</h3>
            <ul>
              <li>Modern web browser (Chrome, Firefox, Safari, Edge)</li>
              <li>Stable internet connection (10+ Mbps recommended for uploads)</li>
              <li>JavaScript enabled</li>
            </ul>
          </section>

          <section className="doc-section" id="uploading" ref={registerRef('uploading')}>
            <h2><Upload size={20} /> Uploading Videos</h2>
            
            <h3>Supported Formats</h3>
            <table className="doc-table">
              <thead>
                <tr>
                  <th>Format</th>
                  <th>Extension</th>
                  <th>Max Size</th>
                </tr>
              </thead>
              <tbody>
                <tr><td>MP4</td><td>.mp4</td><td>5 GB</td></tr>
                <tr><td>MOV</td><td>.mov</td><td>5 GB</td></tr>
                <tr><td>WebM</td><td>.webm</td><td>5 GB</td></tr>
                <tr><td>AVI</td><td>.avi</td><td>5 GB</td></tr>
                <tr><td>MKV</td><td>.mkv</td><td>5 GB</td></tr>
              </tbody>
            </table>

            <h3>Upload Methods</h3>
            <p><strong>Direct Upload:</strong> Drag and drop or click to select a file from your device.</p>
            <p><strong>YouTube URL:</strong> Paste a YouTube video URL to import directly (you must own the content).</p>
            <p><strong>Direct URL:</strong> Provide a direct link to a video file hosted elsewhere.</p>

            <div className="doc-highlight warning">
              <p>
                <strong>Important:</strong> Only upload content you have rights to use. Uploading 
                copyrighted content without permission violates our Terms of Service.
              </p>
            </div>

            <h3>Upload Tips</h3>
            <ul>
              <li>Use H.264 codec for fastest processing</li>
              <li>Ensure audio is clear and not heavily compressed</li>
              <li>Videos with face-cam perform better for vertical clips</li>
              <li>Avoid videos with excessive background music</li>
            </ul>
          </section>

          <section className="doc-section" id="ai-analysis" ref={registerRef('ai-analysis')}>
            <h2><Sparkles size={20} /> AI Analysis</h2>
            <p>
              ClipGen uses advanced AI models to analyze your video content and identify the most 
              engaging moments. Here's how it works:
            </p>

            <h3>Analysis Pipeline</h3>
            <ol>
              <li><strong>Audio Transcription</strong> - Speech-to-text conversion with speaker detection</li>
              <li><strong>Sentiment Analysis</strong> - Detecting emotional peaks and reactions</li>
              <li><strong>Visual Analysis</strong> - Identifying action, expressions, and key visuals</li>
              <li><strong>Engagement Scoring</strong> - Ranking moments by viral potential</li>
              <li><strong>Clip Selection</strong> - Choosing optimal start/end points</li>
            </ol>

            <h3>What Makes a "Viral" Moment?</h3>
            <p>Our AI looks for:</p>
            <ul>
              <li>Emotional reactions (laughter, surprise, excitement)</li>
              <li>Quotable statements or hot takes</li>
              <li>Impressive gameplay or skill demonstrations</li>
              <li>Unexpected events or plot twists</li>
              <li>High chat activity (for Twitch VODs)</li>
              <li>Clear, punchy dialogue</li>
            </ul>

            <h3>AI Models Used</h3>
            <div className="doc-code">
              Primary: Google Gemini 1.5 Pro (video understanding)
              Secondary: GPT-4 Turbo (caption optimization)
              Audio: Whisper Large V3 (transcription)
            </div>
          </section>

          <section className="doc-section" id="clip-generation" ref={registerRef('clip-generation')}>
            <h2><Video size={20} /> Generating Clips</h2>
            
            <h3>Configuration Options</h3>
            <table className="doc-table">
              <thead>
                <tr>
                  <th>Option</th>
                  <th>Values</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Number of Clips</td>
                  <td>3, 5, 8, 10</td>
                  <td>How many clips to generate</td>
                </tr>
                <tr>
                  <td>Clip Duration</td>
                  <td>15s, 30s, 45s, 60s</td>
                  <td>Target length for each clip</td>
                </tr>
                <tr>
                  <td>Format</td>
                  <td>Portrait, Landscape, Square</td>
                  <td>Output aspect ratio</td>
                </tr>
              </tbody>
            </table>

            <h3>Format Recommendations</h3>
            <ul>
              <li><strong>Portrait (9:16)</strong> - TikTok, Instagram Reels, YouTube Shorts</li>
              <li><strong>Landscape (16:9)</strong> - YouTube, Twitter, Facebook</li>
              <li><strong>Square (1:1)</strong> - Instagram Feed, LinkedIn</li>
            </ul>

            <h3>Processing Time</h3>
            <p>
              Processing time depends on video length and server load. Typical times:
            </p>
            <ul>
              <li>10-minute video: 2-4 minutes</li>
              <li>30-minute video: 5-10 minutes</li>
              <li>1-hour video: 15-25 minutes</li>
            </ul>
          </section>

          <section className="doc-section" id="captions" ref={registerRef('captions')}>
            <h2><MessageSquare size={20} /> Captions & Subtitles</h2>
            <p>
              ClipGen automatically generates captions for all clips using advanced speech recognition.
            </p>

            <h3>Caption Styles</h3>
            <ul>
              <li><strong>Standard</strong> - Clean, readable subtitles</li>
              <li><strong>Hormozi Style</strong> - Bold, animated text with emphasis</li>
              <li><strong>Minimal</strong> - Small, unobtrusive captions</li>
              <li><strong>Custom</strong> - Define your own font, size, and colors</li>
            </ul>

            <h3>Export Formats</h3>
            <ul>
              <li><strong>Burned-in</strong> - Captions rendered directly on video</li>
              <li><strong>SRT</strong> - Standard subtitle file for external use</li>
              <li><strong>VTT</strong> - Web-compatible subtitle format</li>
            </ul>

            <h3>Editing Captions</h3>
            <p>
              You can edit auto-generated captions before export. Click on any caption segment 
              to modify the text, timing, or styling.
            </p>
          </section>

          <section className="doc-section" id="publishing" ref={registerRef('publishing')}>
            <h2><Share2 size={20} /> Publishing</h2>
            
            <h3>Supported Platforms</h3>
            <ul>
              <li>TikTok (direct upload)</li>
              <li>YouTube Shorts (via YouTube API)</li>
              <li>Instagram Reels (via Meta API)</li>
              <li>Twitter/X (video posts)</li>
              <li>Facebook (video posts)</li>
            </ul>

            <h3>Connecting Accounts</h3>
            <p>
              Go to Settings → Connected Accounts to link your social media profiles. We use 
              OAuth for secure authentication and never store your passwords.
            </p>

            <h3>Scheduling</h3>
            <p>
              Pro users can schedule clips for future posting. Set your preferred posting times 
              and let ClipGen handle the rest.
            </p>

            <div className="doc-highlight">
              <p>
                <strong>Best Posting Times:</strong> Our analytics show highest engagement for 
                gaming content between 6-9 PM local time on weekdays.
              </p>
            </div>
          </section>

          <section className="doc-section" id="marketplace" ref={registerRef('marketplace')}>
            <h2><Briefcase size={20} /> Marketplace</h2>
            <p>
              The ClipGen Marketplace connects content creators with skilled video editors.
            </p>

            <h3>For Creators</h3>
            <ul>
              <li>Post campaigns with your video content</li>
              <li>Set requirements (clip count, style, duration)</li>
              <li>Review and approve submitted clips</li>
              <li>Pay only for clips you accept</li>
            </ul>

            <h3>For Editors</h3>
            <ul>
              <li>Browse available campaigns</li>
              <li>Claim jobs that match your skills</li>
              <li>Submit clips for review</li>
              <li>Earn money for approved work</li>
            </ul>

            <h3>Payment Structure</h3>
            <table className="doc-table">
              <thead>
                <tr>
                  <th>Item</th>
                  <th>Rate</th>
                </tr>
              </thead>
              <tbody>
                <tr><td>Platform fee</td><td>15% of job value</td></tr>
                <tr><td>Minimum payout</td><td>$25</td></tr>
                <tr><td>Payment methods</td><td>PayPal, Stripe, Bank Transfer</td></tr>
                <tr><td>Payout schedule</td><td>Weekly (Fridays)</td></tr>
              </tbody>
            </table>
          </section>

          <section className="doc-section" id="api" ref={registerRef('api')}>
            <h2><Code size={20} /> API Reference</h2>
            <p>
              Agency and Enterprise users have access to our REST API for programmatic integration.
            </p>

            <h3>Authentication</h3>
            <div className="doc-code">
              Authorization: Bearer YOUR_API_KEY
            </div>

            <h3>Base URL</h3>
            <div className="doc-code">
              https://api.clipgen.io/v1
            </div>

            <h3>Key Endpoints</h3>
            <table className="doc-table">
              <thead>
                <tr>
                  <th>Endpoint</th>
                  <th>Method</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                <tr><td>/videos/upload</td><td>POST</td><td>Upload a video file</td></tr>
                <tr><td>/videos/process</td><td>POST</td><td>Start clip generation</td></tr>
                <tr><td>/jobs/{'{id}'}</td><td>GET</td><td>Check job status</td></tr>
                <tr><td>/clips</td><td>GET</td><td>List generated clips</td></tr>
                <tr><td>/clips/{'{id}'}/download</td><td>GET</td><td>Download a clip</td></tr>
              </tbody>
            </table>

            <h3>Rate Limits</h3>
            <ul>
              <li>Pro: 100 requests/minute</li>
              <li>Agency: 500 requests/minute</li>
              <li>Enterprise: Custom limits</li>
            </ul>
          </section>

          <section className="doc-section" id="glossary" ref={registerRef('glossary')}>
            <h2><BookOpen size={20} /> Glossary</h2>
            
            <dl>
              <div className="glossary-term">
                <dt>VOD (Video on Demand)</dt>
                <dd>A recorded video, typically a past livestream, available for viewing at any time.</dd>
              </div>
              
              <div className="glossary-term">
                <dt>Clip</dt>
                <dd>A short segment extracted from a longer video, typically 15-60 seconds.</dd>
              </div>
              
              <div className="glossary-term">
                <dt>Viral Potential</dt>
                <dd>A score indicating how likely a clip is to gain significant engagement on social media.</dd>
              </div>
              
              <div className="glossary-term">
                <dt>Burned-in Captions</dt>
                <dd>Subtitles that are permanently rendered onto the video, visible without player support.</dd>
              </div>
              
              <div className="glossary-term">
                <dt>Aspect Ratio</dt>
                <dd>The proportional relationship between a video's width and height (e.g., 16:9, 9:16).</dd>
              </div>
              
              <div className="glossary-term">
                <dt>Transcription</dt>
                <dd>The process of converting spoken audio into written text.</dd>
              </div>
              
              <div className="glossary-term">
                <dt>OAuth</dt>
                <dd>A secure authorization protocol that allows third-party access without sharing passwords.</dd>
              </div>
              
              <div className="glossary-term">
                <dt>Campaign</dt>
                <dd>A marketplace listing where creators request clips from editors.</dd>
              </div>
              
              <div className="glossary-term">
                <dt>Job</dt>
                <dd>A claimed campaign task that an editor is working on.</dd>
              </div>
              
              <div className="glossary-term">
                <dt>Engagement Score</dt>
                <dd>A metric measuring viewer interaction (likes, comments, shares, watch time).</dd>
              </div>
            </dl>
          </section>

          <section className="doc-section" id="faq" ref={registerRef('faq')}>
            <h2><HelpCircle size={20} /> Frequently Asked Questions</h2>
            
            <h3>How accurate is the AI?</h3>
            <p>
              Our AI correctly identifies engaging moments approximately 85% of the time. Results 
              improve with clear audio and varied content. You can always regenerate or manually 
              adjust clips.
            </p>

            <h3>Can I use ClipGen for copyrighted content?</h3>
            <p>
              You may only process content you own or have explicit permission to use. We are not 
              responsible for copyright violations.
            </p>

            <h3>How long are clips stored?</h3>
            <p>
              Free users: 90 days. Pro users: 1 year. You can download clips at any time before 
              expiration.
            </p>

            <h3>Can I edit clips after generation?</h3>
            <p>
              Yes! You can trim, adjust captions, and modify styling before downloading or publishing.
            </p>

            <h3>What happens if processing fails?</h3>
            <p>
              Failed jobs don't count against your quota. Check that your video meets our format 
              requirements and try again. Contact support if issues persist.
            </p>

            <h3>Is there a mobile app?</h3>
            <p>
              Not yet, but our web app is fully responsive and works great on mobile browsers. 
              A native app is on our roadmap.
            </p>

            <h3>How do I cancel my subscription?</h3>
            <p>
              Go to Settings → Billing → Cancel Subscription. You'll retain access until the end 
              of your billing period.
            </p>
          </section>
        </>
      )}
    </DocLayout>
  );
};

export default Documentation;
