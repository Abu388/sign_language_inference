import React, { useState, useEffect, useRef } from 'react';

interface SignVideoPlayerProps {
  text: string;
  autoPlay?: boolean;
}

const SignVideoPlayer: React.FC<SignVideoPlayerProps> = ({ text, autoPlay = true }) => {
  const [videoUrls, setVideoUrls] = useState<string[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (!text.trim()) {
      setVideoUrls([]);
      setCurrentIndex(0);
      return;
    }

    const fetchVideos = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch('http://localhost:8000/api/text-to-video', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text }),
        });
        if (!response.ok) throw new Error('Failed to fetch videos');
        const data = await response.json();
        setVideoUrls(data.video_urls);
        setCurrentIndex(0);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchVideos();
  }, [text]);

  useEffect(() => {
    if (videoRef.current && videoUrls.length > 0 && autoPlay) {
      videoRef.current.load();
      videoRef.current.play().catch(e => console.warn('Autoplay prevented:', e));
    }
  }, [currentIndex, videoUrls, autoPlay]);

  const handleVideoEnd = () => {
    if (currentIndex + 1 < videoUrls.length) {
      setCurrentIndex(prev => prev + 1);
    }
  };

  if (loading) return <p className="svp-loading">Loading sign videos...</p>;
  if (error) return <p className="svp-error">Error: {error}</p>;
  if (videoUrls.length === 0) return <p className="svp-empty">No matching signs found.</p>;

  return (
    <div className="svp-wrapper">
      <h4 className="svp-title">Sign Language Playback</h4>
      <video
        ref={videoRef}
        src={videoUrls[currentIndex]}
        controls
        autoPlay={autoPlay}
        onEnded={handleVideoEnd}
        className="svp-video"
      />
      <p className="svp-counter">Video {currentIndex + 1} of {videoUrls.length}</p>
    </div>
  );
};

export default SignVideoPlayer;
