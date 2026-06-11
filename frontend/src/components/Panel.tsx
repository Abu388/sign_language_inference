import React from 'react';
import { Message, LANG_NAMES } from '../types';
import { Transcript } from './Transcript';
import { PTTButton } from './PTTButton';

interface PanelProps {
  role: 'patient' | 'doctor';
  language: string;
  messages: Message[];
  isRecording: boolean;
  isProcessing: boolean;
  onStartRecording: () => void;
  onStopRecording: () => void;
  disabled?: boolean;
}

export const Panel: React.FC<PanelProps> = ({
  role,
  language,
  messages,
  isRecording,
  isProcessing,
  onStartRecording,
  onStopRecording,
  disabled
}) => {
  const isPatient = role === 'patient';
  const panelClass = isPatient ? 'patient' : 'doctor';
  const title = isPatient ? '👤 Patient' : '👨‍⚕️ Doctor';
  const emptyHint = isPatient 
    ? 'Patient speech will appear here…' 
    : 'Doctor speech will appear here…';

  const getStatusText = () => {
    if (isRecording) return 'Recording…';
    if (isProcessing) return 'Processing…';
    return 'Ready';
  };

  const getStatusClass = () => {
    if (isRecording) return 'recording';
    if (isProcessing) return 'processing';
    return 'done';
  };

  const handleMouseDown = () => {
    if (!disabled && !isRecording && !isProcessing) {
      onStartRecording();
    }
  };

  const handleMouseUp = () => {
    if (isRecording) {
      onStopRecording();
    }
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    e.preventDefault();
    if (!disabled && !isRecording && !isProcessing) {
      onStartRecording();
    }
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    e.preventDefault();
    if (isRecording) {
      onStopRecording();
    }
  };

  return (
    <div className={`panel ${panelClass}`}>
      <div className="panel-header">
        {title}
        <span className="lang-label">{LANG_NAMES[language] || language}</span>
      </div>
      
      <Transcript messages={messages} emptyHint={emptyHint} />
      
      <div className="ptt-area">
        <div className={`status-badge ${getStatusClass()}`}>
          {getStatusText()}
        </div>
        <PTTButton
          isRecording={isRecording}
          isProcessing={isProcessing}
          onMouseDown={handleMouseDown}
          onMouseUp={handleMouseUp}
          onTouchStart={handleTouchStart}
          onTouchEnd={handleTouchEnd}
          disabled={disabled}
        />
        <div className="ptt-hint">Hold to speak · Release to translate</div>
      </div>
    </div>
  );
};