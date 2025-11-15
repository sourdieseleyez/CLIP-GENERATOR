import { useState } from 'react';
import { Upload, Youtube, CheckCircle } from 'lucide-react';
import { API_URL } from './config';
import './SubmitJob.css';

function SubmitJob({ token, job, clips, onSuccess }) {
  const [selectedClips, setSelectedClips] = useState([]);
  const [youtubeUrls, setYoutubeUrls] = useState({});
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);

  const toggleClip = (clipId) => {
    setSelectedClips(prev => 
      prev.includes(clipId) 
        ? prev.filter(id => id !== clipId)
        : [...prev, clipId]
    );
  };

  const handleSubmit = async () => {
    if (selectedClips.length === 0) {
      alert('Please select at least one clip to submit');
      return;
    }

    setUploading(true);
    setUploadStatus('Uploading clips to YouTube...');

    const uploadResults = [];
    
    try {
      // Upload each selected clip with individual error handling
      for (const clipId of selectedClips) {
        const clip = clips.find(c => c.id === clipId);
        
        try {
          setUploadStatus(`Uploading clip ${clipId}... (${uploadResults.length + 1}/${selectedClips.length})`);
          
          const uploadResponse = await fetch(`${API_URL}/youtube/upload`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
              clip_id: clipId,
              job_id: job.job_id,
              title: `${job.campaign?.title || 'Clip'} - Clip ${clipId}`,
              description: `Generated clip from campaign: ${job.campaign?.title || 'Campaign'}\n\nTracking: ${job.tracking_code || 'pending'}`,
              tags: ['shorts', 'viral', 'clips']
            })
          });

          if (uploadResponse.ok) {
            const uploadData = await uploadResponse.json();
            uploadResults.push({
              clipId,
              success: true,
              youtube_url: uploadData.youtube_url,
              video_id: uploadData.video_id
            });
            youtubeUrls[clipId] = uploadData.youtube_url;
          } else {
            const errorData = await uploadResponse.json().catch(() => ({}));
            uploadResults.push({
              clipId,
              success: false,
              error: errorData.detail || 'Upload failed'
            });
          }
        } catch (error) {
          uploadResults.push({
            clipId,
            success: false,
            error: error.message
          });
        }
      }

      // Check if at least one upload succeeded
      const successfulUploads = uploadResults.filter(r => r.success);
      
      if (successfulUploads.length === 0) {
        throw new Error('All uploads failed. Please try again.');
      }

      // Submit job with the first successful upload
      setUploadStatus(`Submitting ${successfulUploads.length} successful upload(s)...`);
      const submitResponse = await fetch(`${API_URL}/marketplace/jobs/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          job_id: job.job_id,
          clip_id: successfulUploads[0].clipId,
          youtube_url: successfulUploads[0].youtube_url
        })
      });

      if (!submitResponse.ok) {
        const errorData = await submitResponse.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to submit job');
      }

      // Show summary
      const failedCount = uploadResults.length - successfulUploads.length;
      if (failedCount > 0) {
        setUploadStatus(`Success! ${successfulUploads.length} clip(s) submitted. ${failedCount} upload(s) failed.`);
      } else {
        setUploadStatus('Success! All clips submitted for review.');
      }
      
      setTimeout(() => {
        if (onSuccess) onSuccess();
      }, 2000);

    } catch (error) {
      setUploadStatus(`Error: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="submit-job-container">
      <div className="submit-header">
        <h2>
          <Upload size={24} />
          Submit to Campaign
        </h2>
        <p>Select clips to upload and submit for review</p>
      </div>

      <div className="job-info">
        <h3>{job.campaign?.title || 'Campaign'}</h3>
        <div className="job-details">
          <span>Your Earnings: ${job.your_earnings || job.clipper_share || 0}</span>
          <span>Campaign Budget: ${job.agreed_price || 0}</span>
        </div>
      </div>

      <div className="clips-selection">
        <h3>Select Clips to Submit</h3>
        <div className="clips-grid">
          {clips.map((clip) => (
            <div 
              key={clip.id} 
              className={`clip-card ${selectedClips.includes(clip.id) ? 'selected' : ''}`}
              onClick={() => toggleClip(clip.id)}
            >
              {selectedClips.includes(clip.id) && (
                <div className="selected-badge">
                  <CheckCircle size={20} />
                </div>
              )}
              <div className="clip-preview">
                {clip.url ? (
                  <video src={clip.url} controls width={240} />
                ) : (
                  <video src={`${API_URL}/clips/${clip.id}/download`} controls width={240} />
                )}
              </div>
              <div className="clip-info">
                <strong>Clip #{clip.id}</strong>
                <small>{clip.start}s - {clip.end}s</small>
              </div>
              <p className="clip-text">"{clip.text}"</p>
            </div>
          ))}
        </div>
      </div>

      {uploadStatus && (
        <div className={`upload-status ${uploadStatus.includes('Error') ? 'error' : 'info'}`}>
          {uploadStatus}
        </div>
      )}

      <div className="submit-actions">
        <button 
          className="submit-btn"
          onClick={handleSubmit}
          disabled={uploading || selectedClips.length === 0}
        >
          <Youtube size={18} />
          {uploading ? 'Uploading...' : `Submit ${selectedClips.length} Clip(s)`}
        </button>
      </div>
    </div>
  );
}

export default SubmitJob;
