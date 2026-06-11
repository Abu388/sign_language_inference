import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import './LanguageTranslation.css';
import { Header } from '../components/Header';
import { LanguageBar } from '../components/LanguageBar';
import { Panel } from '../components/Panel';
import { Message, LANG_NAMES } from '../types';
import { useAudioRecorder } from '../hooks/useAudioRecorder';
import { useTranslation } from '../hooks/useTranslation';

const LanguageTranslation: React.FC = () => {
  const navigate = useNavigate();
  const [patientLang, setPatientLang] = useState('am');
  const [doctorLang, setDoctorLang] = useState('en');

  const [patientMessages, setPatientMessages] = useState<Message[]>([]);
  const [doctorMessages, setDoctorMessages] = useState<Message[]>([]);

  const [activeRole, setActiveRole] = useState<'patient' | 'doctor' | null>(null);

  const { translateAudio } = useTranslation();

  const handleRecordingComplete = useCallback(async (role: 'patient' | 'doctor', blob: Blob) => {
    const sourceLang = role === 'patient' ? patientLang : doctorLang;
    const targetLang = role === 'patient' ? doctorLang : patientLang;

    try {
      const result = await translateAudio(blob, sourceLang, targetLang);

      const newMessages: Message[] = [
        {
          id: `${Date.now()}-original`,
          text: result.transcript,
          type: 'original',
          meta: `You said (${LANG_NAMES[sourceLang] || sourceLang})`,
          timestamp: new Date()
        }
      ];

      if (result.translated && result.translated_text) {
        newMessages.push({
          id: `${Date.now()}-translated`,
          text: result.translated_text,
          type: 'translated',
          meta: `→ ${LANG_NAMES[targetLang] || targetLang}`,
          timestamp: new Date()
        });
      }

      if (role === 'patient') {
        setPatientMessages(prev => [...prev, ...newMessages]);
      } else {
        setDoctorMessages(prev => [...prev, ...newMessages]);
      }

      if (result.audio_b64) {
        const audio = new Audio(`data:audio/mp3;base64,${result.audio_b64}`);
        audio.play().catch(err => console.warn('Audio playback blocked:', err));
      }
    } catch (error) {
      console.error('Translation failed:', error);

      const errorMessage: Message = {
        id: `${Date.now()}-error`,
        text: `Error: ${error instanceof Error ? error.message : 'Translation failed'}`,
        type: 'original',
        meta: 'Error',
        timestamp: new Date()
      };

      if (role === 'patient') {
        setPatientMessages(prev => [...prev, errorMessage]);
      } else {
        setDoctorMessages(prev => [...prev, errorMessage]);
      }
    }
  }, [patientLang, doctorLang, translateAudio]);

  const patientRecorder = useAudioRecorder({
    onRecordingComplete: (blob) => handleRecordingComplete('patient', blob)
  });

  const doctorRecorder = useAudioRecorder({
    onRecordingComplete: (blob) => handleRecordingComplete('doctor', blob)
  });

  const handleStartRecording = useCallback((role: 'patient' | 'doctor') => {
    if (activeRole) return;
    setActiveRole(role);

    if (role === 'patient') {
      patientRecorder.startRecording();
    } else {
      doctorRecorder.startRecording();
    }
  }, [activeRole, patientRecorder, doctorRecorder]);

  const handleStopRecording = useCallback(async (role: 'patient' | 'doctor') => {
    if (activeRole !== role) return;

    if (role === 'patient') {
      await patientRecorder.stopRecording();
    } else {
      await doctorRecorder.stopRecording();
    }

    setActiveRole(null);
  }, [activeRole, patientRecorder, doctorRecorder]);

  const handleSwapLanguages = useCallback(() => {
    setPatientLang(doctorLang);
    setDoctorLang(patientLang);
  }, [patientLang, doctorLang]);

  const isAnyRecording = patientRecorder.isRecording || doctorRecorder.isRecording;

  return (
    <div className="language-translation-page">
      <div className="page-topbar">
        <button
          type="button"
          className="back-button"
          onClick={() => (window.history.length > 1 ? navigate(-1) : navigate('/'))}
        >
          ← Back
        </button>
      </div>

      <div className="app">
        <Header />
        <LanguageBar
          patientLang={patientLang}
          doctorLang={doctorLang}
          onPatientLangChange={setPatientLang}
          onDoctorLangChange={setDoctorLang}
          onSwap={handleSwapLanguages}
        />

        <main>
          <Panel
            role="patient"
            language={patientLang}
            messages={patientMessages}
            isRecording={patientRecorder.isRecording}
            isProcessing={patientRecorder.isProcessing}
            onStartRecording={() => handleStartRecording('patient')}
            onStopRecording={() => handleStopRecording('patient')}
            disabled={isAnyRecording && activeRole !== 'patient'}
          />

          <Panel
            role="doctor"
            language={doctorLang}
            messages={doctorMessages}
            isRecording={doctorRecorder.isRecording}
            isProcessing={doctorRecorder.isProcessing}
            onStartRecording={() => handleStartRecording('doctor')}
            onStopRecording={() => handleStopRecording('doctor')}
            disabled={isAnyRecording && activeRole !== 'doctor'}
          />
        </main>

        <footer>
          MediBridge Healthcare Communication Platform
        </footer>
      </div>
    </div>
  );
};

export default LanguageTranslation;

