import React from 'react';

export const Header: React.FC = () => {
  return (
    <header className="lt-header">
      <h1>Language Translator — Live Interpreter</h1>
      <span>Press and hold the microphone to speak. Release to translate.</span>
    </header>
  );
};
