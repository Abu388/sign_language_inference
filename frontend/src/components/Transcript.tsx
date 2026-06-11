import React, { useRef, useEffect } from 'react';
import { Message } from '../types';
import { Bubble } from './Bubble';

interface TranscriptProps {
  messages: Message[];
  emptyHint: string;
}

export const Transcript: React.FC<TranscriptProps> = ({ messages, emptyHint }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="transcript" ref={containerRef}>
      {messages.length === 0 ? (
        <span className="empty-hint">{emptyHint}</span>
      ) : (
        messages.map((message) => (
          <Bubble key={message.id} message={message} />
        ))
      )}
    </div>
  );
};