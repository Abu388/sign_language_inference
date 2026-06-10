import React, { useRef, useState, useEffect, useCallback } from 'react';
import Webcam from 'react-webcam';
import { predictVideo } from './services/api';
import './App.css';
import { PredictionResponse } from './types'; 

// No explicit import of PredictionResponse needed because it's only used as a type
// and TypeScript infers it from the API return type. But if you want to keep it:
// import type { PredictionResponse } from './types';  // not needed here

const App: React.FC = () => {
  const webcamRef = useRef<Webcam>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const [recording, setRecording] = useState(false);
  const [sentence, setSentence] = useState<string>('');
  const [lastPrediction, setLastPrediction] = useState<string>('');
  const [confidence, setConfidence] = useState<number>(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [tempMessage, setTempMessage] = useState<string>('');
  const [tempMessageTimeout, setTempMessageTimeout] = useState<NodeJS.Timeout | null>(null);

  const showTempMessage = useCallback((msg: string) => {
    if (tempMessageTimeout) clearTimeout(tempMessageTimeout);
    setTempMessage(msg);
    const timeout = setTimeout(() => setTempMessage(''), 2000);
    setTempMessageTimeout(timeout);
  }, [tempMessageTimeout]);

  const startRecording = useCallback(() => {
    if (!webcamRef.current?.stream) return;
    const stream = webcamRef.current.stream;
    mediaRecorderRef.current = new MediaRecorder(stream, { mimeType: 'video/webm' });
    const chunks: BlobPart[] = [];

    mediaRecorderRef.current.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.push(e.data);
    };

    mediaRecorderRef.current.onstop = async () => {
      const blob = new Blob(chunks, { type: 'video/webm' });
      setIsProcessing(true);
      try {
        const result = await predictVideo(blob, sentence);
        if (result.success && result.prediction) {
          setLastPrediction(result.prediction);
          setConfidence(result.confidence || 0);
          if (result.full_sentence) {
            setSentence(result.full_sentence);
          } else {
            const newSentence = sentence ? sentence + ' ' + result.prediction : result.prediction;
            setSentence(newSentence);
          }
          showTempMessage(`Recognised: ${result.prediction} (${((result.confidence || 0)*100).toFixed(1)}%)`);
        } else {
          showTempMessage(`Error: ${result.error || 'Unknown error'}`);
        }
      } catch (err) {
        console.error(err);
        showTempMessage('Failed to communicate with server');
      } finally {
        setIsProcessing(false);
      }
    };

    mediaRecorderRef.current.start();
    setRecording(true);
    showTempMessage('Recording started...');
  }, [sentence, showTempMessage]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  }, [recording]);

  const clearSentence = useCallback(() => {
    setSentence('');
    setLastPrediction('');
    setConfidence(0);
    showTempMessage('Sentence cleared');
  }, [showTempMessage]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 's' || e.key === 'S') {
        e.preventDefault();
        if (!recording && !isProcessing) startRecording();
      } else if (e.key === ' ' || e.key === 'Space') {
        e.preventDefault();
        if (recording) stopRecording();
      } else if (e.key === 'f' || e.key === 'F') {
        e.preventDefault();
        showTempMessage(`Current sentence: "${sentence || '(empty)'}"`);
        console.log('Full sentence:', sentence);
      } else if (e.key === 'c' || e.key === 'C') {
        e.preventDefault();
        clearSentence();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [recording, isProcessing, startRecording, stopRecording, sentence, clearSentence, showTempMessage]);

  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ video: true })
      .catch(() => setPermissionDenied(true));
  }, []);

  if (permissionDenied) {
    return <div className="error">Camera permission denied. Please allow access and refresh.</div>;
  }

  return (
    <div className="app">
      <header>
        <h1>Sign Language Recognition</h1>
      </header>
      <main>
        <div className="camera-container">
          <Webcam
            audio={false}
            ref={webcamRef}
            screenshotFormat="image/jpeg"
            videoConstraints={{ facingMode: 'user' }}
            className="webcam"
          />
          {isProcessing && <div className="processing-overlay">Processing...</div>}
          {tempMessage && <div className="temp-message">{tempMessage}</div>}
        </div>
        <div className="controls">
          <button onClick={startRecording} disabled={recording || isProcessing}>
            Start (S)
          </button>
          <button onClick={stopRecording} disabled={!recording || isProcessing}>
            Stop (Space)
          </button>
          <button onClick={clearSentence} disabled={isProcessing}>
            Clear (C)
          </button>
        </div>
        <div className="result">
          <div className="last-sign">
            Last sign: <strong>{lastPrediction || '—'}</strong>
            {confidence > 0 && <span> ({(confidence * 100).toFixed(1)}%)</span>}
          </div>
          <div className="sentence">
            Sentence: {sentence || '—'}
          </div>
          <div className="hint">
            Press <kbd>S</kbd> to start recording, <kbd>Space</kbd> to stop, <kbd>F</kbd> to show full sentence, <kbd>C</kbd> to clear.
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;