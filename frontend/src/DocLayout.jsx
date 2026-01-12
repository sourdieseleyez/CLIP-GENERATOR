import { useState, useEffect, useRef } from 'react';
import { Video, ChevronRight, ArrowLeft } from 'lucide-react';
import './DocLayout.css';

const DocLayout = ({ title, sections, children, onBack }) => {
  const [activeSection, setActiveSection] = useState(sections[0]?.id || '');
  const contentRef = useRef(null);
  const sectionRefs = useRef({});

  useEffect(() => {
    const handleScroll = () => {
      if (!contentRef.current) return;
      
      const scrollTop = contentRef.current.scrollTop;
      const offset = 120;
      
      let currentSection = sections[0]?.id;
      
      for (const section of sections) {
        const element = sectionRefs.current[section.id];
        if (element) {
          const rect = element.getBoundingClientRect();
          const containerRect = contentRef.current.getBoundingClientRect();
          const relativeTop = rect.top - containerRect.top;
          
          if (relativeTop <= offset) {
            currentSection = section.id;
          }
        }
      }
      
      setActiveSection(currentSection);
    };

    const container = contentRef.current;
    if (container) {
      container.addEventListener('scroll', handleScroll);
      handleScroll();
    }

    return () => {
      if (container) {
        container.removeEventListener('scroll', handleScroll);
      }
    };
  }, [sections]);

  const scrollToSection = (sectionId) => {
    const element = sectionRefs.current[sectionId];
    if (element && contentRef.current) {
      const containerRect = contentRef.current.getBoundingClientRect();
      const elementRect = element.getBoundingClientRect();
      const scrollTop = contentRef.current.scrollTop + elementRect.top - containerRect.top - 100;
      
      contentRef.current.scrollTo({
        top: scrollTop,
        behavior: 'smooth'
      });
    }
  };

  const registerRef = (id) => (el) => {
    sectionRefs.current[id] = el;
  };

  return (
    <div className="doc-layout">
      {/* Header */}
      <header className="doc-header">
        <div className="doc-header-content">
          <div className="doc-brand" onClick={onBack}>
            <Video className="brand-icon" />
            <span>Clip<span className="brand-accent">Gen</span></span>
          </div>
          <button className="back-btn" onClick={onBack}>
            <ArrowLeft size={18} />
            Back to Home
          </button>
        </div>
      </header>

      <div className="doc-container">
        {/* Sidebar */}
        <aside className="doc-sidebar">
          <div className="sidebar-sticky">
            <h3 className="sidebar-title">{title}</h3>
            <nav className="sidebar-nav">
              {sections.map((section) => (
                <button
                  key={section.id}
                  className={`sidebar-link ${activeSection === section.id ? 'active' : ''}`}
                  onClick={() => scrollToSection(section.id)}
                >
                  <span className="link-indicator"></span>
                  <span className="link-text">{section.title}</span>
                  <ChevronRight size={14} className="link-arrow" />
                </button>
              ))}
            </nav>
          </div>
        </aside>

        {/* Main Content */}
        <main className="doc-content" ref={contentRef}>
          <div className="doc-content-inner">
            <h1 className="doc-title">{title}</h1>
            {typeof children === 'function' ? children(registerRef) : children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default DocLayout;
