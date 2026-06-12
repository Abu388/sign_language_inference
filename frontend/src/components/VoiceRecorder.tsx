import React, { useState, useRef } from 'react';

interface VoiceRecorderProps {
  onTranscribed: (text: string) => void;
  language?: string;
  buttonText?: string;
}

const VoiceRecorder: React.FC<VoiceRecorderProps> = ({
  onTranscribed,
  language = 'en',
  buttonText = 'Start Speaking'
}) => {
  const [recording, setRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);

  const startRecording = async () => {
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setIsProcessing(true);
        try {
          const reader = new FileReader();
          reader.readAsDataURL(audioBlob);
          reader.onloadend = async () => {
            const base64 = (reader.result as string).split(',')[1];
            const response = await fetch('http://localhost:8000/api/stt-from-audio', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ audio_base64: base64, lang: language }),
            });
            if (!response.ok) {
              const err = await response.json();
              throw new Error(err.detail || 'STT failed');
            }
            const data = await response.json();
            onTranscribed(data.text);
          };
        } catch (err: any) {
          setError(err.message);
        } finally {
          setIsProcessing(false);
          stream.getTracks().forEach(track => track.stop());
        }
      };

      mediaRecorder.start();
      setRecording(true);
    } catch (err) {
      setError('Microphone access denied or error');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  return (
    <div className="vr-wrapper">
      <button
        className={`vr-btn ${recording ? 'recording' : ''}${isProcessing ? ' processing' : ''}`}
        onClick={recording ? stopRecording : startRecording}
        disabled={isProcessing}
      >
        <span className="vr-btn-icon">{recording ? '■' : '🎤'}</span>
        {isProcessing ? 'Processing...' : recording ? 'Stop Recording' : buttonText}
      </button>
      {error && <p className="vr-error">{error}</p>}
    </div>
  );
};

export default VoiceRecorder;
