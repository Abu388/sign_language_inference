import React from 'react';

interface PTTButtonProps {
  isRecording: boolean;
  isProcessing: boolean;
  onMouseDown: () => void;
  onMouseUp: () => void;
  onTouchStart: (e: React.TouchEvent) => void;
  onTouchEnd: (e: React.TouchEvent) => void;
  disabled?: boolean;
}

export const PTTButton: React.FC<PTTButtonProps> = ({
  isRecording,
  isProcessing,
  onMouseDown,
  onMouseUp,
  onTouchStart,
  onTouchEnd,
  disabled
}) => {
  const getButtonText = () => {
    if (isRecording) return '🎤🔴';
    if (isProcessing) return '⏳';
    return '🎤';
  };

  return (
    <button
      className={`ptt-btn ${isRecording ? 'recording' : ''}`}
      onMouseDown={onMouseDown}
      onMouseUp={onMouseUp}
      onTouchStart={onTouchStart}
      onTouchEnd={onTouchEnd}
      disabled={disabled || isProcessing}
    >
      {getButtonText()}
    </button>
  );
};