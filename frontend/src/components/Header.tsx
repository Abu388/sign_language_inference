import React from 'react';

export const Header: React.FC = () => {
  return (
    <header>
      <span style={{ fontSize: '1.5rem' }}></span>
      <div>
        <h1>Language Translator — Live Interpreter</h1>
        <span>Press and hold the microphone to speak. Release to translate.</span>
      </div>
    </header>
  );
};