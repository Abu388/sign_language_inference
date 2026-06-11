import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';

const Home: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="home-container">
      <header className="hero">
        <h1>Sign Language Communication Suite</h1>
        <p>Bridging the gap between hearing and deaf communities using AI.</p>
      </header>
      <div className="cards">
        <div className="card" onClick={() => navigate('/sign-to-recognition')}>
          <h2>✋ Sign to Recognition</h2>
          <p>Recognise sign language gestures from webcam in real time. Build sentences and translate them into text.</p>
          <button>Launch</button>
        </div>
        <div className="card" onClick={() => navigate('/language-translation')}>
          <h2>🌐 Language Translation</h2>
          <p>Translate speech to form one language to another (supported languages include Amharic, English, Afan Oromo).</p>
          <button>Launch</button>
        </div>
      </div>
    </div>
  );
};

export default Home;