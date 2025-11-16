import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// Simple routing: if path is /app, show the app, otherwise redirect to landing page
const currentPath = window.location.pathname;

if (currentPath === '/app' || currentPath === '/app/') {
  // Show the React app
  createRoot(document.getElementById('root')).render(
    <StrictMode>
      <App />
    </StrictMode>,
  )
} else if (currentPath === '/' || currentPath === '') {
  // Redirect to landing page
  window.location.href = '/landing.html';
}
