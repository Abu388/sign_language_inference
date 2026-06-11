import React, { useState, useRef, useEffect } from 'react';
import { AudioVisualizer } from './AudioVisualizer';

interface EnhancedPTTButtonProps {
  onStartRecording: () => Promise<MediaStream>;
  onStopRecording: (audioBlob: Blob) => void;
  onPlaybackComplete?: () => void;
  language: string;
}

export const EnhancedPTTButton: React.FC<EnhancedPTTButtonProps> = ({
  onStartRecording,
  onStopRecording,
  onPlaybackComplete,
  language
}) => {
  const [state, setState] = useState<'idle' | 'recording' | 'processing' | 'playback'>('idle');
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [audioElement, setAudioElement] = useState<HTMLAudioElement | null>(null);
  const [audioContext, setAudioContext] = useState<AudioContext | null>(null);
  const [sourceNode, setSourceNode] = useState<MediaStreamAudioSourceNode | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);

  const startRecording = async () => {
    try {
      const stream = await onStartRecording();
      streamRef.current = stream;
      
      // Setup audio context for visualization
      const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
      const source = audioCtx.createMediaStreamSource(stream);
      
      setAudioContext(audioCtx);
      setSourceNode(source);
      
      // Start recording
      mediaRecorderRef.current = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      audioChunksRef.current = [];
      
      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };
      
      mediaRecorderRef.current.start(100);
      setState('recording');
    } catch (err) {
      console.error('Failed to start recording:', err);
    }
  };

  const stopRecording = async () => {
    if (mediaRecorderRef.current && state === 'recording') {
      mediaRecorderRef.current.stop();
      
      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
        
        // Stop all tracks
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
        }
        
        // Close audio context
        if (audioContext) {
          audioContext.close();
        }
        
        setState('processing');
        
        // Simulate processing delay
        setTimeout(() => {
          onStopRecording(blob);
          setState('playback');
          
          // Auto-play the recorded audio
          const audio = new Audio(url);
          setAudioElement(audio);
          audio.play();
          
          audio.onended = () => {
            setState('idle');
            onPlaybackComplete?.();
          };
        }, 500);
      };
    }
  };

  const playAudio = (url: string) => {
    const audio = new Audio(url);
    setAudioElement(audio);
    setState('playback');
    audio.play();
    
    audio.onended = () => {
      setState('idle');
      onPlaybackComplete?.();
    };
  };

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (audioUrl) URL.revokeObjectURL(audioUrl);
      if (audioContext) audioContext.close();
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, [audioUrl, audioContext]);

  const getButtonContent = () => {
    switch (state) {
      case 'recording':
        return '⏹️';
      case 'processing':
        return '⏳';
      case 'playback':
        return '🔊';
      default:
        return '🎤';
    }
  };

  const getStatusText = () => {
    switch (state) {
      case 'recording':
        return 'Recording...';
      case 'processing':
        return 'Processing...';
      case 'playback':
        return 'Playing...';
      default:
        return 'Hold to speak';
    }
  };

  return (
    <div className="enhanced-ptt-container">
      <div className="visualizer-container">
        <AudioVisualizer
          isActive={state !== 'idle'}
          mode={
            state === 'recording' ? 'recording' :
            state === 'playback' ? 'playback' : 'idle'
          }
          audioContext={audioContext}
          sourceNode={sourceNode}
          audioElement={audioElement}
          barCount={40}
          height={80}
        />
      </div>
      
      <div className="ptt-controls">
        <button
          className={`enhanced-ptt-btn ${state}`}
          onMouseDown={startRecording}
          onMouseUp={stopRecording}
          onMouseLeave={() => {
            if (state === 'recording') stopRecording();
          }}
          onTouchStart={(e) => {
            e.preventDefault();
            startRecording();
          }}
          onTouchEnd={(e) => {
            e.preventDefault();
            if (state === 'recording') stopRecording();
          }}
          disabled={state === 'processing'}
        >
          {getButtonContent()}
        </button>
        
        <div className="ptt-status">
          <span className={`status-dot ${state}`}></span>
          <span>{getStatusText()}</span>
          <span className="language-badge">{language}</span>
        </div>
      </div>
      
      {audioUrl && state === 'idle' && (
        <button 
          className="replay-btn"
          onClick={() => playAudio(audioUrl)}
        >
          🔄 Replay
        </button>
      )}
    </div>
  );
};