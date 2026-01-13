// API Configuration
// In production (when built), use relative URLs so frontend and backend are on same domain
// In development, use localhost backend
export const API_URL = import.meta.env.VITE_API_URL || 
  (import.meta.env.PROD ? '' : 'http://localhost:8000');

// File size limits by plan
export const FILE_SIZE_LIMITS = {
  FREE: 500 * 1024 * 1024,      // 500MB
  PRO: 5 * 1024 * 1024 * 1024,  // 5GB
  AGENCY: 5 * 1024 * 1024 * 1024, // 5GB
};

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
  
  // File Upload Settings - Default to free tier, will be updated from API
  maxFileSize: FILE_SIZE_LIMITS.FREE,
  maxFileSizePro: FILE_SIZE_LIMITS.PRO,
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

// Helper to format file size for display
export const formatFileSize = (bytes) => {
  if (bytes >= 1024 * 1024 * 1024) {
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)}GB`;
  }
  return `${Math.round(bytes / (1024 * 1024))}MB`;
};

// Allow disabling auth in the frontend for local dev: set VITE_DISABLE_AUTH=true
export const DISABLE_AUTH = (import.meta.env.VITE_DISABLE_AUTH || 'false') === 'true';

export default { API_URL, UI_CONFIG, DISABLE_AUTH, FILE_SIZE_LIMITS, formatFileSize };
