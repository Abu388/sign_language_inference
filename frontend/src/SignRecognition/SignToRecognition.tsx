import React, { useRef, useState, useEffect, useCallback } from 'react';
import Webcam from 'react-webcam';
import { useNavigate } from 'react-router-dom';
import { predictVideo } from '../services/api';
import './SignToRecognition.css';

const SignToRecognition: React.FC = () => {
  const navigate = useNavigate();

  const webcamRef = useRef<Webcam>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  // NEW: store the actual webcam stream
  const streamRef = useRef<MediaStream | null>(null);

  const [recording, setRecording] = useState(false);
  const [sentence, setSentence] = useState('');
  const [lastPrediction, setLastPrediction] = useState('');
  const [confidence, setConfidence] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [tempMessage, setTempMessage] = useState('');
  const [tempMessageTimeout, setTempMessageTimeout] =
    useState<NodeJS.Timeout | null>(null);

  const showTempMessage = useCallback(
    (msg: string) => {
      if (tempMessageTimeout) {
        clearTimeout(tempMessageTimeout);
      }

      setTempMessage(msg);

      const timeout = setTimeout(() => {
        setTempMessage('');
      }, 2000);

      setTempMessageTimeout(timeout);
    },
    [tempMessageTimeout]
  );

  // ==========================
  // CAMERA STOP FUNCTION
  // ==========================
  const stopCamera = useCallback(() => {
    console.log('Stopping camera...');

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => {
        console.log(`Stopping ${track.kind} track`);
        track.stop();
      });

      streamRef.current = null;
    }
  }, []);

  // ==========================
  // CLEANUP ON UNMOUNT
  // ==========================
  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current?.state === 'recording') {
        mediaRecorderRef.current.stop();
      }

      stopCamera();
    };
  }, [stopCamera]);

  const startRecording = useCallback(() => {
    if (!streamRef.current) {
      showTempMessage('Camera not ready');
      return;
    }

    const recorder = new MediaRecorder(streamRef.current, {
      mimeType: 'video/webm',
    });

    const chunks: BlobPart[] = [];

    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunks.push(event.data);
      }
    };

    recorder.onstop = async () => {
      const blob = new Blob(chunks, {
        type: 'video/webm',
      });

      setIsProcessing(true);

      try {
        const result = await predictVideo(blob, sentence);

        if (result.success && result.prediction) {
          setLastPrediction(result.prediction);
          setConfidence(result.confidence || 0);

          const updatedSentence =
            result.full_sentence ||
            (sentence
              ? `${sentence} ${result.prediction}`
              : result.prediction);

          setSentence(updatedSentence);

          showTempMessage(
            `Recognised: ${result.prediction} (${(
              (result.confidence || 0) * 100
            ).toFixed(1)}%)`
          );
        } else {
          showTempMessage(
            `Error: ${result.error || 'Unknown error'}`
          );
        }
      } catch (error) {
        console.error(error);
        showTempMessage('Failed to communicate with server');
      } finally {
        setIsProcessing(false);
      }
    };

    recorder.start();

    mediaRecorderRef.current = recorder;
    setRecording(true);

    showTempMessage(
      'Recording... Press SPACE to stop'
    );
  }, [sentence, showTempMessage]);

  const stopRecording = useCallback(() => {
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state === 'recording'
    ) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  }, []);

  const finishSession = useCallback(() => {
  const fullSentence = sentence || '(empty)';

  console.log('Final sentence:', fullSentence);

  if (
    mediaRecorderRef.current &&
    mediaRecorderRef.current.state === 'recording'
  ) {
    mediaRecorderRef.current.stop();
  }

  setRecording(false);

  stopCamera();

  setTimeout(() => {
    navigate('/ai-refinement', {
      state: {
        sentence: fullSentence,
      },
    });
  }, 500);
}, [sentence, stopCamera, navigate]);

  const goBackHome = useCallback(() => {
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state === 'recording'
    ) {
      mediaRecorderRef.current.stop();
    }

    setRecording(false);

    stopCamera();

    setTimeout(() => {
      navigate('/');
    }, 500);
  }, [navigate, stopCamera]);

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if ((e.key === 's' || e.key === 'S') && !recording && !isProcessing) {
        e.preventDefault();
        startRecording();
      }

      if ((e.key === ' ' || e.code === 'Space') && recording) {
        e.preventDefault();
        stopRecording();
      }

      if (e.key === 'f' || e.key === 'F') {
        e.preventDefault();
        finishSession();
      }
    };

    window.addEventListener('keydown', handleKey);

    return () => {
      window.removeEventListener('keydown', handleKey);
    };
  }, [
    recording,
    isProcessing,
    startRecording,
    stopRecording,
    finishSession,
  ]);

  if (permissionDenied) {
    return (
      <div className="error">
        Camera permission denied. Please allow camera access and refresh.
      </div>
    );
  }

  return (
    <div className="sign-container">
      <button
        className="back-button"
        onClick={goBackHome}
      >
        ← Back to Home
      </button>

      <h1>Sign Language Recognition</h1>

      <div className="camera-container">
        <Webcam
          ref={webcamRef}
          audio={false}
          className="webcam"
          mirrored={true}
          onUserMedia={(stream) => {
            console.log('Camera started');
            streamRef.current = stream;
          }}
          onUserMediaError={() => {
            setPermissionDenied(true);
          }}
        />

        {isProcessing && (
          <div className="overlay">
            Processing...
          </div>
        )}

        {tempMessage && (
          <div className="temp-message">
            {tempMessage}
          </div>
        )}
      </div>

      <div className="controls">
        <button
          onClick={startRecording}
          disabled={recording || isProcessing}
        >
          Start (S)
        </button>

        <button
          onClick={stopRecording}
          disabled={!recording || isProcessing}
        >
          Stop (SPACE)
        </button>

        <button
          onClick={finishSession}
          disabled={isProcessing}
        >
          Finish (F)
        </button>
      </div>

      <div className="result">
        <div>
          Last sign:{' '}
          <strong>
            {lastPrediction || '—'}
          </strong>
          {confidence > 0 &&
            ` (${(confidence * 100).toFixed(1)}%)`}
        </div>

        <div className="sentence">
          Sentence: {sentence || '—'}
        </div>

        <div className="hint">
          Press S to record, SPACE to stop, F to finish
        </div>
      </div>
    </div>
  );
};

export default SignToRecognition;
