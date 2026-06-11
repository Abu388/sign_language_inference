import React, { useEffect, useRef, useState } from 'react';

interface AudioVisualizerProps {
  isActive: boolean;
  mode: 'recording' | 'playback' | 'idle';
  audioContext?: AudioContext | null;
  sourceNode?: MediaStreamAudioSourceNode | null;
  audioElement?: HTMLAudioElement | null;
  barCount?: number;
  barColor?: string;
  activeColor?: string;
  height?: number;
}

export const AudioVisualizer: React.FC<AudioVisualizerProps> = ({
  isActive,
  mode,
  audioContext: externalAudioContext,
  sourceNode: externalSourceNode,
  audioElement,
  barCount = 30,
  barColor = '#4a90e2',
  activeColor = '#ff6b6b',
  height = 60
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const audioContextRef = useRef<AudioContext | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const [audioData, setAudioData] = useState<Uint8Array>(new Uint8Array(barCount));

  // Initialize audio context for recording visualization
  const initRecordingVisualizer = async (stream: MediaStream) => {
    if (!canvasRef.current) return;

    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 256;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const source = audioContext.createMediaStreamSource(stream);
    source.connect(analyser);
    
    // Don't connect to destination to avoid feedback
    audioContextRef.current = audioContext;
    analyserRef.current = analyser;
    sourceRef.current = source;

    // Resume audio context (required for Chrome)
    if (audioContext.state === 'suspended') {
      await audioContext.resume();
    }

    return { analyser, dataArray, bufferLength };
  };

  // Initialize visualizer for playback
  const initPlaybackVisualizer = (audioEl: HTMLAudioElement) => {
    if (!canvasRef.current) return;

    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 256;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const source = audioContext.createMediaElementSource(audioEl);
    source.connect(analyser);
    analyser.connect(audioContext.destination);

    audioContextRef.current = audioContext;
    analyserRef.current = analyser;
    sourceRef.current = source;

    return { analyser, dataArray, bufferLength };
  };

  // Draw waveform visualization
  const drawWaveform = () => {
    if (!canvasRef.current || !analyserRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    const analyser = analyserRef.current;

    // Get frequency data
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(dataArray);

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Calculate bar width
    const barWidth = width / barCount;
    
    // Draw bars
    for (let i = 0; i < barCount; i++) {
      // Get value (0-255) and normalize to canvas height
      const value = dataArray[i] || 0;
      const percent = value / 255;
      const barHeight = percent * height;
      
      // Calculate gradient color based on amplitude
      let color;
      if (mode === 'recording') {
        // Red gradient for recording
        const redIntensity = 100 + Math.floor(155 * percent);
        color = `rgb(255, ${Math.floor(100 - 50 * percent)}, ${Math.floor(100 - 50 * percent)})`;
      } else if (mode === 'playback') {
        // Green gradient for playback
        const greenIntensity = 100 + Math.floor(155 * percent);
        color = `rgb(${Math.floor(100 - 50 * percent)}, ${greenIntensity}, ${Math.floor(100 - 50 * percent)})`;
      } else {
        // Blue gradient for idle
        const blueIntensity = 100 + Math.floor(155 * percent);
        color = `rgb(${Math.floor(100 - 50 * percent)}, ${Math.floor(100 - 50 * percent)}, ${blueIntensity})`;
      }
      
      // Draw bar with rounded corners
      const x = i * barWidth;
      const y = height - barHeight;
      
      ctx.fillStyle = color;
      ctx.fillRect(x, y, barWidth - 1, barHeight);
      
      // Add glow effect for active bars
      if (percent > 0.5) {
        ctx.shadowBlur = 8;
        ctx.shadowColor = color;
        ctx.fillRect(x, y, barWidth - 1, barHeight);
        ctx.shadowBlur = 0;
      }
    }

    // Continue animation if active
    if (isActive) {
      animationRef.current = requestAnimationFrame(drawWaveform);
    }
  };

  // Draw circular waveform (alternative style)
  const drawCircularWaveform = () => {
    if (!canvasRef.current || !analyserRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 2 - 10;
    
    const analyser = analyserRef.current;
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(dataArray);

    ctx.clearRect(0, 0, width, height);
    
    // Draw circular bars
    const barCountCircular = 36;
    const angleStep = (Math.PI * 2) / barCountCircular;
    
    for (let i = 0; i < barCountCircular; i++) {
      const value = dataArray[i % dataArray.length] || 0;
      const percent = value / 255;
      const barLength = 15 + (percent * 40);
      
      const angle = i * angleStep;
      const x = centerX + Math.cos(angle) * radius;
      const y = centerY + Math.sin(angle) * radius;
      const x2 = centerX + Math.cos(angle) * (radius + barLength);
      const y2 = centerY + Math.sin(angle) * (radius + barLength);
      
      let color;
      if (mode === 'recording') {
        color = `rgba(255, ${Math.floor(80 + 100 * percent)}, ${Math.floor(80 + 100 * percent)}, ${0.5 + percent * 0.5})`;
      } else if (mode === 'playback') {
        color = `rgba(${Math.floor(80 + 100 * percent)}, 255, ${Math.floor(80 + 100 * percent)}, ${0.5 + percent * 0.5})`;
      } else {
        color = `rgba(${Math.floor(80 + 100 * percent)}, ${Math.floor(80 + 100 * percent)}, 255, ${0.5 + percent * 0.5})`;
      }
      
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(x2, y2);
      ctx.lineWidth = 4;
      ctx.strokeStyle = color;
      ctx.stroke();
    }

    if (isActive) {
      animationRef.current = requestAnimationFrame(drawCircularWaveform);
    }
  };

  // Draw equalizer style
  const drawEqualizer = () => {
    if (!canvasRef.current || !analyserRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    const analyser = analyserRef.current;
    
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(dataArray);
    
    ctx.clearRect(0, 0, width, height);
    
    // Create gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    if (mode === 'recording') {
      gradient.addColorStop(0, '#ff6b6b');
      gradient.addColorStop(1, '#ffa5a5');
    } else if (mode === 'playback') {
      gradient.addColorStop(0, '#51cf66');
      gradient.addColorStop(1, '#a5e6b6');
    } else {
      gradient.addColorStop(0, '#339af0');
      gradient.addColorStop(1, '#74c0fc');
    }
    
    const barWidth = width / barCount;
    
    for (let i = 0; i < barCount; i++) {
      const value = dataArray[i] || 0;
      const percent = Math.pow(value / 255, 1.5); // Exponential curve for smoother animation
      const barHeight = percent * height;
      const x = i * barWidth;
      const y = height - barHeight;
      
      ctx.fillStyle = gradient;
      ctx.fillRect(x, y, barWidth - 1, barHeight);
      
      // Add shine effect
      ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
      ctx.fillRect(x, y, barWidth - 1, Math.min(5, barHeight));
    }
    
    if (isActive) {
      animationRef.current = requestAnimationFrame(drawEqualizer);
    }
  };

  // Setup visualizer based on mode
  useEffect(() => {
    if (!isActive) {
      // Clean up when inactive
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
      return;
    }

    const setupVisualizer = async () => {
      if (mode === 'recording' && externalAudioContext && externalSourceNode) {
        // Use provided audio context for recording
        const analyser = externalAudioContext.createAnalyser();
        analyser.fftSize = 256;
        externalSourceNode.connect(analyser);
        analyserRef.current = analyser;
        audioContextRef.current = externalAudioContext;
        
        drawEqualizer(); // Start animation
      } else if (mode === 'playback' && audioElement) {
        // Setup for playback visualization
        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        
        const source = audioContext.createMediaElementSource(audioElement);
        source.connect(analyser);
        analyser.connect(audioContext.destination);
        
        analyserRef.current = analyser;
        audioContextRef.current = audioContext;
        
        if (audioContext.state === 'suspended') {
          await audioContext.resume();
        }
        
        drawEqualizer();
      } else if (mode === 'idle' && isActive) {
        // Animate even when idle (fake animation)
        animateIdle();
      }
    };

    setupVisualizer();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isActive, mode, externalAudioContext, externalSourceNode, audioElement]);

  // Animate idle state (fake visualization)
  const animateIdle = () => {
    if (!canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    const width = canvas.width;
    const height = canvas.height;
    const time = Date.now() / 1000;
    
    ctx.clearRect(0, 0, width, height);
    
    const barWidth = width / barCount;
    
    for (let i = 0; i < barCount; i++) {
      // Create sine wave pattern
      const sineValue = Math.sin(time * 3 + i * 0.3);
      const percent = (sineValue + 1) / 4; // Range 0-0.5
      const barHeight = percent * height;
      const x = i * barWidth;
      const y = height - barHeight;
      
      ctx.fillStyle = `rgba(100, 100, 255, ${0.3 + percent * 0.3})`;
      ctx.fillRect(x, y, barWidth - 1, barHeight);
    }
    
    if (isActive && mode === 'idle') {
      animationRef.current = requestAnimationFrame(animateIdle);
    }
  };

  // Get canvas dimensions
  useEffect(() => {
    const updateCanvasSize = () => {
      if (canvasRef.current) {
        const container = canvasRef.current.parentElement;
        if (container) {
          canvasRef.current.width = container.clientWidth;
          canvasRef.current.height = height;
        }
      }
    };

    updateCanvasSize();
    window.addEventListener('resize', updateCanvasSize);
    
    return () => window.removeEventListener('resize', updateCanvasSize);
  }, [height]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        width: '100%',
        height: `${height}px`,
        borderRadius: '8px',
        backgroundColor: 'rgba(0, 0, 0, 0.05)',
        display: 'block'
      }}
    />
  );
};