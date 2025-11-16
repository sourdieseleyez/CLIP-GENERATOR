import { useEffect } from 'react';

function LandingPage({ onSignUp }) {
  useEffect(() => {
    // Load the landing page content into an iframe or redirect
    // For simplicity, we'll redirect to the landing.html
    window.location.href = '/landing.html';
  }, []);

  return (
    <div style={{ width: '100%', height: '100vh' }}>
      <p>Loading...</p>
    </div>
  );
}

export default LandingPage;
