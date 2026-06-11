import React from 'react';
import { useLocation } from 'react-router-dom';

const Ai_refinement = () => {
  const location = useLocation();

  const sentence =   location.state?.sentence 
  return (
    <div
      style={{
        padding: '2rem',
      }}
    >
      <h1>AI Refinement</h1>

      <h3>Received Sentence:</h3>

      <p
        style={{
          fontSize: '1.2rem',
          marginTop: '1rem',
        }}
      >
        {sentence}
      </p>
    </div>
  );
};

export default Ai_refinement;