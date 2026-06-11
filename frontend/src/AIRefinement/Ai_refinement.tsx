import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import TextToSpeech from '../components/TextToSpeech';
import VoiceRecorder from '../components/VoiceRecorder';
import SignVideoPlayer from '../components/SignVideoPlayer';
import './Ai_refinement.css';

const BACKEND_URL = "http://127.0.0.1:8000/ai/refine";

const Ai_refinement = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const sentence = location.state?.sentence;

  const [refinedSentence, setRefinedSentence] = useState("");
  const [loading, setLoading] = useState(false);
  const [doctorTranscribedText, setDoctorTranscribedText] = useState("");

  const hasRefined = useRef(false);

  useEffect(() => {
    if (sentence && !hasRefined.current) {
      hasRefined.current = true;
      refineText(sentence);
    }
  }, [sentence]);

  const refineText = async (rawText: string) => {
    setLoading(true);
    try {
      const response = await fetch(BACKEND_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sentence: rawText }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to parse service payload.");
      }
      const data = await response.json();
      setRefinedSentence(data.refined_sentence);
    } catch (error: any) {
      setRefinedSentence(`Error: ${error.message || "Failed to communicate with local proxy server."}`);
    } finally { setLoading(false); }
  };

  return (
    <div className="refine-page">
      <header className="refine-header">
        <button className="refine-back-btn" onClick={() => navigate(-1)}>← Back</button>
        <div className="refine-header-center">
          <h1 className="refine-title">MediBridge</h1>
          <p className="refine-subtitle">AI-Assisted Medical Communication</p>
        </div>
        <div className="refine-header-spacer" />
      </header>

      <main className="refine-main">
        <section className="refine-column">
          <div className="refine-col-header patient">
            <span className="refine-col-icon">👤</span>
            <h2>Patient Communication</h2>
          </div>

          {sentence ? (
            <>
              <div className="refine-card">
                <div className="refine-card-label">Raw Sign Input</div>
                <div className="refine-raw-text">{sentence}</div>
              </div>

              <div className="refine-arrow">
                <span className="refine-arrow-line" />
                <span className="refine-arrow-text">AI Refinement</span>
                <span className="refine-arrow-line" />
              </div>

              <div className={`refine-card refined ${refinedSentence && !refinedSentence.startsWith('Error') ? 'success' : ''}`}>
                <div className="refine-card-label">Medically Refined Output</div>
                {loading ? (
                  <div className="refine-loading">
                    <div className="refine-spinner" />
                    <span>Processing medical communication...</span>
                  </div>
                ) : (
                  <>
                    <div className="refine-refined-text">{refinedSentence || 'Waiting for input...'}</div>
                    {refinedSentence && !refinedSentence.startsWith('Error') && (
                      <div className="refine-tts">
                        <span className="refine-tts-label">🔊 Audio Playback</span>
                        <TextToSpeech text={refinedSentence} lang="en" />
                      </div>
                    )}
                  </>
                )}
              </div>
            </>
          ) : (
            <div className="refine-card refine-start-card">
              <div className="refine-start-icon">🤟</div>
              <h3 className="refine-start-title">No Sign Input Yet</h3>
              <p className="refine-start-desc">Start recording sign language to begin patient communication.</p>
              <button className="refine-start-btn" onClick={() => navigate('/sign-to-recognition')}>
                Start Sign Recording →
              </button>
            </div>
          )}
        </section>

        <section className="refine-column">
          <div className="refine-col-header doctor">
            <span className="refine-col-icon">👨‍⚕️</span>
            <h2>Doctor Communication</h2>
          </div>

          <div className="refine-card">
            <div className="refine-card-label">Speak to Your Patient</div>
            <VoiceRecorder onTranscribed={setDoctorTranscribedText} language="en" buttonText="🎤 Start Speaking" />
            <p className="refine-hint">Press and hold to record, release to transcribe</p>
          </div>

          {doctorTranscribedText && (
            <>
              <div className="refine-arrow">
                <span className="refine-arrow-line" />
                <span className="refine-arrow-text">Transcription</span>
                <span className="refine-arrow-line" />
              </div>

              <div className="refine-card transcription">
                <div className="refine-card-label">Transcribed Text</div>
                <div className="refine-transcribed-text">{doctorTranscribedText}</div>
              </div>

              <div className="refine-arrow">
                <span className="refine-arrow-line" />
                <span className="refine-arrow-text">Sign Playback</span>
                <span className="refine-arrow-line" />
              </div>

              <div className="refine-card sign-playback">
                <SignVideoPlayer text={doctorTranscribedText} autoPlay />
              </div>
            </>
          )}
        </section>
      </main>
    </div>
  );
};

export default Ai_refinement;
