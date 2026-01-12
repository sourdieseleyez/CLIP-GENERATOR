import { useState, useRef, useEffect } from 'react';
import { motion, useScroll, useTransform, AnimatePresence } from 'framer-motion';
import {
  Twitch,
  Video,
  Share2,
  Check,
  Cpu,
  Play,
  ArrowRight,
  Youtube
} from 'lucide-react';

const LandingPage = ({ onGetStarted, onNavigate }) => {
  const { scrollYProgress } = useScroll();
  const y = useTransform(scrollYProgress, [0, 1], [0, -50]);

  // Demo Slideshow State
  const [demoStep, setDemoStep] = useState(0);
  const demoSteps = [
    { title: "Connect", desc: "Link Twitch/Kick Account", icon: <Twitch size={40} /> },
    { title: "Analyze", desc: "AI Scans VODs & Chat", icon: <Cpu size={40} /> },
    { title: "Clip", desc: "Auto-Generate Viral Clips", icon: <Video size={40} /> },
    { title: "Share", desc: "One-Click Social Posting", icon: <Share2 size={40} /> }
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setDemoStep((prev) => (prev + 1) % demoSteps.length);
    }, 3000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="font-body text-light-text bg-night-sky min-h-screen overflow-x-hidden selection:bg-cyber-blue selection:text-night-sky">

      {/* Background Ambience */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyber-blue rounded-full filter blur-[120px] opacity-15 animate-pulse"></div>
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-chrome rounded-full filter blur-[150px] opacity-5 animate-pulse" style={{ animationDelay: '2s' }}></div>
        <div className="absolute inset-0 bg-grainy-pattern opacity-30"></div>
      </div>

      {/* Navbar */}
      <nav className="fixed top-0 w-full z-50 glass-nav border-b border-white/10 backdrop-blur-md bg-night-sky/70">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center">
            <img src="/logos/logo-full.svg" alt="ClipGen Logo" className="h-8 md:h-10 w-auto" />
          </div>
          <div className="hidden md:flex gap-8 items-center">
            <a href="#features" className="hover:text-cyber-blue transition-colors">Features</a>
            <a href="#demo" className="hover:text-cyber-blue transition-colors">How it Works</a>
            <a href="#pricing" className="hover:text-cyber-blue transition-colors">Pricing</a>
            <button
              onClick={onGetStarted}
              className="bg-cyber-blue text-night-sky font-bold py-2 px-6 rounded-lg hover:bg-white hover:shadow-cyber-glow transition-all transform hover:-translate-y-0.5 font-heading"
            >
              Get Started
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 md:pt-44 md:pb-28 container mx-auto px-6 md:px-12 lg:px-20 z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-5xl"
        >
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-heading text-white mb-6 leading-tight text-left">
            Your Stream Highlights, Clipped & Posted{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyber-blue to-chrome drop-shadow-[0_0_15px_rgba(230,0,18,0.5)]">
              While You Sleep
            </span>
          </h1>

          <p className="text-lg md:text-xl lg:text-2xl text-light-text/80 max-w-4xl mb-10 font-light text-left leading-relaxed">
            Ditch the 3am editing grind. Our AI watches your streams, spots the bangers, adds captions, and drops them straight to TikTok & Shorts — all on autopilot.
          </p>

          <div className="flex flex-col sm:flex-row gap-5 items-start">
            <button
              onClick={onGetStarted}
              className="group relative px-8 py-4 bg-cyber-blue text-night-sky font-bold text-lg rounded-xl hover:bg-white transition-all shadow-cyber-glow overflow-hidden"
            >
              <span className="relative z-10 flex items-center gap-2">
                Start Clipping Free <ArrowRight className="group-hover:translate-x-1 transition-transform" />
              </span>
            </button>
            <a href="#demo" className="flex items-center gap-2 text-white hover:text-cyber-blue transition-colors py-4">
              <Play size={20} className="fill-current" /> Watch Demo
            </a>
          </div>
        </motion.div>
      </section>

      {/* Rich Features Section */}
      <section id="features" className="py-32 relative z-10">
        <div className="container mx-auto px-6 space-y-32">

          {/* Feature 1: Smart Detection */}
          <div className="flex flex-col md:flex-row items-center gap-16">
            <motion.div
              className="md:w-1/2"
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <h3 className="text-4xl md:text-5xl font-heading text-white mb-6 leading-tight">
                Smart Detection <br />
                <span className="text-gray-500">Finds the Gold.</span>
              </h3>
              <p className="text-xl text-gray-400 leading-relaxed mb-8">
                Our advanced AI models analyze hours of content in minutes. We identify high-energy moments, laughter, and chat spikes to find exactly what will go viral.
              </p>
              <ul className="space-y-4">
                <li className="flex items-center gap-3 text-gray-300">
                  <div className="p-1 rounded bg-green-500/20 text-green-400"><Check size={16} /></div>
                  Sentiment Analysis
                </li>
                <li className="flex items-center gap-3 text-gray-300">
                  <div className="p-1 rounded bg-green-500/20 text-green-400"><Check size={16} /></div>
                  Chat Reaction Tracking
                </li>
              </ul>
            </motion.div>
            <motion.div
              className="md:w-1/2"
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <div className="relative rounded-2xl overflow-hidden shadow-2xl shadow-cyber-blue/20 border border-white/10 group">
                <div className="absolute inset-0 bg-cyber-blue/10 opacity-0 group-hover:opacity-100 transition-opacity z-10"></div>
                <img src="/smart-detection.png" alt="Smart Detection Interface" className="w-full h-auto transform group-hover:scale-105 transition-transform duration-700" />
              </div>
            </motion.div>
          </div>

          {/* Feature 2: Auto Captions (Reversed Layout) */}
          <div className="flex flex-col md:flex-row-reverse items-center gap-16">
            <motion.div
              className="md:w-1/2"
              initial={{ opacity: 0, x: 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <h3 className="text-4xl md:text-5xl font-heading text-white mb-6 leading-tight">
                Attention-Grabbing <br />
                <span className="text-gray-500">Auto Captions.</span>
              </h3>
              <p className="text-xl text-gray-400 leading-relaxed mb-8">
                Grab attention instantly with dynamic, burned-in captions. Customize fonts, colors, and animations to match your brand identity perfectly.
              </p>
              <ul className="space-y-4">
                <li className="flex items-center gap-3 text-gray-300">
                  <div className="p-1 rounded bg-chrome/20 text-chrome"><Check size={16} /></div>
                  98% Accuracy Transcription
                </li>
                <li className="flex items-center gap-3 text-gray-300">
                  <div className="p-1 rounded bg-chrome/20 text-chrome"><Check size={16} /></div>
                  Keyword Highlighting
                </li>
              </ul>
            </motion.div>
            <motion.div
              className="md:w-1/2"
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <div className="relative rounded-2xl overflow-hidden shadow-2xl shadow-chrome/20 border border-white/10 group">
                <div className="absolute inset-0 bg-chrome/10 opacity-0 group-hover:opacity-100 transition-opacity z-10"></div>
                <img src="/auto-captions.png" alt="Auto Captions Example" className="w-full h-auto transform group-hover:scale-105 transition-transform duration-700" />
              </div>
            </motion.div>
          </div>

          {/* Feature 3: Face Tracking */}
          <div className="flex flex-col md:flex-row items-center gap-16">
            <motion.div
              className="md:w-1/2"
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <h3 className="text-4xl md:text-5xl font-heading text-white mb-6 leading-tight">
                Intelligent <br />
                <span className="text-gray-500">Face Tracking.</span>
              </h3>
              <p className="text-xl text-gray-400 leading-relaxed mb-8">
                Converting landscape to portrait? Our AI automatically tracks the active speaker and keeps them perfectly centered in the frame.
              </p>
              <ul className="space-y-4">
                <li className="flex items-center gap-3 text-gray-300">
                  <div className="p-1 rounded bg-white/10 text-white"><Check size={16} /></div>
                  Multi-Speaker Support
                </li>
                <li className="flex items-center gap-3 text-gray-300">
                  <div className="p-1 rounded bg-white/10 text-white"><Check size={16} /></div>
                  Automatic Gameplay Cropping
                </li>
              </ul>
            </motion.div>
            <motion.div
              className="md:w-1/2"
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <div className="relative rounded-2xl overflow-hidden shadow-2xl shadow-white/10 border border-white/10 group">
                <div className="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity z-10"></div>
                <img src="/face-tracking.png" alt="Face Tracking Visualization" className="w-full h-auto transform group-hover:scale-105 transition-transform duration-700" />
              </div>
            </motion.div>
          </div>

        </div>
      </section>

      {/* Dynamic Demo Slideshow */}
      <section id="demo" className="py-24 relative z-10 overflow-hidden">
        {/* Decorative Background Elements */}
        <div className="absolute top-0 right-0 w-1/2 h-full bg-cyber-blue/5 skew-x-12 -z-10 blur-3xl rounded-full opacity-20"></div>

        <div className="container mx-auto px-6">
          <div className="text-center mb-20 relative">
            <h2 className="text-4xl md:text-6xl font-heading text-white mb-6">
              How ClipGen <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyber-blue to-chrome">Works</span>
            </h2>
            <p className="text-xl md:text-2xl text-gray-400 font-light max-w-3xl mx-auto">
              Total automation from stream to social. <span className="text-white font-medium">zero effort required.</span>
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-16 items-center max-w-7xl mx-auto">
            {/* Steps List with Timeline */}
            <div className="relative space-y-8">
              {/* Connecting Line */}
              <div className="absolute left-8 top-8 bottom-8 w-1 bg-white/10 rounded-full hidden md:block">
                <motion.div
                  className="w-full bg-gradient-to-b from-cyber-blue to-chrome rounded-full"
                  animate={{ height: `${((demoStep + 1) / demoSteps.length) * 100}%` }}
                  transition={{ ease: "linear", duration: 0.5 }}
                />
              </div>

              {demoSteps.map((step, index) => (
                <motion.div
                  key={index}
                  className={`relative pl-0 md:pl-24 group cursor-pointer`}
                  onClick={() => setDemoStep(index)}
                  initial={{ opacity: 0, x: -50 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                >
                  {/* Timeline Node */}
                  <div className={`absolute left-5 top-1/2 -translate-y-1/2 w-7 h-7 rounded-full border-4 z-10 transition-all duration-500 hidden md:block ${index <= demoStep
                    ? 'bg-cyber-blue border-cyber-blue shadow-[0_0_15px_rgba(230,0,18,0.6)]'
                    : 'bg-night-sky border-white/20'
                    }`}>
                    {index === demoStep && (
                      <div className="absolute inset-0 w-full h-full animate-ping rounded-full bg-cyber-blue/50"></div>
                    )}
                  </div>

                  {/* Card Content */}
                  <div className={`p-6 rounded-2xl border transition-all duration-300 relative overflow-hidden ${index === demoStep
                    ? 'bg-white/10 border-cyber-blue/50 shadow-cyber-glow'
                    : 'bg-white/5 border-white/5 hover:border-white/20 hover:bg-white/10'
                    }`}>

                    {/* Active State Highlight */}
                    {index === demoStep && (
                      <motion.div
                        layoutId="activeGlow"
                        className="absolute inset-0 bg-gradient-to-r from-cyber-blue/10 to-transparent pointer-events-none"
                      />
                    )}

                    <div className="flex items-center gap-6 relative z-10">
                      <div className={`p-4 rounded-xl shadow-inner ${index === demoStep ? 'bg-cyber-blue text-night-sky' : 'bg-black/30 text-gray-500'
                        } transition-colors duration-300`}>
                        {step.icon}
                      </div>
                      <div>
                        <h3 className={`text-2xl font-bold font-heading mb-1 ${index === demoStep ? 'text-white' : 'text-gray-400'
                          } transition-colors duration-300`}>
                          {step.title}
                        </h3>
                        <p className="text-sm md:text-base text-gray-400">{step.desc}</p>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Visual Preview Window - Dynamic UI */}
            <div className="relative aspect-square md:aspect-video bg-[#050510] rounded-3xl border border-white/10 overflow-hidden shadow-2xl flex flex-col justify-center items-center group">
              {/* Persistent Streamer Background */}
              <div className="absolute inset-0 z-0">
                <img src="/streamer-action.png" className="w-full h-full object-cover opacity-20 filter blur-sm grayscale-[50%]" alt="Stream Background" />
                <div className="absolute inset-0 bg-[#050510]/80"></div>
              </div>
              {/* Window Decoration */}
              <div className="absolute top-0 left-0 right-0 h-12 bg-white/5 border-b border-white/10 flex items-center px-4 gap-2 z-20">
                <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
                <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
                <div className="ml-4 text-xs font-mono text-gray-500 flex-1 text-center opacity-50">clipgen-engine-v2.exe</div>
              </div>

              {/* Grid Background */}
              <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_at_center,black_40%,transparent_100%)]"></div>

              <AnimatePresence mode="wait">
                <motion.div
                  key={demoStep}
                  initial={{ opacity: 0, y: 20, scale: 0.9 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -20, scale: 1.1, filter: "blur(10px)" }}
                  transition={{ duration: 0.4, type: "spring" }}
                  className="relative z-10 w-full h-full flex items-center justify-center p-8 pt-20"
                >
                  {/* Custom Visuals Based on Step */}
                  {demoStep === 0 && (
                    <div className="flex items-center gap-8 md:gap-12">
                      <motion.div
                        animate={{ x: [0, 10, 0] }}
                        transition={{ repeat: Infinity, duration: 2 }}
                        className="w-24 h-24 bg-[#9146FF] rounded-2xl flex items-center justify-center shadow-[0_0_30px_#9146FF66]"
                      >
                        <Twitch size={48} className="text-white" />
                      </motion.div>
                      <div className="flex flex-col gap-1 items-center">
                        <div className="flex gap-1">
                          <motion.div animate={{ opacity: [0.2, 1, 0.2] }} transition={{ repeat: Infinity, duration: 1, delay: 0 }} className="w-2 h-2 rounded-full bg-cyber-blue" />
                          <motion.div animate={{ opacity: [0.2, 1, 0.2] }} transition={{ repeat: Infinity, duration: 1, delay: 0.2 }} className="w-2 h-2 rounded-full bg-cyber-blue" />
                          <motion.div animate={{ opacity: [0.2, 1, 0.2] }} transition={{ repeat: Infinity, duration: 1, delay: 0.4 }} className="w-2 h-2 rounded-full bg-cyber-blue" />
                        </div>
                        <div className="text-xs text-cyber-blue font-mono uppercase tracking-widest">Connecting</div>
                      </div>
                      <motion.div
                        animate={{ x: [0, -10, 0] }}
                        transition={{ repeat: Infinity, duration: 2 }}
                        className="w-24 h-24 bg-gradient-to-tr from-cyber-blue to-chrome rounded-2xl flex items-center justify-center shadow-[0_0_30px_rgba(230,0,18,0.4)]"
                      >
                        <Video size={48} className="text-white" />
                      </motion.div>
                    </div>
                  )}

                  {demoStep === 1 && (
                    <div className="w-full max-w-sm bg-black/50 rounded-xl border border-cyber-blue/30 p-4 font-mono text-xs overflow-hidden relative">
                      <div className="absolute top-0 left-0 w-full h-1 bg-cyber-blue/50 shadow-[0_0_15px_rgba(230,0,18,0.5)]">
                        <motion.div
                          className="h-full bg-cyber-blue"
                          animate={{ width: ["0%", "100%"] }}
                          transition={{ duration: 2, repeat: Infinity }}
                        />
                      </div>
                      <div className="space-y-2 opacity-80">
                        <div className="text-green-400 flex gap-2"><span className="text-gray-500">[10:02:44]</span> Analyzing audio stream...</div>
                        <div className="text-white flex gap-2"><span className="text-gray-500">[10:02:45]</span> Detected laugh event (Confidence: 98%)</div>
                        <div className="text-chrome flex gap-2"><span className="text-gray-500">[10:02:45]</span> Chat spike &gt; 50 msg/sec</div>
                        <div className="text-yellow-400 flex gap-2"><span className="text-gray-500">[10:02:46]</span> Gaming moment isolated</div>
                        <motion.div
                          initial={{ opacity: 0 }}
                          animate={{ opacity: [0, 1, 0] }}
                          transition={{ duration: 1, repeat: Infinity }}
                          className="text-cyber-blue font-bold mt-4"
                        >
                          PROCESSING SEGMENT ID_8829...
                        </motion.div>
                      </div>
                    </div>
                  )}

                  {demoStep === 2 && (
                    <div className="relative w-64 h-96 bg-gray-900 rounded-lg border-2 border-cyber-blue overflow-hidden shadow-[0_0_40px_rgba(230,0,18,0.2)]">
                      {/* Fake Video Content */}
                      <div className="absolute inset-x-0 top-0 bottom-20 bg-gray-800 flex items-center justify-center">
                        <img src="/streamer-action.png" className="w-full h-full object-cover opacity-50" alt="Clip Content" />
                        <Play size={48} className="absolute text-white/80" />
                      </div>
                      {/* Auto Caption Overlay */}
                      <motion.div
                        initial={{ y: 20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        className="absolute bottom-24 left-0 right-0 text-center"
                      >
                        <span className="bg-black/70 text-yellow-400 px-3 py-1 text-lg font-black italic uppercase rounded">
                          OMG WHAT A SHOT!
                        </span>
                      </motion.div>
                      {/* Timeline at bottom */}
                      <div className="absolute bottom-0 w-full h-20 bg-black/90 p-2 flex flex-col justify-center gap-2">
                        <div className="w-full h-8 bg-gray-700 rounded overflow-hidden relative">
                          <div className="absolute left-10 right-10 top-0 bottom-0 bg-cyber-blue/30 border-x-2 border-cyber-blue"></div>
                          <motion.div
                            className="h-full w-1 bg-white absolute top-0"
                            animate={{ left: ["20%", "80%"] }}
                            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                          />
                        </div>
                      </div>
                    </div>
                  )}

                  {demoStep === 3 && (
                    <div className="grid grid-cols-2 gap-4">
                      <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 0.1 }} className="bg-black p-4 rounded-xl border border-white/10 flex flex-col items-center gap-2">
                        <div className="p-2 bg-pink-600 rounded-full text-white"><Share2 size={24} /></div>
                        <div className="h-2 w-16 bg-gray-800 rounded"></div>
                        <div className="h-2 w-10 bg-gray-800 rounded"></div>
                        <div className="mt-2 text-xs text-green-400">Sent to TikTok</div>
                      </motion.div>
                      <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 0.3 }} className="bg-black p-4 rounded-xl border border-white/10 flex flex-col items-center gap-2">
                        <div className="p-2 bg-red-600 rounded-full text-white"><Youtube size={24} /></div>
                        <div className="h-2 w-16 bg-gray-800 rounded"></div>
                        <div className="h-2 w-10 bg-gray-800 rounded"></div>
                        <div className="mt-2 text-xs text-green-400">Sent to Shorts</div>
                      </motion.div>
                      <div className="col-span-2 text-center mt-4">
                        <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-500/20 text-green-400 rounded-full border border-green-500/30 font-bold">
                          <Check size={16} /> Viral Ready
                        </div>
                      </div>
                    </div>
                  )}

                </motion.div>
              </AnimatePresence>
            </div>
          </div>
        </div>
      </section>

      {/* Trusted By Logos - Marquee Style */}
      <section className="py-10 border-y border-white/5 bg-black/40 backdrop-blur-sm relative z-20">
        <div className="container mx-auto px-6 text-center">
          <p className="text-sm font-mono text-gray-500 mb-6 uppercase tracking-widest">Optimized For</p>
          <div className="flex flex-wrap justify-center items-center gap-12 md:gap-24 opacity-70 grayscale hover:grayscale-0 transition-all duration-500">
            {/* YouTube */}
            <div className="flex items-center gap-3 group">
              <Youtube size={32} className="text-red-600" />
              <span className="font-bold text-2xl tracking-tighter text-white group-hover:text-red-500 transition-colors hidden md:block">YouTube</span>
            </div>
            {/* Twitch */}
            <div className="flex items-center gap-3 group">
              <Twitch size={32} className="text-[#9146FF]" />
              <span className="font-bold text-2xl tracking-tighter text-white group-hover:text-[#9146FF] transition-colors hidden md:block">Twitch</span>
            </div>
            {/* Kick */}
            <div className="flex items-center gap-3 group">
              <div className="bg-white text-black font-black px-1.5 py-0.5 text-xl rounded-sm group-hover:bg-[#53FC18] transition-colors">KiCK</div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing with "Transparent" Model */}
      <section id="pricing" className="py-24 relative overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full bg-gradient-to-b from-transparent via-cyber-blue/5 to-transparent pointer-events-none"></div>

        <div className="container mx-auto px-6 relative z-10">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-heading text-white mb-6">Fair Usage Pricing</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              We charge based on the compute power we use, plus a sustainable reinvestment margin.
              <br />
              <b>Calculation: Backend GPU Cost + Deployment Overhead + 70% Growth Margin.</b>
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto items-center">
            {/* Starter */}
            <div className="p-8 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-sm">
              <h3 className="text-2xl font-heading text-white mb-2">Starter</h3>
              <div className="text-4xl font-bold text-cyber-blue mb-1">$0</div>
              <p className="text-sm text-gray-500 mb-6">Free forever</p>
              <ul className="space-y-4 mb-8 text-sm">
                <li className="flex items-center gap-2"><Check size={16} className="text-green-500" /> 3 AI Clips / mo</li>
                <li className="flex items-center gap-2"><Check size={16} className="text-green-500" /> 720p Resolution</li>
                <li className="flex items-center gap-2"><Check size={16} className="text-green-500" /> Manual Downloads</li>
              </ul>
              <button onClick={onGetStarted} className="w-full py-3 rounded-lg border border-white/20 hover:bg-white/10 text-white font-bold transition-all">Try Free</button>
            </div>

            {/* Pro - The Value Deal */}
            <motion.div
              whileHover={{ scale: 1.02 }}
              className="relative p-10 rounded-2xl bg-night-sky border border-cyber-blue shadow-[0_0_30px_rgba(230,0,18,0.3)] z-20"
            >
              <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-cyber-blue text-night-sky px-4 py-1 rounded-full font-bold text-xs uppercase tracking-wider">
                Most Popular
              </div>
              <h3 className="text-3xl font-heading text-white mb-2">Pro Streamer</h3>
              <div className="text-5xl font-bold text-cyber-blue mb-1">$29</div>
              <p className="text-sm text-gray-500 mb-6">per month</p>
              <div className="text-xs text-chrome bg-chrome/10 p-2 rounded mb-6 border border-chrome/20">
                Maintains 99.9% Production Uptime
              </div>
              <ul className="space-y-4 mb-8">
                <li className="flex items-center gap-3"><Check size={20} className="text-cyber-blue" /> <b>Unlimited</b> AI Clips</li>
                <li className="flex items-center gap-3"><Check size={20} className="text-cyber-blue" /> 1080p Crystal Clear</li>
                <li className="flex items-center gap-3"><Check size={20} className="text-cyber-blue" /> Auto-Post to TikTok/Shorts</li>
                <li className="flex items-center gap-3"><Check size={20} className="text-cyber-blue" /> Priority GPU Access</li>
              </ul>
              <button
                onClick={onGetStarted}
                className="w-full py-4 rounded-lg bg-cyber-blue text-night-sky font-bold hover:bg-white transition-colors shadow-cyber-glow"
              >
                Get Started
              </button>
            </motion.div>

            {/* Enterprise */}
            <div className="p-8 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-sm">
              <h3 className="text-2xl font-heading text-white mb-2">Agency</h3>
              <div className="text-4xl font-bold text-white mb-1">Custom</div>
              <p className="text-sm text-gray-500 mb-6 font-mono">Volume Discounts</p>
              <ul className="space-y-4 mb-8 text-sm">
                <li className="flex items-center gap-2"><Check size={16} className="text-green-500" /> Multiple Channels</li>
                <li className="flex items-center gap-2"><Check size={16} className="text-green-500" /> Custom Branding</li>
                <li className="flex items-center gap-2"><Check size={16} className="text-green-500" /> Dedicated Account Mgr</li>
                <li className="flex items-center gap-2"><Check size={16} className="text-green-500" /> API Access</li>
              </ul>
              <button className="w-full py-3 rounded-lg border border-white/20 hover:bg-white/10 text-white font-bold transition-all">Contact Sales</button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-16 bg-black/40">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-12 mb-12">
            {/* Brand */}
            <div>
              <div className="flex items-center mb-4">
                <img src="/logos/logo-full.svg" alt="ClipGen Logo" className="h-8 w-auto" />
              </div>
              <p className="text-gray-500 text-sm leading-relaxed">
                AI-powered clip generation for streamers and content creators. Turn your streams into viral moments.
              </p>
            </div>

            {/* Product */}
            <div>
              <h4 className="text-white font-heading text-sm uppercase tracking-wider mb-4">Product</h4>
              <ul className="space-y-3">
                <li><a href="#features" className="text-gray-400 hover:text-cyber-blue transition-colors text-sm">Features</a></li>
                <li><a href="#pricing" className="text-gray-400 hover:text-cyber-blue transition-colors text-sm">Pricing</a></li>
                <li><a href="#demo" className="text-gray-400 hover:text-cyber-blue transition-colors text-sm">How it Works</a></li>
                <li><button onClick={() => onNavigate?.('docs')} className="text-gray-400 hover:text-cyber-blue transition-colors text-sm bg-transparent border-none cursor-pointer p-0">Documentation</button></li>
              </ul>
            </div>

            {/* Company */}
            <div>
              <h4 className="text-white font-heading text-sm uppercase tracking-wider mb-4">Company</h4>
              <ul className="space-y-3">
                <li><button onClick={() => onNavigate?.('contact')} className="text-gray-400 hover:text-cyber-blue transition-colors text-sm bg-transparent border-none cursor-pointer p-0">Contact Us</button></li>
              </ul>
            </div>

            {/* Legal */}
            <div>
              <h4 className="text-white font-heading text-sm uppercase tracking-wider mb-4">Legal</h4>
              <ul className="space-y-3">
                <li><button onClick={() => onNavigate?.('privacy')} className="text-gray-400 hover:text-cyber-blue transition-colors text-sm bg-transparent border-none cursor-pointer p-0">Privacy Policy</button></li>
                <li><button onClick={() => onNavigate?.('terms')} className="text-gray-400 hover:text-cyber-blue transition-colors text-sm bg-transparent border-none cursor-pointer p-0">Terms of Service</button></li>
              </ul>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="pt-8 border-t border-white/10 flex flex-col md:flex-row justify-center items-center">
            <div className="text-gray-500 text-sm">
              © 2026 ClipGen Technologies. All rights reserved.
            </div>
          </div>
        </div>
      </footer>

    </div>
  );
};

export default LandingPage;
