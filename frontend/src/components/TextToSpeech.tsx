import React, { useEffect, useRef } from 'react';

// Global Set to track sentences already played (persists across remounts)
const playedSentences = new Set<string>();

interface TextToSpeechProps {
  text: string;
  lang?: string;      // 'en', 'am', 'om' – default 'en'
}

const TextToSpeech: React.FC<TextToSpeechProps> = ({ text, lang = 'en' }) => {
  const isPlayingRef = useRef(false);
  const currentAudioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    const playAudio = async () => {
      // Skip if no text, already played, or currently playing
      if (!text.trim() || playedSentences.has(text) || isPlayingRef.current) return;

      isPlayingRef.current = true;

      try {
        const response = await fetch('http://localhost:8000/api/tts', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text, lang, speaking_rate: 0.9 }),
        });

        if (!response.ok) {
          console.error('TTS error:', await response.json());
          isPlayingRef.current = false;
          return;
        }

        const data = await response.json();
        const audioBase64 = data.audio_base64;
        const audioBlob = base64ToBlob(audioBase64, 'audio/mpeg');
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        currentAudioRef.current = audio;

        audio.onended = () => {
          URL.revokeObjectURL(audioUrl);
          isPlayingRef.current = false;
          currentAudioRef.current = null;
          playedSentences.add(text); // Mark as played only after successful end
        };
        audio.onerror = () => {
          URL.revokeObjectURL(audioUrl);
          isPlayingRef.current = false;
          currentAudioRef.current = null;
          console.error('Audio playback failed');
        };
        await audio.play();
      } catch (err) {
        console.error('Auto-play TTS failed:', err);
        isPlayingRef.current = false;
      }
    };

    playAudio();

    // Cleanup on unmount or text change
    return () => {
      if (currentAudioRef.current) {
        currentAudioRef.current.pause();
        currentAudioRef.current = null;
      }
    };
  }, [text, lang]);

  const base64ToBlob = (base64: string, mimeType: string) => {
    const byteCharacters = atob(base64);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: mimeType });
  };

  return null;
};

export default TextToSpeech;