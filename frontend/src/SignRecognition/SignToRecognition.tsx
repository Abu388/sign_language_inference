import React, { useRef, useState, useEffect, useCallback } from 'react';
import Webcam from 'react-webcam';
import { useNavigate } from 'react-router-dom';
import { predictVideo } from '../services/api';
import './SignToRecognition.css';

const SignToRecognition: React.FC = () => {
  const navigate = useNavigate();

  const webcamRef = useRef<Webcam>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const [recording, setRecording] = useState(false);
  const [sentence, setSentence] = useState('');
  const [lastPrediction, setLastPrediction] = useState('');
  const [confidence, setConfidence] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [tempMessage, setTempMessage] = useState('');
  const [tempMessageTimeout, setTempMessageTimeout] = useState<NodeJS.Timeout | null>(null);

  const wordHistory = sentence ? sentence.split(' ').filter(Boolean) : [];

  const showTempMessage = useCallback(
    (msg: string) => {
      if (tempMessageTimeout) clearTimeout(tempMessageTimeout);
      setTempMessage(msg);
      const timeout = setTimeout(() => setTempMessage(''), 2000);
      setTempMessageTimeout(timeout);
    }, [tempMessageTimeout]
  );

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
  }, []);

  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current?.state === 'recording') mediaRecorderRef.current.stop();
      stopCamera();
    };
  }, [stopCamera]);

  const startRecording = useCallback(() => {
    if (!streamRef.current) { showTempMessage('Camera not ready'); return; }
    const recorder = new MediaRecorder(streamRef.current, { mimeType: 'video/webm' });
    const chunks: BlobPart[] = [];
    recorder.ondataavailable = (event) => { if (event.data.size > 0) chunks.push(event.data); };
    recorder.onstop = async () => {
      const blob = new Blob(chunks, { type: 'video/webm' });
      setIsProcessing(true);
      try {
        const result = await predictVideo(blob, sentence);
        if (result.success && result.prediction) {
          setLastPrediction(result.prediction);
          setConfidence(result.confidence || 0);
          const updatedSentence = result.full_sentence || (sentence ? `${sentence} ${result.prediction}` : result.prediction);
          setSentence(updatedSentence);
          showTempMessage(`Recognised: ${result.prediction} (${((result.confidence || 0) * 100).toFixed(1)}%)`);
        } else {
          showTempMessage(`Error: ${result.error || 'Unknown error'}`);
        }
      } catch (error) {
        showTempMessage('Failed to communicate with server');
      } finally { setIsProcessing(false); }
    };
    recorder.start();
    mediaRecorderRef.current = recorder;
    setRecording(true);
    showTempMessage('Recording... Press SPACE to stop');
  }, [sentence, showTempMessage]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  }, []);

  const finishSession = useCallback(() => {
    const fullSentence = sentence || '(empty)';
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') mediaRecorderRef.current.stop();
    setRecording(false);
    stopCamera();
    setTimeout(() => navigate('/ai-refinement', { state: { sentence: fullSentence } }), 500);
  }, [sentence, stopCamera, navigate]);

  const goBackHome = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') mediaRecorderRef.current.stop();
    setRecording(false);
    stopCamera();
    setTimeout(() => navigate('/'), 500);
  }, [navigate, stopCamera]);

  const clearSentence = useCallback(() => {
    setSentence('');
    setLastPrediction('');
    setConfidence(0);
  }, []);

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if ((e.key === 's' || e.key === 'S') && !recording && !isProcessing) { e.preventDefault(); startRecording(); }
      if ((e.key === ' ' || e.code === 'Space') && recording) { e.preventDefault(); stopRecording(); }
      if (e.key === 'f' || e.key === 'F') { e.preventDefault(); finishSession(); }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [recording, isProcessing, startRecording, stopRecording, finishSession]);

  if (permissionDenied) {
    return (
      <div className="sign-error">
        <div className="sign-error-icon">⚠️</div>
        <h2>Camera Permission Denied</h2>
        <p>Please allow camera access in your browser settings and refresh the page.</p>
        <button className="sign-btn sign-btn-secondary" onClick={goBackHome}>← Back to Home</button>
      </div>
    );
  }

  return (
    <div className="sign-page">
      <header className="sign-header">
        <button className="sign-back-btn" onClick={goBackHome}>← Back</button>
        <h1 className="sign-title">Sign Language Recognition</h1>
        <div className="sign-header-spacer" />
      </header>

      <main className="sign-main">
        <section className="sign-camera-section">
          <div className="sign-camera-card">
            <div className="sign-camera-wrapper">
              <Webcam
                ref={webcamRef}
                audio={false}
                className="sign-webcam"
                mirrored={true}
                onUserMedia={(stream) => { streamRef.current = stream; }}
                onUserMediaError={() => setPermissionDenied(true)}
              />
              {isProcessing && (
                <div className="sign-overlay">
                  <div className="sign-spinner" />
                  <span>Processing...</span>
                </div>
              )}
              <div className={`sign-rec-indicator ${recording ? 'active' : ''}`}>
                <span className="sign-rec-dot" />
                {recording ? 'Recording' : 'Standby'}
              </div>
            </div>

            <div className="sign-controls">
              <button
                className="sign-btn sign-btn-record"
                onClick={startRecording}
                disabled={recording || isProcessing}
              >
                ● Record (S)
              </button>
              <button
                className="sign-btn sign-btn-stop"
                onClick={stopRecording}
                disabled={!recording || isProcessing}
              >
                ■ Stop (Space)
              </button>
              <button
                className="sign-btn sign-btn-finish"
                onClick={finishSession}
                disabled={isProcessing || (!sentence && !lastPrediction)}
              >
                ✓ Finish (F)
              </button>
            </div>
          </div>
        </section>

        <section className="sign-results-section">
          <div className="sign-card">
            <div className="sign-card-header">
              <h3>Word History</h3>
              <span className="sign-badge">{wordHistory.length} words</span>
            </div>
            <div className="sign-word-chips">
              {wordHistory.length > 0 ? (
                wordHistory.map((word, i) => (
                  <span key={i} className="sign-chip" style={{ animationDelay: `${i * 0.05}s` }}>
                    {word}
                  </span>
                ))
              ) : (
                <p className="sign-empty">No words yet — start recording to begin</p>
              )}
            </div>
          </div>

          <div className="sign-card">
            <div className="sign-card-header">
              <h3>Current Sentence</h3>
              {sentence && (
                <button className="sign-clear-btn" onClick={clearSentence} title="Clear sentence">✕</button>
              )}
            </div>
            <div className="sign-sentence-display">
              {sentence || <span className="sign-placeholder">—</span>}
            </div>
          </div>

          <div className="sign-card">
            <h3>Last Prediction</h3>
            <div className="sign-prediction-row">
              <span className="sign-prediction-word">{lastPrediction || '—'}</span>
              {confidence > 0 && (
                <div className="sign-confidence">
                  <div className="sign-confidence-bar">
                    <div
                      className="sign-confidence-fill"
                      style={{ width: `${(confidence * 100).toFixed(1)}%` }}
                    />
                  </div>
                  <span className="sign-confidence-text">{(confidence * 100).toFixed(1)}%</span>
                </div>
              )}
            </div>
          </div>

          <div className="sign-card sign-hints-card">
            <h3>Keyboard Shortcuts</h3>
            <div className="sign-hints">
              <span><kbd>S</kbd> Record</span>
              <span><kbd>Space</kbd> Stop</span>
              <span><kbd>F</kbd> Finish</span>
            </div>
          </div>
        </section>
      </main>

      {tempMessage && <div className="sign-toast">{tempMessage}</div>}
    </div>
  );
};

export default SignToRecognition;
