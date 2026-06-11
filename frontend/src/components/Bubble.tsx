import React from 'react';
import { Message } from '../types';

interface BubbleProps {
  message: Message;
}

export const Bubble: React.FC<BubbleProps> = ({ message }) => {
  return (
    <div className={`bubble ${message.type}`}>
      <span className="meta">{message.meta}</span>
      <span>{message.text}</span>
    </div>
  );
};