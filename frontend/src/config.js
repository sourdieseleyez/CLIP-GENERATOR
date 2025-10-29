// API Configuration
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// UI Configuration
export const UI_CONFIG = {
  // App Info
  appName: 'Clip Generator',
  appTagline: 'Transform your videos into viral clips with AI',
  
  // Theme Colors (can be customized)
  colors: {
    primary: '#6366f1',
    primaryLight: '#818cf8',
    primaryDark: '#4f46e5',
    success: '#10b981',
    error: '#ef4444',
  },
  
  // File Upload Settings
  maxFileSize: 500 * 1024 * 1024, // 500MB
  acceptedVideoFormats: [
    'video/mp4',
    'video/quicktime',
    'video/x-msvideo',
    'video/x-matroska',
  ],
  
  // Animation Settings
  enableAnimations: true,
  transitionDuration: 300, // ms
};

export default { API_URL, UI_CONFIG };
