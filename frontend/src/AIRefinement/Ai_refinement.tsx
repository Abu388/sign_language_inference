import React, { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import TextToSpeech from '../components/TextToSpeech';
import VoiceRecorder from '../components/VoiceRecorder';
import SignVideoPlayer from '../components/SignVideoPlayer';

const BACKEND_URL = "http://127.0.0.1:8000/ai/refine";

const Ai_refinement = () => {
  const location = useLocation();
  const sentence = location.state?.sentence;
  
  const [refinedSentence, setRefinedSentence] = useState("");
  const [loading, setLoading] = useState(false);
  const [doctorTranscribedText, setDoctorTranscribedText] = useState("");
  
  const hasRefined = useRef(false);   // Prevents double API call in StrictMode

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
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sentence: rawText }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to parse service payload.");
      }

      const data = await response.json();
      setRefinedSentence(data.refined_sentence);
    } catch (error: any) {
      console.error("Error connecting to proxy backend:", error);
      setRefinedSentence(`Error: ${error.message || "Failed to communicate with local proxy server."}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        padding: '2rem',
        maxWidth: '800px',
        margin: '0 auto',
        fontFamily: 'system-ui, sans-serif'
      }}
    >
      <h1>MediBridge</h1>

      {/* Existing AI Refinement Section */}
      <div style={{ marginBottom: '2rem', padding: '1rem', backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
        <h3>Raw Transcribed Input:</h3>
        <p style={{ fontSize: '1.2rem', marginTop: '0.5rem', color: '#666' }}>
          {sentence || "No sentence received from routing."}
        </p>
      </div>

      <div style={{ padding: '1rem', border: '2px solid #007bff', borderRadius: '8px' }}>
        <h3 style={{ color: '#007bff' }}>MediBridge Refined Output:</h3>
        {loading ? (
          <p style={{ fontStyle: 'italic', color: '#555' }}>Processing medical communication...</p>
        ) : (
          <>
            <p style={{ fontSize: '1.3rem', marginTop: '0.5rem', fontWeight: '500' }}>
              {refinedSentence}
            </p>
            {/* Auto‑play TTS when refinedSentence appears */}
            {refinedSentence && !refinedSentence.startsWith('Error') && (
              <TextToSpeech text={refinedSentence} lang="en" />
            )}
          </>
        )}
      </div>

      {/* New Doctor Speech Section */}
      <hr style={{ margin: '2rem 0' }} />
      <h2>Doctor Speech to Sign Language</h2>
      <p>Press the button, speak a medical sentence, and see the sign language videos.</p>

      <VoiceRecorder onTranscribed={setDoctorTranscribedText} language="en" buttonText="🎤 Start Speaking" />

      {doctorTranscribedText && (
        <>
          <div style={{ marginTop: '1.5rem', padding: '1rem', backgroundColor: '#e9f7ef', borderRadius: '8px' }}>
            <h3>Transcribed Text:</h3>
            <p style={{ fontSize: '1.2rem' }}>{doctorTranscribedText}</p>
            {/* <TextToSpeech text={doctorTranscribedText} lang="en" /> */}
          </div>

          <div style={{ marginTop: '1.5rem', padding: '1rem', border: '2px solid #28a745', borderRadius: '8px' }}>
            <h3 style={{ color: '#28a745' }}>Sign Language Playback</h3>
            <SignVideoPlayer text={doctorTranscribedText} autoPlay />
          </div>
        </>
      )}
    </div>
  );
};

export default Ai_refinement;